//go:build !windows

package main

func resolveClientTarget(pid int, port int) (WindowInfo, error) {
	return WindowInfo{}, ErrUnsupported
}
