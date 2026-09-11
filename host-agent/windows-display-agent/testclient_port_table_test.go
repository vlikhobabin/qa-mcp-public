package main

import (
	"encoding/binary"
	"testing"
)

func TestWindowsTCPTableListenerInspectionDoesNotNeedAConnection(t *testing.T) {
	table := make([]byte, 4+2*windowsTCPListenerRowSize)
	binary.LittleEndian.PutUint32(table[:4], 2)
	first := table[4 : 4+windowsTCPListenerRowSize]
	binary.LittleEndian.PutUint32(first[:4], 5)
	binary.LittleEndian.PutUint16(first[8:10], 0x153c)
	second := table[4+windowsTCPListenerRowSize:]
	binary.LittleEndian.PutUint32(second[:4], windowsTCPStateListen)
	binary.LittleEndian.PutUint16(second[8:10], 0x153c)

	if !windowsTCPTableHasListener(table, 15381) {
		t.Fatal("listener port 15381 was not found")
	}
	if windowsTCPTableHasListener(table, 15382) {
		t.Fatal("unrelated relay port was reported as listening")
	}
}

func TestWindowsTCPTableInspectionFailsClosedOnTruncation(t *testing.T) {
	table := make([]byte, 4+windowsTCPListenerRowSize-1)
	binary.LittleEndian.PutUint32(table[:4], 1)
	if windowsTCPTableHasListener(table, 15381) {
		t.Fatal("truncated table was accepted")
	}
}
