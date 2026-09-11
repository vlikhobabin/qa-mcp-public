package main

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
)

const maxPlatformOutputRunes = 8192

type platformExecutable struct {
	Name        string
	Path        string
	Version     string
	PrependArgv []string
}

type platformExecError struct {
	status int
	code   string
	detail string
}

func resolvePlatformExecutableVersion(name string, roots []string, requestedVersion string) (platformExecutable, *platformExecError) {
	name = strings.ToLower(strings.TrimSpace(name))
	requestedVersion = strings.TrimSpace(requestedVersion)
	if name != "1cv8" && name != "1cv8c" {
		return platformExecutable{}, &platformExecError{http.StatusBadRequest, "executable-not-allowed", "TestClient lifecycle permits only 1cv8 or 1cv8c"}
	}
	for _, candidate := range platformExecutableCandidates(roots, name) {
		if requestedVersion != "" && candidate.Version != requestedVersion {
			continue
		}
		if fileExecutable(candidate.Path) {
			return platformExecutable{Name: name, Path: candidate.Path, Version: candidate.Version}, nil
		}
	}
	if requestedVersion != "" {
		return platformExecutable{}, &platformExecError{http.StatusServiceUnavailable, "platform-version-not-found", fmt.Sprintf("%s version %s was not found in the configured platform catalog", name, requestedVersion)}
	}
	return platformExecutable{}, &platformExecError{http.StatusServiceUnavailable, "platform-executable-not-found", fmt.Sprintf("%s was not found in the configured platform catalog", name)}
}

type platformCandidate struct {
	Path    string
	Version string
}

func platformExecutableCandidates(roots []string, base string) []platformCandidate {
	var out []platformCandidate
	seen := map[string]bool{}
	for _, root := range roots {
		root = strings.TrimSpace(root)
		if root == "" {
			continue
		}
		for _, dir := range platformCandidateDirs(root) {
			for _, fileName := range platformExecutableFileNames(base) {
				candidate := filepath.Join(dir, fileName)
				if !seen[candidate] {
					seen[candidate] = true
					out = append(out, platformCandidate{candidate, platformVersionForDir(dir)})
				}
			}
		}
	}
	return out
}

func platformCandidateDirs(root string) []string {
	dirs := []string{root, filepath.Join(root, "bin")}
	entries, err := os.ReadDir(root)
	if err != nil {
		return dirs
	}
	var versions []string
	for _, entry := range entries {
		if entry.IsDir() {
			versions = append(versions, entry.Name())
		}
	}
	sort.SliceStable(versions, func(i, j int) bool { return compareVersionish(versions[i], versions[j]) > 0 })
	for _, version := range versions {
		dirs = append(dirs, filepath.Join(root, version, "bin"))
	}
	return dirs
}

func platformExecutableFileNames(base string) []string {
	if runtime.GOOS == "windows" {
		return []string{base + ".exe", base}
	}
	return []string{base, base + ".exe"}
}

func platformVersionForDir(dir string) string {
	dir = filepath.Clean(dir)
	if strings.EqualFold(filepath.Base(dir), "bin") {
		return filepath.Base(filepath.Dir(dir))
	}
	return ""
}

func fileExecutable(path string) bool {
	info, err := os.Stat(path)
	return err == nil && !info.IsDir() && (runtime.GOOS == "windows" || info.Mode()&0o111 != 0)
}

func compareVersionish(left string, right string) int {
	lp := strings.FieldsFunc(left, func(r rune) bool { return r == '.' || r == '-' || r == '_' })
	rp := strings.FieldsFunc(right, func(r rune) bool { return r == '.' || r == '-' || r == '_' })
	for i := 0; i < len(lp) || i < len(rp); i++ {
		var l, r string
		if i < len(lp) {
			l = lp[i]
		}
		if i < len(rp) {
			r = rp[i]
		}
		ln, le := strconv.Atoi(l)
		rn, re := strconv.Atoi(r)
		if le == nil && re == nil && ln != rn {
			if ln > rn {
				return 1
			}
			return -1
		}
		if l != r {
			if l > r {
				return 1
			}
			return -1
		}
	}
	return 0
}

func collectSensitiveArgs(args []string) []string {
	var secrets []string
	for index, arg := range args {
		lower := strings.ToLower(strings.TrimSpace(arg))
		if (lower == "/p" || lower == "-p" || lower == "--password") && index+1 < len(args) {
			secrets = appendSecret(secrets, args[index+1])
		}
		if strings.HasPrefix(lower, "/p") && len(arg) > 2 {
			secrets = appendSecret(secrets, strings.TrimSpace(arg)[2:])
		}
		for _, marker := range []string{"password=", "pwd=", "pass="} {
			if value, ok := valueAfterMarker(arg, lower, marker); ok {
				secrets = appendSecret(secrets, value)
			}
		}
	}
	return secrets
}

func valueAfterMarker(original string, lower string, marker string) (string, bool) {
	index := strings.Index(lower, marker)
	if index < 0 || index+len(marker) >= len(original) {
		return "", false
	}
	rest := original[index+len(marker):]
	if end := strings.IndexAny(rest, "; \t\r\n"); end >= 0 {
		rest = rest[:end]
	}
	return rest, strings.TrimSpace(rest) != ""
}

func appendSecret(secrets []string, value string) []string {
	value = strings.TrimSpace(value)
	if value == "" {
		return secrets
	}
	for _, existing := range secrets {
		if existing == value {
			return secrets
		}
	}
	return append(secrets, value)
}

func redactSensitiveText(value string, secrets []string) string {
	for _, secret := range secrets {
		if secret = strings.TrimSpace(secret); secret != "" {
			value = strings.ReplaceAll(value, secret, "[redacted-secret]")
		}
	}
	return value
}

func boundedPlatformOutput(value string, secrets []string) string {
	runes := []rune(redactSensitiveText(strings.TrimSpace(value), secrets))
	if len(runes) > maxPlatformOutputRunes {
		return string(runes[:maxPlatformOutputRunes]) + "...(truncated)"
	}
	return string(runes)
}
