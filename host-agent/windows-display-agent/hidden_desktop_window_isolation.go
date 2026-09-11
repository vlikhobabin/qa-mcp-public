package main

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"sort"
	"strings"
)

const hiddenWindowInventoryLimit = 4096

type hiddenWindowIdentity struct {
	HWND        uintptr
	PID         uint32
	ClassName   string
	OwnerHWND   uintptr
	DesktopHash string
}

type hiddenWindowIsolationReceipt struct {
	HiddenDesktopHash           string   `json:"hidden_desktop_hash"`
	OperatorDesktopHash         string   `json:"operator_desktop_hash"`
	HiddenWindowCount           int      `json:"hidden_window_count"`
	JobOwnedHiddenWindowCount   int      `json:"job_owned_hidden_window_count"`
	JobOwnedOperatorWindowCount int      `json:"job_owned_operator_window_count"`
	ClassHashes                 []string `json:"class_hashes"`
	GlobalInputCalls            uint64   `json:"global_input_calls"`
	DesktopSwitchCalls          uint64   `json:"desktop_switch_calls"`
}

func hiddenWindowHash(value string) string {
	sum := sha256.Sum256([]byte(value))
	return hex.EncodeToString(sum[:])
}

func validHiddenWindowHash(value string) bool {
	decoded, err := hex.DecodeString(value)
	return err == nil && len(decoded) == sha256.Size && strings.ToLower(value) == value
}

func validHiddenWindowIdentity(value hiddenWindowIdentity, expectedDesktop string) bool {
	return value.HWND != 0 && value.PID != 0 && value.OwnerHWND != value.HWND && value.ClassName != "" && len(value.ClassName) <= 256 && value.DesktopHash == expectedDesktop && validHiddenWindowHash(value.DesktopHash)
}

func validateHiddenWindowIsolation(hidden, operator []hiddenWindowIdentity, hiddenHash, operatorHash string, inJob func(uint32) bool) (hiddenWindowIsolationReceipt, error) {
	receipt := hiddenWindowIsolationReceipt{HiddenDesktopHash: hiddenHash, OperatorDesktopHash: operatorHash, HiddenWindowCount: len(hidden)}
	if inJob == nil || !validHiddenWindowHash(hiddenHash) || !validHiddenWindowHash(operatorHash) || hiddenHash == operatorHash || len(hidden) == 0 || len(hidden) > hiddenWindowInventoryLimit || len(operator) > hiddenWindowInventoryLimit {
		return receipt, errors.New("window isolation inventory is invalid")
	}
	hashes := make([]string, 0, len(hidden))
	for _, window := range hidden {
		if !validHiddenWindowIdentity(window, hiddenHash) || !inJob(window.PID) {
			return receipt, errors.New("foreign hidden window")
		}
		receipt.JobOwnedHiddenWindowCount++
		hashes = append(hashes, hiddenWindowHash(window.ClassName))
	}
	for _, window := range operator {
		if !validHiddenWindowIdentity(window, operatorHash) {
			return receipt, errors.New("operator window inventory is invalid")
		}
		if inJob(window.PID) {
			receipt.JobOwnedOperatorWindowCount++
			return receipt, errors.New("owned window reached operator desktop")
		}
	}
	sort.Strings(hashes)
	for _, hash := range hashes {
		if len(receipt.ClassHashes) == 0 || receipt.ClassHashes[len(receipt.ClassHashes)-1] != hash {
			receipt.ClassHashes = append(receipt.ClassHashes, hash)
		}
	}
	return receipt, nil
}

func admitExactHiddenWindow(items []hiddenWindowIdentity, desktopHash string, pid uint32, className string, owner uintptr, inJob func(uint32) bool) (hiddenWindowIdentity, error) {
	if pid == 0 || className == "" || len(className) > 256 || !validHiddenWindowHash(desktopHash) || inJob == nil {
		return hiddenWindowIdentity{}, errors.New("window predicate is invalid")
	}
	matches := make([]hiddenWindowIdentity, 0, 1)
	for _, item := range items {
		if !validHiddenWindowIdentity(item, desktopHash) || !inJob(item.PID) {
			return hiddenWindowIdentity{}, errors.New("foreign hidden window")
		}
		if item.PID == pid && strings.EqualFold(item.ClassName, className) && item.OwnerHWND == owner {
			matches = append(matches, item)
		}
	}
	if len(matches) != 1 {
		return hiddenWindowIdentity{}, errors.New("exact hidden window is missing or ambiguous")
	}
	return matches[0], nil
}
