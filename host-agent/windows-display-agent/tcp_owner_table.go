package main

import "encoding/binary"

// pidForListeningPort parses a Windows MIB_TCPTABLE_OWNER_PID byte buffer (as
// returned by GetExtendedTcpTable with TCP_TABLE_OWNER_PID_LISTENER) and returns
// the owning PID of the first LISTEN row whose local port matches `port`.
//
// Layout: a leading DWORD dwNumEntries, then dwNumEntries MIB_TCPROW_OWNER_PID
// rows of 6 DWORDs (24 bytes) each:
//
//	0  dwState       (LISTEN == 2)
//	4  dwLocalAddr
//	8  dwLocalPort   (port in the low WORD, network byte order)
//	12 dwRemoteAddr
//	16 dwRemotePort
//	20 dwOwningPid
//
// The parsing is kept platform-neutral so it is exercised by the offline test
// suite; the Windows-only caller supplies the real table from the syscall.
func pidForListeningPort(table []byte, port uint16) (uint32, bool) {
	const (
		rowSize          = 24
		stateOffset      = 0
		localPortOffset  = 8
		owningPidOffset  = 20
		mibTCPStateListen = 2
	)
	if len(table) < 4 {
		return 0, false
	}
	count := binary.LittleEndian.Uint32(table[0:4])
	for i := uint32(0); i < count; i++ {
		base := 4 + int(i)*rowSize
		if base+rowSize > len(table) {
			break
		}
		state := binary.LittleEndian.Uint32(table[base+stateOffset : base+stateOffset+4])
		// dwLocalPort holds the port in the low two bytes in network (big-endian)
		// byte order, regardless of host endianness.
		rowPort := binary.BigEndian.Uint16(table[base+localPortOffset : base+localPortOffset+2])
		if state == mibTCPStateListen && rowPort == port {
			return binary.LittleEndian.Uint32(table[base+owningPidOffset : base+owningPidOffset+4]), true
		}
	}
	return 0, false
}
