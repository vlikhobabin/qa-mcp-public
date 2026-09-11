package main

import (
	"encoding/binary"
	"errors"
	"path/filepath"
	"strings"
	"time"
)

const hiddenWorkerLifecycleSchema = "qa-mcp.internal-hidden-worker-lifecycle.v1"

type hiddenWorkerLifecycleRequest struct {
	Identity                           hiddenDesktopProcessIdentity
	WorkerToken, ChildExecutable       string
	WorkerArgs, ChildArgs, Environment []string
	Port                               int
	Timeout                            time.Duration
}

type hiddenWorkerLifecycleResponse struct {
	Schema, Code, RunIDHash, WorkerTokenHash, DesktopHash string
	Port int; WorkerPID, ChildPID, ListenerPID uint32; WorkerJobHandle uint64
}

func validateHiddenWorkerLifecycleRequest(request hiddenWorkerLifecycleRequest) error {
	_, environmentErr := composeHiddenDesktopProcessEnvironment(request.Environment, nil)
	if validateHiddenDesktopProcessIdentity(request.Identity) != nil || hiddenDesktopProcessHash(request.WorkerToken) != request.Identity.WorkerTokenHash || !filepath.IsAbs(request.ChildExecutable) || !validTCPPort(request.Port) || request.Timeout <= 0 || request.Timeout > 2*time.Minute || environmentErr != nil ||
		!hiddenWorkerLifecycleStringsBounded(request.WorkerArgs) || !hiddenWorkerLifecycleStringsBounded(request.ChildArgs) {
		return errors.New("hidden worker lifecycle request is invalid") }
	return nil
}

func hiddenWorkerLifecycleStringsBounded(values []string) bool { return len(values) <= 128 && len(strings.Join(values, "")) <= 32768 }

func hiddenWorkerExactPIDForPort(table []byte, port uint16) (uint32, bool) {
	if len(table) < 4 { return 0, false }
	const rowSize = 24
	count := binary.LittleEndian.Uint32(table[:4])
	var owner uint32
	for index := uint32(0); index < count; index++ {
		base := 4 + int(index)*rowSize
		if base+rowSize > len(table) { return 0, false }
		if binary.LittleEndian.Uint32(table[base:base+4]) == 2 && binary.BigEndian.Uint16(table[base+8:base+10]) == port {
			if owner != 0 { return 0, false }
			owner = binary.LittleEndian.Uint32(table[base+20:base+24])
		}
	}
	return owner, owner != 0
}

func validateHiddenWorkerLifecycleResponse(request hiddenWorkerLifecycleRequest, response hiddenWorkerLifecycleResponse, workerPID uint32) error {
	if validateHiddenWorkerLifecycleRequest(request) != nil || response.Schema != hiddenWorkerLifecycleSchema || response.Code != "ready" || response.RunIDHash != request.Identity.RunIDHash || response.WorkerTokenHash != request.Identity.WorkerTokenHash || response.DesktopHash != hiddenDesktopProcessHash(request.Identity.Desktop) || response.Port != request.Port || workerPID == 0 ||
		response.WorkerPID != workerPID || response.ChildPID == 0 || response.ListenerPID == 0 || response.WorkerJobHandle == 0 {
		return errors.New("hidden worker lifecycle response is not exact-owned") }
	return nil
}

func validateHiddenWorkerTransferredObserver(response hiddenWorkerLifecycleResponse, job uint64, port int) error {
	if response.Schema != hiddenWorkerLifecycleSchema || response.Code != "ready" || !validHiddenWindowHash(response.RunIDHash) || !validHiddenWindowHash(response.WorkerTokenHash) || !validHiddenWindowHash(response.DesktopHash) || response.WorkerPID == 0 || response.ChildPID == 0 || response.ListenerPID == 0 || response.Port != port || !validTCPPort(port) || response.WorkerJobHandle == 0 || response.WorkerJobHandle != job {
		return errors.New("hidden worker transferred observer is not exact-owned") }
	return nil
}
