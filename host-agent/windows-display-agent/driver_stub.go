//go:build !windows

package main

import "time"

type unsupportedDriver struct{}

func NewWin32Driver() Driver {
	return unsupportedDriver{}
}

func (unsupportedDriver) Health() map[string]any {
	return map[string]any{"ok": false, "platform": "non-windows", "error": "unsupported-platform"}
}

func (unsupportedDriver) Focus(window string) (WindowInfo, error) {
	return WindowInfo{}, ErrUnsupported
}

func (unsupportedDriver) SendKeys(keys []string, settle time.Duration) error {
	return ErrUnsupported
}

func (unsupportedDriver) SendKeysTo(window string, keys []string, settle time.Duration) (WindowInfo, error) {
	return WindowInfo{}, ErrUnsupported
}

func (unsupportedDriver) TypeText(text string, delay time.Duration) error {
	return ErrUnsupported
}

func (unsupportedDriver) Click(x int, y int, button int) error {
	return ErrUnsupported
}

func (unsupportedDriver) Screenshot(window string) ([]byte, WindowInfo, error) {
	return nil, WindowInfo{}, ErrUnsupported
}

func (unsupportedDriver) WindowList() ([]WindowInfo, error) {
	return nil, ErrUnsupported
}

func (unsupportedDriver) VisibleListCells(window string, limit int) (WindowInfo, []string, error) {
	return WindowInfo{}, nil, ErrUnsupported
}
