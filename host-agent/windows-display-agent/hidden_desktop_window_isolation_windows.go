//go:build windows

package main

import (
	"errors"
	"strings"
	"unsafe"

	"golang.org/x/sys/windows"
)

const (
	hiddenWindowDesktopEnumerate   = 0x0040
	hiddenWindowDesktopReadObjects = 0x0001
	hiddenWindowGetOwner           = 4
)

var (
	hiddenWindowUser32       = windows.NewLazySystemDLL("user32.dll")
	hiddenWindowOpenDesktop  = hiddenWindowUser32.NewProc("OpenDesktopW")
	hiddenWindowCloseDesktop = hiddenWindowUser32.NewProc("CloseDesktop")
	hiddenWindowEnumDesktop  = hiddenWindowUser32.NewProc("EnumDesktopWindows")
	hiddenWindowGetPID       = hiddenWindowUser32.NewProc("GetWindowThreadProcessId")
	hiddenWindowGetOwnerProc = hiddenWindowUser32.NewProc("GetWindow")
	hiddenWindowGetClass     = hiddenWindowUser32.NewProc("GetClassNameW")
)

type hiddenWindowInventoryFailure string

const (
	hiddenWindowInventoryFailureOpen      hiddenWindowInventoryFailure = "open"
	hiddenWindowInventoryFailureEnumerate hiddenWindowInventoryFailure = "enumerate"
	hiddenWindowInventoryFailureOverflow  hiddenWindowInventoryFailure = "overflow"
)

func hiddenWindowDesktopLeaf(name string) (string, error) {
	if name == `Winsta0\Default` {
		return "Default", nil
	}
	if validateHiddenDesktopProcessName(name) != nil {
		return "", errors.New("window desktop identity is invalid")
	}
	return name[len(`Winsta0\`):], nil
}

func hiddenWindowInventoryOnDesktop(desktopName string) ([]hiddenWindowIdentity, error) {
	items, _, err := hiddenWindowInventoryOnDesktopClassified(desktopName)
	return items, err
}

func hiddenWindowInventoryOnDesktopClassified(desktopName string) ([]hiddenWindowIdentity, hiddenWindowInventoryFailure, error) {
	leaf, err := hiddenWindowDesktopLeaf(desktopName)
	if err != nil {
		return nil, "", err
	}
	pointer, err := windows.UTF16PtrFromString(leaf)
	if err != nil {
		return nil, "", err
	}
	handle, _, callErr := hiddenWindowOpenDesktop.Call(uintptr(unsafe.Pointer(pointer)), 0, 0, hiddenWindowDesktopEnumerate|hiddenWindowDesktopReadObjects)
	if handle == 0 {
		return nil, hiddenWindowInventoryFailureOpen, callErr
	}
	defer hiddenWindowCloseDesktop.Call(handle)
	desktopHash := hiddenWindowHash(desktopName)
	items := make([]hiddenWindowIdentity, 0, 8)
	overflow := false
	callback := windows.NewCallback(func(hwnd uintptr, _ uintptr) uintptr {
		if len(items) >= hiddenWindowInventoryLimit {
			overflow = true
			return 0
		}
		var pid uint32
		hiddenWindowGetPID.Call(hwnd, uintptr(unsafe.Pointer(&pid)))
		buffer := make([]uint16, 257)
		count, _, _ := hiddenWindowGetClass.Call(hwnd, uintptr(unsafe.Pointer(&buffer[0])), 257)
		owner, _, _ := hiddenWindowGetOwnerProc.Call(hwnd, hiddenWindowGetOwner)
		if pid != 0 && count != 0 {
			items = append(items, hiddenWindowIdentity{HWND: hwnd, PID: pid, ClassName: windows.UTF16ToString(buffer[:count]), OwnerHWND: owner, DesktopHash: desktopHash})
		}
		return 1
	})
	if ok, _, enumErr := hiddenWindowEnumDesktop.Call(handle, callback, 0); overflow || ok == 0 {
		if overflow {
			return nil, hiddenWindowInventoryFailureOverflow, errors.New("window desktop inventory is oversized")
		}
		if enumErr == windows.ERROR_SUCCESS {
			enumErr = windows.ERROR_INVALID_DATA
		}
		return nil, hiddenWindowInventoryFailureEnumerate, enumErr
	}
	return items, "", nil
}

func inventoryHiddenWindowIsolation(hiddenDesktop string, job windows.Handle) (hiddenWindowIsolationReceipt, []hiddenWindowIdentity, error) {
	receipt, hidden, _, err := inventoryHiddenWindowIsolationClassified(hiddenDesktop, job)
	return receipt, hidden, err
}

func inventoryHiddenWindowIsolationClassified(hiddenDesktop string, job windows.Handle) (hiddenWindowIsolationReceipt, []hiddenWindowIdentity, hiddenDirectInventoryFailure, error) {
	if job == 0 || !strings.HasPrefix(hiddenDesktop, `Winsta0\qa-mcp-`) {
		return hiddenWindowIsolationReceipt{}, nil, "", errors.New("window isolation lifecycle is invalid")
	}
	hidden, source, err := hiddenWindowInventoryOnDesktopClassified(hiddenDesktop)
	if err != nil {
		failure := map[hiddenWindowInventoryFailure]hiddenDirectInventoryFailure{
			hiddenWindowInventoryFailureOpen:      hiddenDirectInventoryFailureHiddenOpen,
			hiddenWindowInventoryFailureEnumerate: hiddenDirectInventoryFailureHiddenEnumerate,
			hiddenWindowInventoryFailureOverflow:  hiddenDirectInventoryFailureHiddenOverflow,
		}[source]
		return hiddenWindowIsolationReceipt{}, nil, failure, err
	}
	operator, source, err := hiddenWindowInventoryOnDesktopClassified(`Winsta0\Default`)
	if err != nil {
		failure := map[hiddenWindowInventoryFailure]hiddenDirectInventoryFailure{
			hiddenWindowInventoryFailureOpen:      hiddenDirectInventoryFailureOperatorOpen,
			hiddenWindowInventoryFailureEnumerate: hiddenDirectInventoryFailureOperatorEnumerate,
			hiddenWindowInventoryFailureOverflow:  hiddenDirectInventoryFailureOperatorOverflow,
		}[source]
		return hiddenWindowIsolationReceipt{}, nil, failure, err
	}
	member := func(pid uint32) bool { return hiddenWorkerPIDInJob(pid, uint64(job)) }
	receipt, err := validateHiddenWindowIsolation(hidden, operator, hiddenWindowHash(hiddenDesktop), hiddenWindowHash(`Winsta0\Default`), member)
	if err != nil {
		return receipt, hidden, hiddenDirectInventoryFailureIsolation, err
	}
	return receipt, hidden, "", nil
}
