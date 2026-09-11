//go:build windows

package main

func resolveClientTarget(pid int, port int) (WindowInfo, error) {
	if pid < 0 || !validTCPPort(port) {
		return WindowInfo{}, ErrClientTargetInvalid
	}
	listenerPID, ok := pidListeningOnPort(uint16(port))
	if !ok {
		return WindowInfo{}, ErrClientTargetStale
	}
	if pid > 0 && listenerPID != uint32(pid) {
		return WindowInfo{}, ErrClientTargetMismatch
	}
	_, info, ok := find1CWindowForPID(listenerPID)
	if !ok {
		return WindowInfo{}, ErrWindowNotFound
	}
	return info, nil
}
