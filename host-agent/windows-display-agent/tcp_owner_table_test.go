package main

import (
	"encoding/binary"
	"testing"
)

// buildRow renders one MIB_TCPROW_OWNER_PID (24 bytes).
func buildRow(state uint32, localPort uint16, pid uint32) []byte {
	row := make([]byte, 24)
	binary.LittleEndian.PutUint32(row[0:4], state)   // dwState
	binary.LittleEndian.PutUint32(row[4:8], 0)       // dwLocalAddr
	binary.BigEndian.PutUint16(row[8:10], localPort) // dwLocalPort low WORD, network order
	binary.LittleEndian.PutUint32(row[12:16], 0)     // dwRemoteAddr
	binary.LittleEndian.PutUint32(row[16:20], 0)     // dwRemotePort
	binary.LittleEndian.PutUint32(row[20:24], pid)   // dwOwningPid
	return row
}

func buildTable(rows ...[]byte) []byte {
	table := make([]byte, 4)
	binary.LittleEndian.PutUint32(table[0:4], uint32(len(rows)))
	for _, r := range rows {
		table = append(table, r...)
	}
	return table
}

const stateListen = 2
const stateEstablished = 5

func TestPidForListeningPortFindsListener(t *testing.T) {
	table := buildTable(
		buildRow(stateEstablished, 15381, 100), // established on 15381 — must be ignored
		buildRow(stateListen, 15383, 4242),     // the listener we want
		buildRow(stateListen, 8001, 777),
	)
	pid, ok := pidForListeningPort(table, 15383)
	if !ok || pid != 4242 {
		t.Fatalf("pid = %d ok = %v, want 4242 true", pid, ok)
	}
}

func TestPidForListeningPortKeepsFirstMatchingListener(t *testing.T) {
	table := buildTable(
		buildRow(stateListen, 15383, 4242),
		buildRow(stateListen, 15383, 7777),
	)
	pid, ok := pidForListeningPort(table, 15383)
	if !ok || pid != 4242 {
		t.Fatalf("pid = %d ok = %v, want first match 4242 true", pid, ok)
	}
}

func TestPidForListeningPortIgnoresNonListen(t *testing.T) {
	// Only an ESTABLISHED row on the port — not a listener, so no match.
	table := buildTable(buildRow(stateEstablished, 15383, 4242))
	if pid, ok := pidForListeningPort(table, 15383); ok {
		t.Fatalf("established-only port should not match, got pid %d", pid)
	}
}

func TestPidForListeningPortMissing(t *testing.T) {
	table := buildTable(buildRow(stateListen, 8001, 777))
	if pid, ok := pidForListeningPort(table, 15383); ok {
		t.Fatalf("absent port should not match, got pid %d", pid)
	}
}

func TestPidForListeningPortEmptyOrShort(t *testing.T) {
	if _, ok := pidForListeningPort(nil, 15383); ok {
		t.Fatal("nil table should not match")
	}
	if _, ok := pidForListeningPort([]byte{1, 2}, 15383); ok {
		t.Fatal("short table should not match")
	}
	// Header claims 3 rows but the buffer is truncated after one — must not panic.
	trunc := buildTable(buildRow(stateListen, 15383, 4242))
	binary.LittleEndian.PutUint32(trunc[0:4], 3)
	if pid, ok := pidForListeningPort(trunc, 15383); !ok || pid != 4242 {
		t.Fatalf("truncated table: pid = %d ok = %v, want 4242 true", pid, ok)
	}
	if _, ok := pidForListeningPort(trunc, 8001); ok {
		t.Fatal("truncated table should stop cleanly without a false match")
	}
}
