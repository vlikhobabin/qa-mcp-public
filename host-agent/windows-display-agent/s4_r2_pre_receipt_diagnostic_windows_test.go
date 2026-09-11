//go:build windows

package main

import (
	"context"
	"errors"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func s4R2FileHash(path string) (string, error) {
	if !filepath.IsAbs(path) {
		return "", os.ErrInvalid
	}
	value, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return s4R2Hash(value), nil
}

func writeS4R2Diagnostic(path string, value s4R2Diagnostic) error {
	if !filepath.IsAbs(path) {
		return os.ErrInvalid
	}
	encoded, err := encodeS4R2Diagnostic(value)
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(encoded, '\n'), 0o600)
}

func TestS4R2PreReceiptDiagnosticNative(t *testing.T) {
	candidate := strings.TrimSpace(os.Getenv("QA_MCP_S4_R2_CANDIDATE"))
	platform := strings.TrimSpace(os.Getenv("QA_MCP_S4_PLATFORM_EXE"))
	target := strings.TrimSpace(os.Getenv("QA_MCP_S4_TARGET"))
	fixture := strings.TrimSpace(os.Getenv("QA_MCP_S4_EPF"))
	selector := strings.TrimSpace(os.Getenv("QA_MCP_S4_MARKER_AUTOMATION_ID_SHA256"))
	receiptDir := strings.TrimSpace(os.Getenv("QA_MCP_S4_R2_RECEIPT_DIR"))
	if candidate == "" || platform == "" || target == "" || fixture == "" || selector == "" || receiptDir == "" {
		t.Skip("exact S4-R2 Windows diagnostic inputs are unavailable")
	}
	if !filepath.IsAbs(candidate) || !filepath.IsAbs(platform) || !filepath.IsAbs(target) || !filepath.IsAbs(fixture) || !filepath.IsAbs(receiptDir) {
		t.Fatal("S4-R2 diagnostic paths are not absolute")
	}
	candidateHash, candidateErr := s4R2FileHash(candidate)
	platformHash, platformErr := s4R2FileHash(platform)
	fixtureHash, fixtureErr := s4R2FileHash(fixture)
	identity := s4R2DiagnosticIdentity{
		CandidateSHA256: candidateHash,
		PlatformSHA256:  platformHash,
		TargetSHA256:    s4R2Hash([]byte(strings.ToLower(filepath.Clean(target)))),
		FixtureSHA256:   fixtureHash,
		ArgvSHA256: s4R2Hash([]byte(strings.Join([]string{
			"TestHiddenDirectObservationNative", strings.ToLower(filepath.Clean(platform)),
			strings.ToLower(filepath.Clean(target)), strings.ToLower(filepath.Clean(fixture)), selector,
			"user_present=" + boolString(os.Getenv("QA_MCP_S4_USER") != ""),
			"password_present=" + boolString(os.Getenv("QA_MCP_S4_PASSWORD") != ""),
		}, "\x00"))),
	}
	outputPath := filepath.Join(receiptDir, "s4-r2-diagnostic.json")
	checkpointPath := filepath.Join(receiptDir, "native-pre-receipt-diagnostic.json")
	if candidateErr != nil || platformErr != nil || fixtureErr != nil || !s4R2ValidHash(selector) ||
		!strings.EqualFold(filepath.Clean(target), `C:\1C_BASES\vanessa_client`) ||
		!strings.Contains(strings.ToLower(platform), `\8.3.27.2214\`) {
		t.Fatal("S4-R2 diagnostic setup is invalid")
	}
	if err := os.MkdirAll(receiptDir, 0o700); err != nil {
		t.Fatal("S4-R2 receipt directory is unavailable")
	}
	if _, err := os.Stat(outputPath); !os.IsNotExist(err) {
		t.Fatal("S4-R2 diagnostic output is not fresh")
	}
	expectedCandidate := strings.TrimSpace(os.Getenv("QA_MCP_S4_R2_EXPECTED_CANDIDATE_SHA256"))
	expectedPlatform := strings.TrimSpace(os.Getenv("QA_MCP_S4_R2_EXPECTED_PLATFORM_SHA256"))
	expectedFixture := strings.TrimSpace(os.Getenv("QA_MCP_S4_R2_EXPECTED_FIXTURE_SHA256"))
	if candidateHash != expectedCandidate || platformHash != expectedPlatform || fixtureHash != expectedFixture {
		value, valueErr := newS4R2Failure(identity, s4R2ArgvValidation, s4R2FailureArgvValidation, -1, false, false, nil)
		if valueErr == nil {
			_ = writeS4R2Diagnostic(outputPath, value)
		}
		t.Fatal("S4-R2 candidate, platform or fixture identity differs")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 135*time.Second)
	defer cancel()
	command := exec.CommandContext(ctx, candidate, "-test.run=^TestHiddenDirectObservationNative$", "-test.count=1", "-test.timeout=120s")
	command.Env = append(os.Environ(), "QA_MCP_S4_RECEIPT_DIR="+receiptDir)
	command.Stdout = io.Discard
	command.Stderr = io.Discard
	if err := command.Start(); err != nil {
		value, valueErr := newS4R2Failure(identity, s4R2ChildLaunch, s4R2FailureChildLaunch, -1, false, false, nil)
		if valueErr != nil || writeS4R2Diagnostic(outputPath, value) != nil {
			t.Fatal("S4-R2 child launch and diagnostic write failed")
		}
		return
	}
	exitCode := 0
	if err := command.Wait(); err != nil {
		var exitErr *exec.ExitError
		if errors.As(err, &exitErr) {
			exitCode = exitErr.ExitCode()
		} else {
			exitCode = -1
		}
	}
	if ctx.Err() != nil {
		t.Fatal("S4-R2 external candidate exceeded its bounded timeout")
	}
	checkpoint, readErr := os.ReadFile(checkpointPath)
	if readErr != nil && !os.IsNotExist(readErr) {
		t.Fatal("S4-R2 checkpoint could not be read")
	}
	if exitCode == 0 {
		t.Fatal("S4-R2 candidate produced an unexpected positive row; investigation classification is not applicable")
	}
	value, err := classifyS4R2CandidateExit(identity, checkpoint, exitCode)
	if err != nil || writeS4R2Diagnostic(outputPath, value) != nil {
		t.Fatal("S4-R2 candidate failure could not be typed safely")
	}
}

func boolString(value bool) string {
	if value {
		return "true"
	}
	return "false"
}
