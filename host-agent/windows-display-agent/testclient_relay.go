package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"net"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

const (
	testClientRelayPreface    = "QA-MCP-TESTCLIENT-RELAY/1"
	testClientRelayMaxPreface = 1024
	testClientRelayAuthWait   = 5 * time.Second
)

type TestClientRelayConfig struct {
	Listen string
	Token  string
	Target string
}

type TestClientRelay struct {
	config   TestClientRelayConfig
	listener net.Listener
	slot     chan struct{}
	active   atomic.Int32
	mu       sync.RWMutex
	closed   bool
}

func NewTestClientRelay(config TestClientRelayConfig) (*TestClientRelay, error) {
	config.Listen = strings.TrimSpace(config.Listen)
	config.Token = normalizeToken(config.Token)
	config.Target = strings.TrimSpace(config.Target)
	if config.Listen == "" {
		return &TestClientRelay{config: config, slot: make(chan struct{}, 1)}, nil
	}
	if config.Token == "" {
		return nil, fmt.Errorf("TestClient relay token is required when relay listen address is configured")
	}
	host, port, err := net.SplitHostPort(config.Target)
	if err != nil || port == "" {
		return nil, fmt.Errorf("TestClient relay target must be a loopback host:port")
	}
	ip := net.ParseIP(host)
	if ip == nil || !ip.IsLoopback() {
		return nil, fmt.Errorf("TestClient relay target must be loopback")
	}
	return &TestClientRelay{config: config, slot: make(chan struct{}, 1)}, nil
}

func (r *TestClientRelay) Start() error {
	if r.config.Listen == "" {
		return nil
	}
	listener, err := net.Listen("tcp", r.config.Listen)
	if err != nil {
		return err
	}
	r.mu.Lock()
	r.listener = listener
	r.mu.Unlock()
	go r.acceptLoop(listener)
	return nil
}

func (r *TestClientRelay) Addr() string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	if r.listener == nil {
		return ""
	}
	return r.listener.Addr().String()
}

func (r *TestClientRelay) Close() error {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.closed = true
	if r.listener == nil {
		return nil
	}
	err := r.listener.Close()
	r.listener = nil
	return err
}

func (r *TestClientRelay) Status() map[string]any {
	if r == nil || r.config.Listen == "" {
		return map[string]any{"configured": false, "state": "disabled", "active_sessions": 0}
	}
	state := "ready"
	if r.Addr() == "" {
		state = "not_listening"
	}
	return map[string]any{
		"configured":      true,
		"state":           state,
		"listen":          r.Addr(),
		"target":          r.config.Target,
		"active_sessions": int(r.active.Load()),
		"max_sessions":    1,
	}
}

func (r *TestClientRelay) acceptLoop(listener net.Listener) {
	for {
		connection, err := listener.Accept()
		if err != nil {
			r.mu.RLock()
			closed := r.closed
			r.mu.RUnlock()
			if closed || errors.Is(err, net.ErrClosed) {
				return
			}
			continue
		}
		go r.handle(connection)
	}
}

func (r *TestClientRelay) handle(client net.Conn) {
	defer client.Close()
	_ = client.SetDeadline(time.Now().Add(testClientRelayAuthWait))
	reader := bufio.NewReaderSize(client, testClientRelayMaxPreface+1)
	line, err := reader.ReadSlice('\n')
	if err != nil || len(line) > testClientRelayMaxPreface {
		_, _ = io.WriteString(client, "ERR preface\n")
		return
	}
	prefix, token, ok := strings.Cut(strings.TrimSpace(string(line)), " ")
	if !ok || prefix != testClientRelayPreface || !tokenMatches(token, r.config.Token) {
		_, _ = io.WriteString(client, "ERR auth\n")
		return
	}
	select {
	case r.slot <- struct{}{}:
		defer func() { <-r.slot }()
	default:
		_, _ = io.WriteString(client, "ERR busy\n")
		return
	}
	target, err := net.DialTimeout("tcp", r.config.Target, 3*time.Second)
	if err != nil {
		_, _ = io.WriteString(client, "ERR target\n")
		return
	}
	defer target.Close()
	r.active.Add(1)
	defer r.active.Add(-1)
	_ = client.SetDeadline(time.Time{})
	if _, err := io.WriteString(client, "OK\n"); err != nil {
		return
	}
	done := make(chan struct{}, 2)
	go func() {
		_, _ = io.Copy(target, reader)
		if tcp, ok := target.(*net.TCPConn); ok {
			_ = tcp.CloseWrite()
		}
		done <- struct{}{}
	}()
	go func() {
		_, _ = io.Copy(client, target)
		if tcp, ok := client.(*net.TCPConn); ok {
			_ = tcp.CloseWrite()
		}
		done <- struct{}{}
	}()
	<-done
}
