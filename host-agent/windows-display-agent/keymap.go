package main

import (
	"fmt"
	"strconv"
	"strings"
)

func virtualKey(name string) (uint16, bool) {
	name = strings.ToLower(strings.TrimSpace(name))
	keys := map[string]uint16{
		"return":    0x0D,
		"enter":     0x0D,
		"escape":    0x1B,
		"esc":       0x1B,
		"tab":       0x09,
		"up":        0x26,
		"down":      0x28,
		"left":      0x25,
		"right":     0x27,
		"insert":    0x2D,
		"delete":    0x2E,
		"backspace": 0x08,
		"space":     0x20,
	}
	if strings.HasPrefix(name, "f") {
		number, err := strconv.Atoi(strings.TrimPrefix(name, "f"))
		if err == nil && number >= 1 && number <= 12 {
			return uint16(0x70 + number - 1), true
		}
	}
	if len(name) == 1 {
		ch := name[0]
		if ch >= 'a' && ch <= 'z' {
			return uint16(ch - 'a' + 'A'), true
		}
		if ch >= '0' && ch <= '9' {
			return uint16(ch), true
		}
	}
	vk, ok := keys[name]
	return vk, ok
}

func keyChordVirtuals(chord string) ([]uint16, uint16, error) {
	parts := strings.Split(strings.ToLower(strings.TrimSpace(chord)), "+")
	if len(parts) == 0 || strings.TrimSpace(chord) == "" {
		return nil, 0, fmt.Errorf("unsupported key %q", chord)
	}
	var modifiers []uint16
	keyName := parts[len(parts)-1]
	for _, part := range parts[:len(parts)-1] {
		switch part {
		case "ctrl", "control":
			modifiers = append(modifiers, 0x11)
		case "alt":
			modifiers = append(modifiers, 0x12)
		case "shift":
			modifiers = append(modifiers, 0x10)
		default:
			return nil, 0, fmt.Errorf("unsupported modifier %q", part)
		}
	}
	vk, ok := virtualKey(keyName)
	if !ok {
		return nil, 0, fmt.Errorf("unsupported key %q", chord)
	}
	return modifiers, vk, nil
}

func validateKeyChords(keys []string) error {
	for _, key := range keys {
		if _, _, err := keyChordVirtuals(key); err != nil {
			return err
		}
	}
	return nil
}

func targetMessageVirtualKey(chord string) (uint16, bool, error) {
	modifiers, vk, err := keyChordVirtuals(chord)
	if err != nil {
		return 0, false, err
	}
	if len(modifiers) != 0 {
		return 0, false, nil
	}
	switch vk {
	case 0x74, 0x1B: // VK_F5 and VK_ESCAPE.
		return vk, true, nil
	default:
		return 0, false, nil
	}
}

func allTargetMessageKeys(keys []string) (bool, error) {
	if len(keys) == 0 {
		return false, nil
	}
	for _, key := range keys {
		if _, ok, err := targetMessageVirtualKey(key); err != nil {
			return false, err
		} else if !ok {
			return false, nil
		}
	}
	return true, nil
}
