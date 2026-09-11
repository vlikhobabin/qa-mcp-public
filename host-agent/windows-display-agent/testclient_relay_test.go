package main

import (
	"bufio"
	"bytes"
	"io"
	"net"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func startRelayEchoTarget(t *testing.T) (string, *atomic.Int32) {
	t.Helper()
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = listener.Close() })
	accepted := &atomic.Int32{}
	go func() {
		for {
			conn, err := listener.Accept()
			if err != nil {
				return
			}
			accepted.Add(1)
			go func() {
				defer conn.Close()
				_, _ = io.Copy(conn, conn)
			}()
		}
	}()
	return listener.Addr().String(), accepted
}

func startTestRelay(t *testing.T, target string) *TestClientRelay {
	t.Helper()
	relay, err := NewTestClientRelay(TestClientRelayConfig{
		Listen: "127.0.0.1:0", Token: "relay-secret", Target: target,
	})
	if err != nil {
		t.Fatal(err)
	}
	if err := relay.Start(); err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = relay.Close() })
	return relay
}

func readRelayReply(t *testing.T, conn net.Conn) string {
	t.Helper()
	_ = conn.SetReadDeadline(time.Now().Add(2 * time.Second))
	line, err := bufio.NewReader(conn).ReadString('\n')
	if err != nil {
		t.Fatalf("read relay reply: %v", err)
	}
	return line
}

func TestTestClientRelayAuthenticatesBeforeFixedTargetAndCopiesBinary(t *testing.T) {
	target, accepted := startRelayEchoTarget(t)
	relay := startTestRelay(t, target)

	bad, err := net.Dial("tcp", relay.Addr())
	if err != nil {
		t.Fatal(err)
	}
	_, _ = io.WriteString(bad, testClientRelayPreface+" wrong\n")
	if reply := readRelayReply(t, bad); reply != "ERR auth\n" {
		t.Fatalf("bad-token reply = %q", reply)
	}
	_ = bad.Close()
	if accepted.Load() != 0 {
		t.Fatalf("unauthorized connection opened target %d times", accepted.Load())
	}

	conn, err := net.Dial("tcp", relay.Addr())
	if err != nil {
		t.Fatal(err)
	}
	defer conn.Close()
	_, _ = io.WriteString(conn, testClientRelayPreface+" relay-secret\n")
	if reply := readRelayReply(t, conn); reply != "OK\n" {
		t.Fatalf("authorized reply = %q", reply)
	}
	payload := []byte{0x00, 0xff, 0x53, 0xf5, 0xc6, 0x1a, 0x7b}
	if _, err := conn.Write(payload); err != nil {
		t.Fatal(err)
	}
	got := make([]byte, len(payload))
	if _, err := io.ReadFull(conn, got); err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(got, payload) {
		t.Fatalf("binary relay = %x, want %x", got, payload)
	}
	if accepted.Load() != 1 {
		t.Fatalf("authorized target accepts = %d", accepted.Load())
	}
}

func TestTestClientRelayRejectsOversizedPrefaceAndConcurrentSession(t *testing.T) {
	target, accepted := startRelayEchoTarget(t)
	relay := startTestRelay(t, target)

	oversized, _ := net.Dial("tcp", relay.Addr())
	_, _ = io.WriteString(oversized, strings.Repeat("x", testClientRelayMaxPreface+1))
	if reply := readRelayReply(t, oversized); reply != "ERR preface\n" {
		t.Fatalf("oversized reply = %q", reply)
	}
	_ = oversized.Close()
	if accepted.Load() != 0 {
		t.Fatalf("oversized preface opened target")
	}

	first, _ := net.Dial("tcp", relay.Addr())
	defer first.Close()
	_, _ = io.WriteString(first, testClientRelayPreface+" relay-secret\n")
	if reply := readRelayReply(t, first); reply != "OK\n" {
		t.Fatalf("first reply = %q", reply)
	}
	second, _ := net.Dial("tcp", relay.Addr())
	defer second.Close()
	_, _ = io.WriteString(second, testClientRelayPreface+" relay-secret\n")
	if reply := readRelayReply(t, second); reply != "ERR busy\n" {
		t.Fatalf("second reply = %q", reply)
	}
	if accepted.Load() != 1 {
		t.Fatalf("busy connection opened second target: %d", accepted.Load())
	}
	status := relay.Status()
	if status["configured"] != true || status["active_sessions"] != 1 {
		t.Fatalf("relay status = %#v", status)
	}
}

func TestTestClientRelayDisabledHasNoListener(t *testing.T) {
	relay, err := NewTestClientRelay(TestClientRelayConfig{})
	if err != nil {
		t.Fatal(err)
	}
	if err := relay.Start(); err != nil {
		t.Fatal(err)
	}
	if relay.Addr() != "" || relay.Status()["configured"] != false {
		t.Fatalf("disabled relay = addr:%q status:%#v", relay.Addr(), relay.Status())
	}
}
