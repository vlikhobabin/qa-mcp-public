package main

type desktopSessionState string

const (
	desktopSessionActive         desktopSessionState = "active"
	desktopSessionLocked         desktopSessionState = "locked"
	desktopSessionDisconnected   desktopSessionState = "disconnected"
	desktopSessionNonInteractive desktopSessionState = "noninteractive"
)

var desktopSessionProbe = probeDesktopSession
