//go:build windows

package main

import (
	"fmt"
	"syscall"
	"unsafe"
)

var (
	iphlpapi                = syscall.NewLazyDLL("iphlpapi.dll")
	procGetExtendedTcpTable = iphlpapi.NewProc("GetExtendedTcpTable")
)

const (
	afInet                   = 2 // AF_INET (IPv4)
	tcpTableOwnerPidListener = 3 // TCP_TABLE_OWNER_PID_LISTENER
)

// pidListeningOnPort returns the PID of the IPv4 process listening on TCP
// `port` on the local host. It queries GetExtendedTcpTable and delegates the
// table parsing to the platform-neutral, offline-tested pidForListeningPort.
func pidListeningOnPort(port uint16) (uint32, bool) {
	var size uint32
	// First call sizes the buffer; it is expected to fail with
	// ERROR_INSUFFICIENT_BUFFER while writing the required size.
	procGetExtendedTcpTable.Call(0, uintptr(unsafe.Pointer(&size)), 0, afInet, tcpTableOwnerPidListener, 0)
	if size == 0 {
		return 0, false
	}
	buf := make([]byte, size)
	ret, _, _ := procGetExtendedTcpTable.Call(
		uintptr(unsafe.Pointer(&buf[0])), uintptr(unsafe.Pointer(&size)),
		0, afInet, tcpTableOwnerPidListener, 0)
	if ret != 0 {
		return 0, false
	}
	if int(size) < len(buf) {
		buf = buf[:size]
	}
	return pidForListeningPort(buf, port)
}

// find1CWindowForPID returns only the process's 1C top-level window (window
// class prefixed "V8TopLevelFrame…", the TestClient main SDI frame). It never
// falls back to another process-owned window: lifecycle targeting must fail
// closed until the exact TestClient frame exists.
func find1CWindowForPID(pid uint32) (uintptr, WindowInfo, bool) {
	for _, info := range enumerateWindows() {
		if !isTestClientTopLevelWindow(info, pid) {
			continue
		}
		var hwnd uintptr
		fmt.Sscanf(info.HWND, "0x%X", &hwnd)
		return hwnd, info, true
	}
	return 0, WindowInfo{}, false
}
