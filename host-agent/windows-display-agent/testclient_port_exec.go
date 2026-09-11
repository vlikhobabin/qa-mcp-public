//go:build !windows

package main

import (
	"net"
	"strconv"
	"time"
)

func testClientPortListening(port int, timeout time.Duration) bool {
	if !validTCPPort(port) {
		return false
	}
	conn, err := net.DialTimeout("tcp", net.JoinHostPort("127.0.0.1", strconv.Itoa(port)), timeout)
	if err != nil {
		return false
	}
	_ = conn.Close()
	return true
}
