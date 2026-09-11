//go:build !windows

package main

import "os/exec"

// hideChildWindow is a no-op off Windows: there is no console-window concept to suppress.
func hideChildWindow(cmd *exec.Cmd) {}

// hideChildConsole is also a no-op off Windows.
func hideChildConsole(cmd *exec.Cmd) {}
