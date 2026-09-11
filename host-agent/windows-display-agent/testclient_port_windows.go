//go:build windows

package main

import (
	"syscall"
	"time"
	"unsafe"
)

const (
	windowsAFInet                   = 2
	windowsTCPTableOwnerPIDListener = 3
	windowsErrorInsufficientBuffer  = 122
)

var procGetExtendedTCPTable = syscall.NewLazyDLL("iphlpapi.dll").NewProc("GetExtendedTcpTable")

func testClientPortListening(port int, timeout time.Duration) bool {
	_ = timeout
	if !validTCPPort(port) {
		return false
	}
	var size uint32
	status, _, _ := procGetExtendedTCPTable.Call(
		0,
		uintptr(unsafe.Pointer(&size)),
		0,
		windowsAFInet,
		windowsTCPTableOwnerPIDListener,
		0,
	)
	if uint32(status) != windowsErrorInsufficientBuffer || size < 4 {
		return false
	}
	table := make([]byte, size)
	status, _, _ = procGetExtendedTCPTable.Call(
		uintptr(unsafe.Pointer(&table[0])),
		uintptr(unsafe.Pointer(&size)),
		0,
		windowsAFInet,
		windowsTCPTableOwnerPIDListener,
		0,
	)
	if status != 0 {
		return false
	}
	return windowsTCPTableHasListener(table[:size], port)
}
