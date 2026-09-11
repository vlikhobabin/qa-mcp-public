package main

import "unicode/utf16"

// windowsEnvironmentBlock renders a Windows CreateProcess environment block:
// a sequence of NUL-terminated UTF-16 "KEY=VALUE" segments followed by one
// extra terminating NUL. Each segment is encoded independently so the interior
// NUL separators are part of the block rather than an argument to a
// NUL-forbidding helper. (syscall.StringToUTF16 panics on any interior NUL, so
// it must never be handed the joined block.) The encoding is pure Go so it is
// exercised by the offline test suite on every platform.
func windowsEnvironmentBlock(env []string) []uint16 {
	if len(env) == 0 {
		return nil
	}
	block := make([]uint16, 0, len(env)*16+1)
	nonEmpty := 0
	for _, entry := range env {
		if entry == "" {
			continue
		}
		block = append(block, utf16.Encode([]rune(entry))...)
		block = append(block, 0) // terminate this KEY=VALUE segment
		nonEmpty++
	}
	if nonEmpty == 0 {
		return nil
	}
	block = append(block, 0) // final block terminator
	return block
}
