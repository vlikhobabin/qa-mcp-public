package main

import "encoding/binary"

const (
	windowsTCPListenerRowSize = 24
	windowsTCPStateListen     = 2
)

// windowsTCPTableHasListener parses MIB_TCPTABLE_OWNER_PID without opening a
// TestManager connection. Windows stores dwLocalPort as a network-order uint16
// inside a DWORD.
func windowsTCPTableHasListener(table []byte, port int) bool {
	if !validTCPPort(port) || len(table) < 4 {
		return false
	}
	rows := int(binary.LittleEndian.Uint32(table[:4]))
	for index := 0; index < rows; index++ {
		offset := 4 + index*windowsTCPListenerRowSize
		if offset+windowsTCPListenerRowSize > len(table) {
			return false
		}
		state := binary.LittleEndian.Uint32(table[offset : offset+4])
		networkPort := binary.LittleEndian.Uint16(table[offset+8 : offset+10])
		localPort := int(networkPort>>8 | networkPort<<8)
		if state == windowsTCPStateListen && localPort == port {
			return true
		}
	}
	return false
}
