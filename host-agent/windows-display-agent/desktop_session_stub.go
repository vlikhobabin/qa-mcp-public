//go:build !windows

package main

func probeDesktopSession() desktopSessionState {
	return desktopSessionActive
}
