//go:build windows

package main

import (
	"bufio"
	"fmt"
	"io"
	"os/exec"
	"strconv"
	"strings"
	"testing"
	"time"
)

const visibleCellAccessibleFixtureScript = `
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName WindowsBase
$parameters = [System.Windows.Interop.HwndSourceParameters]::new('QaMcpAccessibleFixture', 480, 300)
$parameters.WindowName = ''
$parameters.WindowStyle = 0x10CF0000
$parameters.SetPosition(100, 100)
$source = [System.Windows.Interop.HwndSource]::new($parameters)
$list = [System.Windows.Controls.ListBox]::new()
$item = [System.Windows.Controls.ListBoxItem]::new()
$item.Content = 'VisibleCell'
[System.Windows.Automation.AutomationProperties]::SetName($item, 'VisibleCell')
[void]$list.Items.Add($item)
$source.RootVisual = $list
[Console]::Out.WriteLine([long]$source.Handle)
[Console]::Out.Flush()
[System.Windows.Threading.Dispatcher]::Run()
`

type visibleCellFixtureStart struct {
	hwnd uintptr
	err  error
}

func startVisibleCellFixture() (uintptr, func(), error) {
	cmd := exec.Command(
		"powershell.exe", "-NoProfile", "-NonInteractive", "-STA",
		"-ExecutionPolicy", "Bypass", "-EncodedCommand",
		powershellEncodedCommand(visibleCellAccessibleFixtureScript),
	)
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return 0, nil, err
	}
	cmd.Stderr = io.Discard
	if err := cmd.Start(); err != nil {
		return 0, nil, err
	}

	started := make(chan visibleCellFixtureStart, 1)
	go func() {
		scanner := bufio.NewScanner(stdout)
		if !scanner.Scan() {
			started <- visibleCellFixtureStart{err: fmt.Errorf("accessible fixture did not report a window handle")}
			return
		}
		value, err := strconv.ParseUint(strings.TrimSpace(scanner.Text()), 10, 64)
		if err != nil || value == 0 {
			started <- visibleCellFixtureStart{err: fmt.Errorf("accessible fixture reported an invalid window handle")}
			return
		}
		started <- visibleCellFixtureStart{hwnd: uintptr(value)}
	}()

	var result visibleCellFixtureStart
	select {
	case result = <-started:
	case <-time.After(15 * time.Second):
		result.err = fmt.Errorf("accessible fixture startup timed out")
	}
	if result.err != nil {
		_ = cmd.Process.Kill()
		_ = cmd.Wait()
		return 0, nil, result.err
	}
	cleanup := func() {
		_ = cmd.Process.Kill()
		_ = cmd.Wait()
	}
	return result.hwnd, cleanup, nil
}

func TestWindowsVisibleListCellsReturnsOwnedNativeMarker(t *testing.T) {
	hwnd, cleanup, err := startVisibleCellFixture()
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(cleanup)
	if title := titleOf(hwnd); title != "" {
		t.Fatalf("owned target title must be empty")
	}

	cells, err := readVisibleListCells(hwnd, 10)
	if err != nil {
		t.Fatal(err)
	}
	for _, cell := range cells {
		if cell == "VisibleCell" {
			return
		}
	}
	t.Fatalf("owned native marker absent from production reader; bounded_cell_count=%d", len(cells))
}
