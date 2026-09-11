package main

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"sort"
	"strings"
	"unicode/utf16"
)

const (
	hiddenDesktopProcessPrefix       = `Winsta0\qa-mcp-`
	hiddenDesktopEnvironmentPrefix   = "QA_MCP_INTERNAL_HIDDEN_"
	hiddenDesktopIdentityMaxBytes    = 256
	hiddenDesktopEnvironmentMaxItems = 512
	hiddenDesktopEnvironmentMaxUnits = 32767
)

type hiddenDesktopProcessIdentity struct {
	Desktop         string `json:"desktop"`
	RunIDHash       string `json:"run_id_hash"`
	WorkerTokenHash string `json:"worker_token_hash"`
}

func newHiddenDesktopProcessIdentity(runID, workerToken string) (hiddenDesktopProcessIdentity, error) {
	if len(runID) > hiddenDesktopIdentityMaxBytes || len(workerToken) > hiddenDesktopIdentityMaxBytes {
		return hiddenDesktopProcessIdentity{}, errors.New("bounded hidden desktop identity is required")
	}
	if runID == "" || workerToken == "" || strings.TrimSpace(runID) != runID || strings.TrimSpace(workerToken) != workerToken {
		return hiddenDesktopProcessIdentity{}, errors.New("bounded hidden desktop identity is required")
	}
	runHash := hiddenDesktopProcessHash(runID)
	return hiddenDesktopProcessIdentity{
		Desktop: hiddenDesktopProcessPrefix + runHash[:16], RunIDHash: runHash,
		WorkerTokenHash: hiddenDesktopProcessHash(workerToken),
	}, nil
}

func validateHiddenDesktopProcessIdentity(identity hiddenDesktopProcessIdentity) error {
	if len(identity.RunIDHash) != 64 || len(identity.WorkerTokenHash) != 64 ||
		identity.Desktop != hiddenDesktopProcessPrefix+identity.RunIDHash[:16] {
		return errors.New("hidden desktop identity is invalid")
	}
	if _, err := hex.DecodeString(identity.RunIDHash + identity.WorkerTokenHash); err != nil {
		return errors.New("hidden desktop identity is invalid")
	}
	return validateHiddenDesktopProcessName(identity.Desktop)
}

func validateHiddenDesktopProcessName(name string) error {
	if !strings.HasPrefix(name, hiddenDesktopProcessPrefix) || len(name) != len(hiddenDesktopProcessPrefix)+16 {
		return errors.New("hidden desktop name is invalid")
	}
	if _, err := hex.DecodeString(strings.TrimPrefix(name, hiddenDesktopProcessPrefix)); err != nil {
		return errors.New("hidden desktop name is invalid")
	}
	return nil
}

func composeHiddenDesktopProcessEnvironment(base, additions []string) ([]string, error) {
	values := make(map[string]string, len(base)+len(additions))
	for _, entry := range base {
		name, _, ok := strings.Cut(entry, "=")
		if !ok || name == "" || strings.ContainsRune(entry, 0) || strings.HasPrefix(strings.ToUpper(name), hiddenDesktopEnvironmentPrefix) {
			continue
		}
		values[strings.ToUpper(name)] = entry
	}
	for _, entry := range additions {
		name, _, ok := strings.Cut(entry, "=")
		key := strings.ToUpper(name)
		if !ok || name == "" || strings.ContainsRune(entry, 0) || !strings.HasPrefix(key, hiddenDesktopEnvironmentPrefix) {
			return nil, errors.New("hidden desktop environment addition is invalid")
		}
		if _, exists := values[key]; exists {
			return nil, errors.New("hidden desktop environment addition is duplicated")
		}
		values[key] = entry
	}
	keys := make([]string, 0, len(values))
	for key := range values {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	environment := make([]string, 0, len(keys))
	for _, key := range keys {
		environment = append(environment, values[key])
	}
	if err := validateHiddenDesktopProcessEnvironment(environment); err != nil {
		return nil, err
	}
	return environment, nil
}

func validateHiddenDesktopProcessEnvironment(environment []string) error {
	if len(environment) == 0 || len(environment) > hiddenDesktopEnvironmentMaxItems {
		return errors.New("hidden desktop environment is oversized")
	}
	seen, units := make(map[string]struct{}, len(environment)), 1
	for _, entry := range environment {
		name, _, ok := strings.Cut(entry, "=")
		key := strings.ToUpper(name)
		if !ok || name == "" || strings.ContainsRune(entry, 0) {
			return errors.New("hidden desktop environment is invalid")
		}
		if _, exists := seen[key]; exists {
			return errors.New("hidden desktop environment is duplicated")
		}
		seen[key] = struct{}{}
		units += len(utf16.Encode([]rune(entry))) + 1
	}
	if units > hiddenDesktopEnvironmentMaxUnits {
		return errors.New("hidden desktop environment is oversized")
	}
	return nil
}

func hiddenDesktopProcessHash(value string) string {
	sum := sha256.Sum256([]byte(value))
	return hex.EncodeToString(sum[:])
}
