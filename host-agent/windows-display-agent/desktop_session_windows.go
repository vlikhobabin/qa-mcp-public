//go:build windows

package main

import (
	"strings"
	"unsafe"

	"golang.org/x/sys/windows"
)

const (
	wtsConnectState      = 8
	wtsActive            = 0
	wtsDisconnected      = 4
	uoiName              = 2
	desktopSwitchDesktop = 0x0100
	invalidSessionID     = 0xFFFFFFFF
)

var (
	wtsapi32                         = windows.NewLazySystemDLL("wtsapi32.dll")
	procWTSQuerySessionInformation   = wtsapi32.NewProc("WTSQuerySessionInformationW")
	procWTSFreeMemory                = wtsapi32.NewProc("WTSFreeMemory")
	procWTSGetActiveConsoleSessionID = kernel32.NewProc("WTSGetActiveConsoleSessionId")
	procOpenInputDesktop             = user32.NewProc("OpenInputDesktop")
	procCloseDesktop                 = user32.NewProc("CloseDesktop")
	procGetUserObjectInformation     = user32.NewProc("GetUserObjectInformationW")
)

func probeDesktopSession() desktopSessionState {
	sessionID, _, _ := procWTSGetActiveConsoleSessionID.Call()
	if uint32(sessionID) == invalidSessionID {
		return desktopSessionNonInteractive
	}
	if state, ok := queryWTSConnectState(uint32(sessionID)); ok {
		if state == wtsDisconnected {
			return desktopSessionDisconnected
		}
		if state != wtsActive {
			return desktopSessionNonInteractive
		}
	}

	desktop, _, _ := procOpenInputDesktop.Call(0, 0, desktopSwitchDesktop)
	if desktop == 0 {
		return desktopSessionNonInteractive
	}
	defer procCloseDesktop.Call(desktop)
	name, ok := desktopObjectName(desktop)
	if !ok {
		return desktopSessionNonInteractive
	}
	if !strings.EqualFold(name, "Default") {
		return desktopSessionLocked
	}
	return desktopSessionActive
}

func queryWTSConnectState(sessionID uint32) (uint32, bool) {
	var buffer uintptr
	var bytesReturned uint32
	ok, _, _ := procWTSQuerySessionInformation.Call(
		0,
		uintptr(sessionID),
		wtsConnectState,
		uintptr(unsafe.Pointer(&buffer)),
		uintptr(unsafe.Pointer(&bytesReturned)),
	)
	if ok == 0 || buffer == 0 || bytesReturned < 4 {
		return 0, false
	}
	defer procWTSFreeMemory.Call(buffer)
	return *(*uint32)(unsafe.Pointer(buffer)), true
}

func desktopObjectName(desktop uintptr) (string, bool) {
	var needed uint32
	procGetUserObjectInformation.Call(desktop, uoiName, 0, 0, uintptr(unsafe.Pointer(&needed)))
	if needed < 2 {
		return "", false
	}
	buf := make([]uint16, (needed+1)/2)
	ok, _, _ := procGetUserObjectInformation.Call(
		desktop,
		uoiName,
		uintptr(unsafe.Pointer(&buf[0])),
		uintptr(needed),
		uintptr(unsafe.Pointer(&needed)),
	)
	if ok == 0 {
		return "", false
	}
	return windows.UTF16ToString(buf), true
}
