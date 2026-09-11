//go:build windows

package main

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os/exec"
	"strconv"
	"strings"
	"time"
	"unicode/utf16"
	"unsafe"

	"golang.org/x/sys/windows"
)

const (
	inputKeyboard        = 1
	inputMouse           = 0
	keyeventfKeyUp       = 0x0002
	keyeventfUnicode     = 0x0004
	mapvkVkToVsc         = 0
	mouseeventfLeftDown  = 0x0002
	mouseeventfLeftUp    = 0x0004
	mouseeventfRightDown = 0x0008
	mouseeventfRightUp   = 0x0010
	pwRenderFullContent  = 0x00000002
	swShow               = 5
	swRestore            = 9
	wmKeyDown            = 0x0100
	wmKeyUp              = 0x0101
	spiGetFgLockTimeout  = 0x2000
	spiSetFgLockTimeout  = 0x2001
	lsfwUnlock           = 2
	biRGB                = 0
	dibRGBColors         = 0
	srccopy              = 0x00CC0020
)

var (
	user32                  = windows.NewLazySystemDLL("user32.dll")
	kernel32                = windows.NewLazySystemDLL("kernel32.dll")
	gdi32                   = windows.NewLazySystemDLL("gdi32.dll")
	procSendInput           = user32.NewProc("SendInput")
	procSetCursorPos        = user32.NewProc("SetCursorPos")
	procEnumWindows         = user32.NewProc("EnumWindows")
	procIsWindowVisible     = user32.NewProc("IsWindowVisible")
	procIsIconic            = user32.NewProc("IsIconic")
	procShowWindow          = user32.NewProc("ShowWindow")
	procBringWindowToTop    = user32.NewProc("BringWindowToTop")
	procSetActiveWindow     = user32.NewProc("SetActiveWindow")
	procSetFocus            = user32.NewProc("SetFocus")
	procAttachThreadInput   = user32.NewProc("AttachThreadInput")
	procSwitchToThisWindow  = user32.NewProc("SwitchToThisWindow")
	procAllowSetForeground  = user32.NewProc("AllowSetForegroundWindow")
	procLockSetForeground   = user32.NewProc("LockSetForegroundWindow")
	procMapVirtualKey       = user32.NewProc("MapVirtualKeyW")
	procPostMessage         = user32.NewProc("PostMessageW")
	procSystemParameters    = user32.NewProc("SystemParametersInfoW")
	procGetWindowTextLength = user32.NewProc("GetWindowTextLengthW")
	procGetWindowText       = user32.NewProc("GetWindowTextW")
	procGetClassName        = user32.NewProc("GetClassNameW")
	procGetWindowRect       = user32.NewProc("GetWindowRect")
	procGetForegroundWindow = user32.NewProc("GetForegroundWindow")
	procSetForegroundWindow = user32.NewProc("SetForegroundWindow")
	procGetWindowThreadPID  = user32.NewProc("GetWindowThreadProcessId")
	procPrintWindow         = user32.NewProc("PrintWindow")
	procGetWindowDC         = user32.NewProc("GetWindowDC")
	procReleaseDC           = user32.NewProc("ReleaseDC")
	procGetCurrentThreadID  = kernel32.NewProc("GetCurrentThreadId")
	procCreateCompatibleDC  = gdi32.NewProc("CreateCompatibleDC")
	procCreateCompatibleBmp = gdi32.NewProc("CreateCompatibleBitmap")
	procSelectObject        = gdi32.NewProc("SelectObject")
	procDeleteObject        = gdi32.NewProc("DeleteObject")
	procDeleteDC            = gdi32.NewProc("DeleteDC")
	procBitBlt              = gdi32.NewProc("BitBlt")
	procGetDIBits           = gdi32.NewProc("GetDIBits")
)

type win32Driver struct{}

func NewWin32Driver() Driver {
	return win32Driver{}
}

func (win32Driver) Health() map[string]any {
	hwnd, _, _ := procGetForegroundWindow.Call()
	return map[string]any{"ok": hwnd != 0, "platform": "windows", "foreground_hwnd": hwndString(hwnd)}
}

func (win32Driver) Focus(window string) (WindowInfo, error) {
	hwnd, info, err := targetWindow(window)
	if err != nil {
		return WindowInfo{}, err
	}
	if err := focusWindow(hwnd, info.HWND); err != nil {
		return info, err
	}
	time.Sleep(150 * time.Millisecond)
	return info, nil
}

func (win32Driver) SendKeys(keys []string, settle time.Duration) error {
	if err := validateKeyChords(keys); err != nil {
		return err
	}
	for _, key := range keys {
		if err := sendKeyChord(key); err != nil {
			return err
		}
		if settle > 0 {
			time.Sleep(settle)
		}
	}
	return nil
}

func (d win32Driver) SendKeysTo(window string, keys []string, settle time.Duration) (WindowInfo, error) {
	hwnd, info, err := targetWindow(window)
	if err != nil {
		return WindowInfo{}, err
	}
	targetSafe, err := allTargetMessageKeys(keys)
	if err != nil {
		return info, err
	}
	if targetSafe {
		for _, key := range keys {
			vk, _, err := targetMessageVirtualKey(key)
			if err != nil {
				return info, err
			}
			if err := postKey(hwnd, vk); err != nil {
				return info, err
			}
			if settle > 0 {
				time.Sleep(settle)
			}
		}
		return info, nil
	}
	if err := focusWindow(hwnd, info.HWND); err != nil {
		return info, err
	}
	time.Sleep(150 * time.Millisecond)
	return info, d.SendKeys(keys, settle)
}

func (win32Driver) TypeText(text string, delay time.Duration) error {
	for _, r := range text {
		if r > 0xFFFF {
			return fmt.Errorf("rune %U is outside BMP and is not supported by KEYEVENTF_UNICODE v1", r)
		}
		if err := sendUnicode(uint16(r)); err != nil {
			return err
		}
		if delay > 0 {
			time.Sleep(delay)
		}
	}
	return nil
}

func (win32Driver) Click(x int, y int, button int) error {
	if ok, _, err := procSetCursorPos.Call(uintptr(x), uintptr(y)); ok == 0 {
		return fmt.Errorf("SetCursorPos failed: %w", err)
	}
	down, up := uintptr(mouseeventfLeftDown), uintptr(mouseeventfLeftUp)
	if button == 2 {
		down, up = mouseeventfRightDown, mouseeventfRightUp
	}
	if err := sendMouse(uint32(down)); err != nil {
		return err
	}
	return sendMouse(uint32(up))
}

func (win32Driver) Screenshot(window string) ([]byte, WindowInfo, error) {
	hwnd, info, err := targetWindow(window)
	if err != nil {
		return nil, WindowInfo{}, err
	}
	pngBytes, err := captureWindowPNG(hwnd, info.Geometry)
	return pngBytes, info, err
}

func (win32Driver) WindowList() ([]WindowInfo, error) {
	return enumerateWindows(), nil
}

func (win32Driver) VisibleListCells(window string, limit int) (WindowInfo, []string, error) {
	hwnd, info, err := targetWindow(window)
	if err != nil {
		return WindowInfo{}, nil, err
	}
	cells, err := readVisibleListCells(hwnd, normalizeCellLimit(limit))
	if err != nil {
		return info, nil, err
	}
	return info, cells, nil
}

func normalizeCellLimit(limit int) int {
	if limit <= 0 {
		return 120
	}
	if limit > 500 {
		return 500
	}
	return limit
}

func readVisibleListCells(hwnd uintptr, limit int) ([]string, error) {
	script := fmt.Sprintf(`
$ErrorActionPreference = 'Stop'
# Suppress the progress stream: the first Add-Type emits a "Preparing modules
# for first use" progress record, which PowerShell serializes as a #< CLIXML
# wrapper around redirected output and breaks the JSON parse below.
$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]%d)
if ($null -eq $root) { throw 'uia-root-not-found' }
$items = New-Object 'System.Collections.Generic.List[string]'
$all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($el in $all) {
  if ($items.Count -ge %d) { break }
  $name = $el.Current.Name
  if ([string]::IsNullOrWhiteSpace($name)) { continue }
  $control = $el.Current.ControlType.ProgrammaticName
  if ($control -match 'ControlType\.(Custom|DataItem|ListItem|Text|Edit|HeaderItem)') {
    $items.Add($name.Trim())
  }
}
[pscustomobject]@{ ok = $true; cells = @($items) } | ConvertTo-Json -Depth 4 -Compress
`, hwnd, limit)
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, "powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-EncodedCommand", powershellEncodedCommand(script))
	hideChildWindow(cmd)
	out, err := cmd.CombinedOutput()
	if ctx.Err() == context.DeadlineExceeded {
		return nil, fmt.Errorf("uia-visible-cells timeout")
	}
	if err != nil {
		return nil, fmt.Errorf("uia-visible-cells failed: %w: %s", err, strings.TrimSpace(string(out)))
	}
	var payload struct {
		OK    bool     `json:"ok"`
		Cells []string `json:"cells"`
	}
	if err := json.Unmarshal(extractJSONObject(out), &payload); err != nil {
		return nil, fmt.Errorf("uia-visible-cells invalid JSON: %w: %s", err, strings.TrimSpace(string(out)))
	}
	if !payload.OK {
		return nil, fmt.Errorf("uia-visible-cells returned ok=false")
	}
	return payload.Cells, nil
}

// extractJSONObject returns the outermost { … } slice of out, tolerating a
// leading/trailing PowerShell #< CLIXML wrapper (which contains no JSON braces)
// so a stray progress/verbose record does not break the JSON parse.
func extractJSONObject(out []byte) []byte {
	start := bytes.IndexByte(out, '{')
	end := bytes.LastIndexByte(out, '}')
	if start < 0 || end < start {
		return out
	}
	return out[start : end+1]
}

func powershellEncodedCommand(script string) string {
	encoded := utf16.Encode([]rune(script))
	raw := make([]byte, 0, len(encoded)*2)
	for _, value := range encoded {
		raw = append(raw, byte(value), byte(value>>8))
	}
	return base64.StdEncoding.EncodeToString(raw)
}

func focusWindow(hwnd uintptr, label string) error {
	if isForeground(hwnd) {
		return nil
	}
	if iconic, _, _ := procIsIconic.Call(hwnd); iconic != 0 {
		procShowWindow.Call(hwnd, swRestore)
	} else {
		procShowWindow.Call(hwnd, swShow)
	}

	restoreLockTimeout := temporarilyDisableForegroundLock()
	defer restoreLockTimeout()
	procLockSetForeground.Call(lsfwUnlock)
	procAllowSetForeground.Call(^uintptr(0))

	foreground, _, _ := procGetForegroundWindow.Call()
	targetThread, _, _ := procGetWindowThreadPID.Call(hwnd, 0)
	currentThread, _, _ := procGetCurrentThreadID.Call()
	var foregroundThread uintptr
	if foreground != 0 {
		foregroundThread, _, _ = procGetWindowThreadPID.Call(foreground, 0)
	}

	detach := attachInputThreads(currentThread, targetThread, foregroundThread)
	defer detach()

	var callErr error
	for attempt := 0; attempt < 4; attempt++ {
		procSwitchToThisWindow.Call(hwnd, 1)
		procBringWindowToTop.Call(hwnd)
		procSetActiveWindow.Call(hwnd)
		procSetFocus.Call(hwnd)
		ok, _, err := procSetForegroundWindow.Call(hwnd)
		callErr = err
		if ok != 0 || isForeground(hwnd) {
			return nil
		}
		// Pressing and releasing Alt is a documented user-input path that can unlock foreground activation in an
		// interactive session. Keep this as a final attempt before failing closed.
		_ = sendKeyboard(0x12, 0, 0)
		_ = sendKeyboard(0x12, 0, keyeventfKeyUp)
		procSwitchToThisWindow.Call(hwnd, 1)
		procBringWindowToTop.Call(hwnd)
		ok, _, err = procSetForegroundWindow.Call(hwnd)
		callErr = err
		if ok != 0 || isForeground(hwnd) {
			return nil
		}
		time.Sleep(200 * time.Millisecond)
	}
	return fmt.Errorf("%w: SetForegroundWindow(%s) failed: %v", ErrForegroundDenied, label, callErr)
}

func temporarilyDisableForegroundLock() func() {
	var previous uint32
	ok, _, _ := procSystemParameters.Call(spiGetFgLockTimeout, 0, uintptr(unsafe.Pointer(&previous)), 0)
	if ok == 0 {
		return func() {}
	}
	var zero uint32
	procSystemParameters.Call(spiSetFgLockTimeout, 0, uintptr(unsafe.Pointer(&zero)), 0)
	return func() {
		procSystemParameters.Call(spiSetFgLockTimeout, 0, uintptr(unsafe.Pointer(&previous)), 0)
	}
}

func isForeground(hwnd uintptr) bool {
	foreground, _, _ := procGetForegroundWindow.Call()
	return foreground == hwnd
}

func attachInputThreads(currentThread uintptr, targetThread uintptr, foregroundThread uintptr) func() {
	var attached []uintptr
	attach := func(thread uintptr) {
		if thread == 0 || thread == currentThread {
			return
		}
		if ok, _, _ := procAttachThreadInput.Call(currentThread, thread, 1); ok != 0 {
			attached = append(attached, thread)
		}
	}
	attach(targetThread)
	attach(foregroundThread)
	return func() {
		for i := len(attached) - 1; i >= 0; i-- {
			procAttachThreadInput.Call(currentThread, attached[i], 0)
		}
	}
}

type keyboardInput struct {
	Vk        uint16
	Scan      uint16
	Flags     uint32
	Time      uint32
	ExtraInfo uintptr
}

type mouseInput struct {
	Dx        int32
	Dy        int32
	MouseData uint32
	Flags     uint32
	Time      uint32
	ExtraInfo uintptr
}

type input struct {
	Type  uint32
	Pad   uint32
	Union [32]byte
}

func sendUnicode(scan uint16) error {
	if err := sendKeyboard(0, scan, keyeventfUnicode); err != nil {
		return err
	}
	return sendKeyboard(0, scan, keyeventfUnicode|keyeventfKeyUp)
}

func sendKeyboard(vk uint16, scan uint16, flags uint32) error {
	var in input
	in.Type = inputKeyboard
	ki := (*keyboardInput)(unsafe.Pointer(&in.Union[0]))
	ki.Vk = vk
	ki.Scan = scan
	ki.Flags = flags
	return sendInputs([]input{in})
}

func sendMouse(flags uint32) error {
	var in input
	in.Type = inputMouse
	mi := (*mouseInput)(unsafe.Pointer(&in.Union[0]))
	mi.Flags = flags
	return sendInputs([]input{in})
}

func sendInputs(inputs []input) error {
	if len(inputs) == 0 {
		return nil
	}
	sent, _, err := procSendInput.Call(
		uintptr(len(inputs)),
		uintptr(unsafe.Pointer(&inputs[0])),
		unsafe.Sizeof(input{}),
	)
	if sent != uintptr(len(inputs)) {
		return fmt.Errorf("SendInput sent %d/%d: %w", sent, len(inputs), err)
	}
	return nil
}

func sendKeyChord(chord string) error {
	modifiers, vk, err := keyChordVirtuals(chord)
	if err != nil {
		return err
	}
	for _, mod := range modifiers {
		if err := sendKeyboard(mod, 0, 0); err != nil {
			return err
		}
	}
	if err := sendKeyboard(vk, 0, 0); err != nil {
		return err
	}
	if err := sendKeyboard(vk, 0, keyeventfKeyUp); err != nil {
		return err
	}
	for i := len(modifiers) - 1; i >= 0; i-- {
		if err := sendKeyboard(modifiers[i], 0, keyeventfKeyUp); err != nil {
			return err
		}
	}
	return nil
}

func postKey(hwnd uintptr, vk uint16) error {
	scan, _, _ := procMapVirtualKey.Call(uintptr(vk), mapvkVkToVsc)
	downParam := uintptr(1 | (scan << 16))
	upParam := uintptr(1 | (scan << 16) | (1 << 30) | (1 << 31))
	if ok, _, err := procPostMessage.Call(hwnd, wmKeyDown, uintptr(vk), downParam); ok == 0 {
		return fmt.Errorf("PostMessage WM_KEYDOWN %#x failed: %w", vk, err)
	}
	if ok, _, err := procPostMessage.Call(hwnd, wmKeyUp, uintptr(vk), upParam); ok == 0 {
		return fmt.Errorf("PostMessage WM_KEYUP %#x failed: %w", vk, err)
	}
	return nil
}

type winRect struct {
	Left   int32
	Top    int32
	Right  int32
	Bottom int32
}

func enumerateWindows() []WindowInfo {
	var windowsOut []WindowInfo
	cb := windows.NewCallback(func(hwnd uintptr, lparam uintptr) uintptr {
		if !visible(hwnd) {
			return 1
		}
		windowsOut = append(windowsOut, infoFor(hwnd, titleOf(hwnd)))
		return 1
	})
	procEnumWindows.Call(cb, 0)
	return windowsOut
}

func targetWindow(titleContains string) (uintptr, WindowInfo, error) {
	if titleContains == "" {
		return 0, WindowInfo{}, ErrMissingClientTarget
	}
	if strings.HasPrefix(strings.ToLower(titleContains), "class:") {
		needle := strings.ToLower(strings.TrimSpace(titleContains[6:]))
		for _, info := range enumerateWindows() {
			var hwnd uintptr
			fmt.Sscanf(info.HWND, "0x%X", &hwnd)
			if strings.Contains(strings.ToLower(classOf(hwnd)), needle) {
				return hwnd, info, nil
			}
		}
		return 0, WindowInfo{}, ErrWindowNotFound
	}
	if strings.HasPrefix(strings.ToLower(titleContains), "hwnd:") {
		raw := strings.TrimSpace(titleContains[5:])
		raw = strings.TrimPrefix(strings.ToLower(raw), "0x")
		value, err := strconv.ParseUint(raw, 16, 64)
		if err != nil || value == 0 {
			return 0, WindowInfo{}, ErrWindowNotFound
		}
		hwnd := uintptr(value)
		return hwnd, infoFor(hwnd, titleOf(hwnd)), nil
	}
	if strings.HasPrefix(strings.ToLower(titleContains), "pid:") {
		want, err := strconv.ParseUint(strings.TrimSpace(titleContains[4:]), 10, 32)
		if err != nil {
			return 0, WindowInfo{}, ErrWindowNotFound
		}
		for _, info := range enumerateWindows() {
			if info.PID == uint32(want) {
				var hwnd uintptr
				fmt.Sscanf(info.HWND, "0x%X", &hwnd)
				return hwnd, info, nil
			}
		}
		return 0, WindowInfo{}, ErrWindowNotFound
	}
	if strings.HasPrefix(strings.ToLower(titleContains), "client:") {
		parts := strings.Split(strings.TrimSpace(titleContains[7:]), ":")
		if len(parts) != 2 {
			return 0, WindowInfo{}, ErrClientTargetInvalid
		}
		pidValue, pidErr := strconv.ParseUint(parts[0], 10, 32)
		portValue, portErr := strconv.ParseUint(parts[1], 10, 16)
		if pidErr != nil || portErr != nil || pidValue == 0 || portValue == 0 {
			return 0, WindowInfo{}, ErrClientTargetInvalid
		}
		info, err := resolveClientTarget(int(pidValue), int(portValue))
		if err != nil {
			return 0, WindowInfo{}, err
		}
		var hwnd uintptr
		fmt.Sscanf(info.HWND, "0x%X", &hwnd)
		if hwnd == 0 {
			return 0, WindowInfo{}, ErrWindowNotFound
		}
		return hwnd, info, nil
	}
	if strings.HasPrefix(strings.ToLower(titleContains), "port:") {
		// Resolve the 1C window owned by the process listening on this TPort, so
		// callers can target the client they are driving without knowing its
		// config-specific caption. Falls back to nothing if the port has no
		// listener or that process has no window.
		want, err := strconv.ParseUint(strings.TrimSpace(titleContains[5:]), 10, 16)
		if err != nil || want == 0 {
			return 0, WindowInfo{}, ErrWindowNotFound
		}
		pid, ok := pidListeningOnPort(uint16(want))
		if !ok {
			return 0, WindowInfo{}, ErrWindowNotFound
		}
		if hwnd, info, ok := find1CWindowForPID(pid); ok {
			return hwnd, info, nil
		}
		return 0, WindowInfo{}, ErrWindowNotFound
	}
	needle := strings.ToLower(titleContains)
	for _, info := range enumerateWindows() {
		if strings.Contains(strings.ToLower(info.Title), needle) {
			var hwnd uintptr
			fmt.Sscanf(info.HWND, "0x%X", &hwnd)
			return hwnd, info, nil
		}
	}
	return 0, WindowInfo{}, ErrWindowNotFound
}

func visible(hwnd uintptr) bool {
	ok, _, _ := procIsWindowVisible.Call(hwnd)
	return ok != 0
}

func titleOf(hwnd uintptr) string {
	n, _, _ := procGetWindowTextLength.Call(hwnd)
	if n == 0 {
		return ""
	}
	buf := make([]uint16, n+1)
	procGetWindowText.Call(hwnd, uintptr(unsafe.Pointer(&buf[0])), n+1)
	return windows.UTF16ToString(buf)
}

func classOf(hwnd uintptr) string {
	buf := make([]uint16, 256)
	n, _, _ := procGetClassName.Call(hwnd, uintptr(unsafe.Pointer(&buf[0])), uintptr(len(buf)))
	if n == 0 {
		return ""
	}
	return windows.UTF16ToString(buf[:n])
}

// find1CWindow returns the first visible 1C top-level window — class "V8TopLevelFrame…" (the TestClient main
// SDI frame) — so callers can focus the 1C window without knowing its config-specific caption (card 124).
func find1CWindow() (uintptr, WindowInfo, bool) {
	for _, info := range enumerateWindows() {
		var hwnd uintptr
		fmt.Sscanf(info.HWND, "0x%X", &hwnd)
		if strings.HasPrefix(strings.ToLower(classOf(hwnd)), "v8toplevelframe") {
			return hwnd, info, true
		}
	}
	return 0, WindowInfo{}, false
}

func infoFor(hwnd uintptr, title string) WindowInfo {
	var pid uint32
	procGetWindowThreadPID.Call(hwnd, uintptr(unsafe.Pointer(&pid)))
	return WindowInfo{
		HWND:     hwndString(hwnd),
		Title:    title,
		Class:    classOf(hwnd),
		PID:      pid,
		Geometry: rectOf(hwnd),
		Visible:  visible(hwnd),
	}
}

func rectOf(hwnd uintptr) Rect {
	var r winRect
	procGetWindowRect.Call(hwnd, uintptr(unsafe.Pointer(&r)))
	return Rect{X: int(r.Left), Y: int(r.Top), Width: int(r.Right - r.Left), Height: int(r.Bottom - r.Top)}
}

type bitmapInfoHeader struct {
	Size          uint32
	Width         int32
	Height        int32
	Planes        uint16
	BitCount      uint16
	Compression   uint32
	SizeImage     uint32
	XPelsPerMeter int32
	YPelsPerMeter int32
	ClrUsed       uint32
	ClrImportant  uint32
}

type bitmapInfo struct {
	Header bitmapInfoHeader
	Colors [1]uint32
}

func captureWindowPNG(hwnd uintptr, rect Rect) ([]byte, error) {
	if rect.Width <= 0 || rect.Height <= 0 {
		return nil, errors.New("window has empty geometry")
	}
	hdcWindow, _, err := procGetWindowDC.Call(hwnd)
	if hdcWindow == 0 {
		return nil, fmt.Errorf("GetWindowDC failed: %w", err)
	}
	defer procReleaseDC.Call(hwnd, hdcWindow)
	hdcMem, _, err := procCreateCompatibleDC.Call(hdcWindow)
	if hdcMem == 0 {
		return nil, fmt.Errorf("CreateCompatibleDC failed: %w", err)
	}
	defer procDeleteDC.Call(hdcMem)
	hbm, _, err := procCreateCompatibleBmp.Call(hdcWindow, uintptr(rect.Width), uintptr(rect.Height))
	if hbm == 0 {
		return nil, fmt.Errorf("CreateCompatibleBitmap failed: %w", err)
	}
	defer procDeleteObject.Call(hbm)
	old, _, _ := procSelectObject.Call(hdcMem, hbm)
	defer procSelectObject.Call(hdcMem, old)
	printed, _, _ := procPrintWindow.Call(hwnd, hdcMem, pwRenderFullContent)
	if printed == 0 {
		ok, _, err := procBitBlt.Call(hdcMem, 0, 0, uintptr(rect.Width), uintptr(rect.Height), hdcWindow, 0, 0, srccopy)
		if ok == 0 {
			return nil, fmt.Errorf("PrintWindow and BitBlt failed: %w", err)
		}
	}
	buf := make([]byte, rect.Width*rect.Height*4)
	bi := bitmapInfo{Header: bitmapInfoHeader{
		Size:        uint32(unsafe.Sizeof(bitmapInfoHeader{})),
		Width:       int32(rect.Width),
		Height:      -int32(rect.Height),
		Planes:      1,
		BitCount:    32,
		Compression: biRGB,
	}}
	lines, _, err := procGetDIBits.Call(
		hdcMem,
		hbm,
		0,
		uintptr(rect.Height),
		uintptr(unsafe.Pointer(&buf[0])),
		uintptr(unsafe.Pointer(&bi)),
		dibRGBColors,
	)
	if lines == 0 {
		return nil, fmt.Errorf("GetDIBits failed: %w", err)
	}
	img := image.NewRGBA(image.Rect(0, 0, rect.Width, rect.Height))
	for y := 0; y < rect.Height; y++ {
		for x := 0; x < rect.Width; x++ {
			i := (y*rect.Width + x) * 4
			img.SetRGBA(x, y, color.RGBA{R: buf[i+2], G: buf[i+1], B: buf[i], A: 0xFF})
		}
	}
	var out bytes.Buffer
	if err := png.Encode(&out, img); err != nil {
		return nil, err
	}
	return out.Bytes(), nil
}
