package main

import "strings"

var clientTargetResolver = resolveClientTarget

func isTestClientTopLevelWindow(info WindowInfo, pid uint32) bool {
	return info.PID == pid && info.Visible &&
		strings.HasPrefix(strings.ToLower(strings.TrimSpace(info.Class)), "v8toplevelframe")
}
