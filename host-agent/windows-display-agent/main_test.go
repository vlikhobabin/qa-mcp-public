package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"testing"
	"time"
)

type fakeDriver struct {
	keys              []string
	targetWindows     []string
	typed             string
	clicks            [][3]int
	windows           []WindowInfo
	windowListCalls   int
	visibleTarget     WindowInfo
	visibleCells      []string
	visibleErr        error
	visibleCalls      int
	focusCalls        int
	sendKeysToErr     error
	targetInfo        WindowInfo
	screenshotCalls   int
	screenshotWindows []string
	visibleWindows    []string
}

func (f *fakeDriver) Health() map[string]any {
	return map[string]any{"ok": true, "platform": "test"}
}

func (f *fakeDriver) Focus(window string) (WindowInfo, error) {
	f.focusCalls++
	f.targetWindows = append(f.targetWindows, window)
	return WindowInfo{HWND: "0x1", Title: window, Geometry: Rect{Width: 10, Height: 10}, Visible: true}, nil
}

func (f *fakeDriver) SendKeys(keys []string, settle time.Duration) error {
	f.keys = append(f.keys, keys...)
	return nil
}

func (f *fakeDriver) SendKeysTo(window string, keys []string, settle time.Duration) (WindowInfo, error) {
	f.targetWindows = append(f.targetWindows, window)
	info := f.targetInfo
	if info.HWND == "" {
		info = WindowInfo{HWND: "0x1", Title: window, Geometry: Rect{Width: 10, Height: 10}, Visible: true}
	}
	if f.sendKeysToErr != nil {
		return info, f.sendKeysToErr
	}
	f.keys = append(f.keys, keys...)
	return info, nil
}

func (f *fakeDriver) TypeText(text string, delay time.Duration) error {
	f.typed += text
	return nil
}

func (f *fakeDriver) Click(x int, y int, button int) error {
	f.clicks = append(f.clicks, [3]int{x, y, button})
	return nil
}

func (f *fakeDriver) Screenshot(window string) ([]byte, WindowInfo, error) {
	f.screenshotCalls++
	f.screenshotWindows = append(f.screenshotWindows, window)
	return []byte("\x89PNG\r\n\x1a\nfake"), WindowInfo{HWND: "0x1", Title: "1C", Geometry: Rect{Width: 10, Height: 10}, Visible: true}, nil
}

func (f *fakeDriver) WindowList() ([]WindowInfo, error) {
	f.windowListCalls++
	if f.windows != nil {
		return f.windows, nil
	}
	return []WindowInfo{{HWND: "0x1", Title: "1C", Geometry: Rect{X: 1, Y: 2, Width: 3, Height: 4}, Visible: true}}, nil
}

func (f *fakeDriver) VisibleListCells(window string, limit int) (WindowInfo, []string, error) {
	f.visibleCalls++
	f.visibleWindows = append(f.visibleWindows, window)
	if f.visibleErr != nil {
		return WindowInfo{}, nil, f.visibleErr
	}
	target := f.visibleTarget
	if target.HWND == "" {
		target = WindowInfo{HWND: "0x1", Title: window, Class: "V8TopLevelFrameSDI", Geometry: Rect{Width: 10, Height: 10}, Visible: true}
	}
	cells := f.visibleCells
	if cells == nil {
		cells = []string{"Российский рубль Наименование валюты", "643 Цифр. код"}
	}
	if limit > 0 && limit < len(cells) {
		cells = cells[:limit]
	}
	return target, cells, nil
}

func recordOwnedDisplayTarget(agent *Agent) map[string]any {
	done := make(chan struct{})
	agent.testClients.Record(&launchedTestClientProcess{
		PID: 4321, LifecycleID: "launch-1", Done: done, Terminate: func() error { return nil },
	}, 15444, testClientLaunchContext{})
	return map[string]any{
		"kind": "host-agent-testclient", "lifecycle_id": "launch-1", "pid": 4321, "port": 15444,
	}
}

func request(handler http.Handler, method string, path string, token string, body any) *httptest.ResponseRecorder {
	return requestWithOrigin(handler, method, path, token, "", body)
}

func requestWithOrigin(handler http.Handler, method string, path string, token string, origin string, body any) *httptest.ResponseRecorder {
	var reader *bytes.Reader
	if body == nil {
		reader = bytes.NewReader(nil)
	} else {
		raw, _ := json.Marshal(body)
		reader = bytes.NewReader(raw)
	}
	req := httptest.NewRequest(method, path, reader)
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	if token != "" {
		req.Header.Set("X-QA-MCP-Agent-Token", token)
	}
	if origin != "" {
		req.Header.Set("Origin", origin)
	}
	rec := httptest.NewRecorder()
	handler.ServeHTTP(rec, req)
	return rec
}

func rawRequest(handler http.Handler, method string, path string, token string, raw string) *httptest.ResponseRecorder {
	req := httptest.NewRequest(method, path, strings.NewReader(raw))
	req.Header.Set("Content-Type", "application/json")
	if token != "" {
		req.Header.Set("X-QA-MCP-Agent-Token", token)
	}
	rec := httptest.NewRecorder()
	handler.ServeHTTP(rec, req)
	return rec
}

func writeFakeCLI(t *testing.T, dir string, name string, body string) string {
	t.Helper()
	path := filepath.Join(dir, name)
	if err := os.WriteFile(path, []byte("#!/bin/sh\nset -eu\n"+body), 0o755); err != nil {
		t.Fatal(err)
	}
	return path
}

func writeFakePlatformBinary(t *testing.T, root string, name string, body string) string {
	t.Helper()
	binDir := filepath.Join(root, "8.3.27.2130", "bin")
	if err := os.MkdirAll(binDir, 0o755); err != nil {
		t.Fatal(err)
	}
	return writeFakeCLI(t, binDir, name, body)
}

func freeTCPPort(t *testing.T) int {
	t.Helper()
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer ln.Close()
	_, portText, err := net.SplitHostPort(ln.Addr().String())
	if err != nil {
		t.Fatal(err)
	}
	port, err := strconv.Atoi(portText)
	if err != nil {
		t.Fatal(err)
	}
	return port
}

func setFakePATH(t *testing.T, dir string) {
	t.Helper()
	old := os.Getenv("PATH")
	if old == "" {
		t.Setenv("PATH", dir)
		return
	}
	t.Setenv("PATH", dir+string(os.PathListSeparator)+old)
}

func TestVersionAndHealth(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	handler := agent.Handler()

	unauthorizedVersion := request(handler, http.MethodGet, "/version", "", nil)
	if unauthorizedVersion.Code != http.StatusUnauthorized {
		t.Fatalf("unauthorized version status = %d", unauthorizedVersion.Code)
	}
	if bytes.Contains(unauthorizedVersion.Body.Bytes(), []byte("sha256")) {
		t.Fatalf("unauthorized version leaked sha256: %s", unauthorizedVersion.Body.String())
	}

	version := request(handler, http.MethodGet, "/version", "tok", nil)
	if version.Code != http.StatusOK {
		t.Fatalf("version status = %d", version.Code)
	}
	var payload map[string]any
	if err := json.Unmarshal(version.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["version"] != AgentVersion {
		t.Fatalf("version = %v", payload["version"])
	}
	if payload["display_protocol"] != DisplayProtocol {
		t.Fatalf("display protocol = %v", payload["display_protocol"])
	}
	capabilities, ok := payload["capabilities"].([]any)
	if !ok || len(capabilities) != len(StandaloneCapabilities) || capabilities[0] != "health" {
		t.Fatalf("capabilities = %#v", payload["capabilities"])
	}

	unauthorizedHealth := request(handler, http.MethodGet, "/health", "", nil)
	if unauthorizedHealth.Code != http.StatusUnauthorized {
		t.Fatalf("unauthorized health status = %d", unauthorizedHealth.Code)
	}
	if bytes.Contains(unauthorizedHealth.Body.Bytes(), []byte("foreground_hwnd")) {
		t.Fatalf("unauthorized health leaked foreground state: %s", unauthorizedHealth.Body.String())
	}

	health := request(handler, http.MethodGet, "/health", "tok", nil)
	if health.Code != http.StatusOK {
		t.Fatalf("health status = %d", health.Code)
	}
}

func TestLoadTokenFileIgnoresUTF8BOM(t *testing.T) {
	path := filepath.Join(t.TempDir(), "token.txt")
	if err := os.WriteFile(path, append([]byte{0xEF, 0xBB, 0xBF}, []byte("tok\r\n")...), 0o600); err != nil {
		t.Fatal(err)
	}
	token, err := loadToken("", path)
	if err != nil {
		t.Fatal(err)
	}
	if token != "tok" {
		t.Fatalf("token = %q", token)
	}
}

func TestPrimitiveRequiresToken(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	rec := request(agent.Handler(), http.MethodPost, "/type", "", map[string]any{"text": "x"})
	if rec.Code != http.StatusUnauthorized {
		t.Fatalf("status = %d", rec.Code)
	}
}

func TestHostileOriginRejected(t *testing.T) {
	agent := NewAgent(Config{Token: "tok", AllowedOrigins: []string{"https://allowed.example"}}, &fakeDriver{})
	rec := requestWithOrigin(agent.Handler(), http.MethodPost, "/type", "tok", "https://evil.example", map[string]any{"text": "x"})
	if rec.Code != http.StatusForbidden {
		t.Fatalf("status = %d body=%s", rec.Code, rec.Body.String())
	}
}

func TestAllowedOriginAccepted(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok", AllowedOrigins: []string{"https://allowed.example"}}, driver)
	target := recordOwnedDisplayTarget(agent)
	rec := requestWithOrigin(agent.Handler(), http.MethodPost, "/type", "tok", "https://allowed.example", map[string]any{
		"text": "x", "window": "class:V8TopLevelFrame", "client_target": target,
	})
	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", rec.Code, rec.Body.String())
	}
	if driver.typed != "x" {
		t.Fatalf("typed = %q", driver.typed)
	}
}

func TestFailedAuthRateLimited(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	handler := agent.Handler()
	for i := 0; i < 5; i++ {
		rec := request(handler, http.MethodPost, "/type", "bad", map[string]any{"text": "x"})
		if rec.Code != http.StatusUnauthorized {
			t.Fatalf("attempt %d status = %d", i, rec.Code)
		}
	}
	rec := request(handler, http.MethodPost, "/type", "bad", map[string]any{"text": "x"})
	if rec.Code != http.StatusTooManyRequests {
		t.Fatalf("rate-limited status = %d", rec.Code)
	}
}

func TestFailedAuthLimiterEvictsStaleEntries(t *testing.T) {
	limiter := newFailureLimiter(2, time.Minute)
	now := time.Unix(1000, 0)
	old := now.Add(-2 * time.Minute)
	active := now.Add(-30 * time.Second)
	limiter.attempts["old"] = []time.Time{old}
	limiter.attempts["mixed"] = []time.Time{old, active}

	if !limiter.allowAt("new", now) {
		t.Fatal("new key should be allowed")
	}
	if _, ok := limiter.attempts["old"]; ok {
		t.Fatalf("stale key was not evicted: %#v", limiter.attempts)
	}
	if got := limiter.attempts["mixed"]; len(got) != 1 || !got[0].Equal(active) {
		t.Fatalf("mixed key was not pruned to active attempt: %#v", got)
	}
	if got := limiter.attempts["new"]; len(got) != 1 || !got[0].Equal(now) {
		t.Fatalf("new attempt missing: %#v", got)
	}
}

func TestExecutionLimiterReleasesCapacity(t *testing.T) {
	limiter := newExecutionLimiter(1)
	release, ok := limiter.acquire()
	if !ok {
		t.Fatal("first acquire failed")
	}
	if _, ok := limiter.acquire(); ok {
		t.Fatal("second acquire unexpectedly succeeded while slot was occupied")
	}
	release()
	release2, ok := limiter.acquire()
	if !ok {
		t.Fatal("acquire after release failed")
	}
	release2()
}

func TestAuthenticatedExecutionRouteRejectsOverCapacityBeforeDriver(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	agent.execLimit = newExecutionLimiter(1)
	release, ok := agent.execLimit.acquire()
	if !ok {
		t.Fatal("failed to occupy execution slot")
	}
	defer release()

	routes := []struct {
		path string
		body map[string]any
	}{
		{"/send_keys", map[string]any{"keys": []string{"F5"}}},
		{"/type", map[string]any{"text": "x"}},
		{"/click", map[string]any{"x": 1, "y": 2}},
		{"/screenshot", map[string]any{}},
		{"/window_list", map[string]any{"geometry": true}},
		{"/uia/visible_list_cells", map[string]any{"limit": 1}},
		{"/testclient/launch", map[string]any{"port": 15444}},
		{"/testclient/status", map[string]any{"port": 15444}},
		{"/testclient/stop", map[string]any{"pid": 4321}},
	}
	for _, tc := range routes {
		resp := request(agent.Handler(), http.MethodPost, tc.path, "tok", tc.body)
		if resp.Code != http.StatusTooManyRequests {
			t.Fatalf("path=%s status=%d body=%s", tc.path, resp.Code, resp.Body.String())
		}
		var payload map[string]any
		if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
			t.Fatal(err)
		}
		if payload["error"] != "execution-capacity-exhausted" {
			t.Fatalf("path=%s payload=%#v", tc.path, payload)
		}
	}
	if driver.windowListCalls != 0 || driver.visibleCalls != 0 || driver.screenshotCalls != 0 {
		t.Fatalf("driver ran while capacity was exhausted: %#v", driver)
	}
}

func TestExecutionRouteReleasesCapacityAfterHandlerFailure(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	agent.execLimit = newExecutionLimiter(1)
	handler := agent.Handler()

	invalid := rawRequest(handler, http.MethodPost, "/send_keys", "tok", "{")
	if invalid.Code != http.StatusBadRequest {
		t.Fatalf("invalid status=%d body=%s", invalid.Code, invalid.Body.String())
	}
	valid := request(handler, http.MethodPost, "/testclient/status", "tok", map[string]any{"port": 15444})
	if valid.Code != http.StatusOK {
		t.Fatalf("valid status=%d body=%s", valid.Code, valid.Body.String())
	}
}

func TestLoadTokenFromFile(t *testing.T) {
	path := filepath.Join(t.TempDir(), "token")
	if err := os.WriteFile(path, []byte(" file-token \n"), 0o600); err != nil {
		t.Fatal(err)
	}
	token, err := loadToken("", path)
	if err != nil {
		t.Fatal(err)
	}
	if token != "file-token" {
		t.Fatalf("token = %q", token)
	}
}

func TestTypeAndSendKeys(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	target := recordOwnedDisplayTarget(agent)
	handler := agent.Handler()

	typed := request(handler, http.MethodPost, "/type", "tok", map[string]any{
		"text": "WIN-OK-К", "window": "class:V8TopLevelFrame", "client_target": target,
	})
	if typed.Code != http.StatusOK {
		t.Fatalf("type status = %d body=%s", typed.Code, typed.Body.String())
	}
	if driver.typed != "WIN-OK-К" {
		t.Fatalf("typed = %q", driver.typed)
	}

	keys := request(handler, http.MethodPost, "/send_keys", "tok", map[string]any{
		"keys": []string{"Tab", "ctrl+s"}, "window": "class:V8TopLevelFrame", "client_target": target,
	})
	if keys.Code != http.StatusOK {
		t.Fatalf("keys status = %d body=%s", keys.Code, keys.Body.String())
	}
	if len(driver.keys) != 2 || driver.keys[1] != "ctrl+s" {
		t.Fatalf("keys = %#v", driver.keys)
	}
}

func TestSendKeysUsesTargetWindowDriverPath(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	target := recordOwnedDisplayTarget(agent)
	handler := agent.Handler()

	resp := request(handler, http.MethodPost, "/send_keys", "tok", map[string]any{
		"keys":          []string{"F5", "Escape"},
		"window":        "class:V8TopLevelFrame",
		"client_target": target,
	})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	if driver.focusCalls != 0 {
		t.Fatalf("Focus called %d times; want no foreground focus from handler", driver.focusCalls)
	}
	if len(driver.targetWindows) != 1 || driver.targetWindows[0] != "client:4321:15444" {
		t.Fatalf("target windows = %#v", driver.targetWindows)
	}
	if len(driver.keys) != 2 || driver.keys[0] != "F5" || driver.keys[1] != "Escape" {
		t.Fatalf("keys = %#v", driver.keys)
	}
}

func TestDisplayRequestUsesOwnedLifecycleClientTargetWithEmptyTitle(t *testing.T) {
	done := make(chan struct{})
	driver := &fakeDriver{targetInfo: WindowInfo{
		HWND: "0x77", Title: "", Class: "V8TopLevelFrameSDI", PID: 4321,
		Geometry: Rect{Width: 10, Height: 10}, Visible: true,
	}}
	agent := NewAgent(Config{Token: "tok"}, driver)
	agent.testClients.Record(&launchedTestClientProcess{
		PID: 4321, LifecycleID: "launch-1", Done: done, Terminate: func() error { return nil },
	}, 15444, testClientLaunchContext{})

	resp := request(agent.Handler(), http.MethodPost, "/send_keys", "tok", map[string]any{
		"keys": []string{"F5"},
		"client_target": map[string]any{
			"kind": "host-agent-testclient", "lifecycle_id": "launch-1", "pid": 4321, "port": 15444,
		},
	})

	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	if len(driver.targetWindows) != 1 || driver.targetWindows[0] != "client:4321:15444" {
		t.Fatalf("target windows = %#v", driver.targetWindows)
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	target := payload["target"].(map[string]any)
	if target["title"] != "" || target["class"] != "V8TopLevelFrameSDI" {
		t.Fatalf("target = %#v", target)
	}
}

func TestClientTargetWindowPredicateRejectsSameProcessGenericWindow(t *testing.T) {
	pid := uint32(4321)
	if isTestClientTopLevelWindow(WindowInfo{
		Title: "Other dialog", Class: "#32770", PID: pid, Visible: true,
	}, pid) {
		t.Fatal("same-process generic window must not satisfy TestClient targeting")
	}
	if !isTestClientTopLevelWindow(WindowInfo{
		Title: "", Class: "V8TopLevelFrameSDI", PID: pid, Visible: true,
	}, pid) {
		t.Fatal("visible empty-title TestClient frame must satisfy exact targeting")
	}
	if isTestClientTopLevelWindow(WindowInfo{
		Title: "", Class: "V8TopLevelFrameSDI", PID: pid + 1, Visible: true,
	}, pid) {
		t.Fatal("unrelated process window must not satisfy TestClient targeting")
	}
}

func TestAllDisplayRoutesUseImplicitClientTarget(t *testing.T) {
	tests := []struct {
		name     string
		path     string
		body     map[string]any
		selected func(*fakeDriver) []string
	}{
		{"send_keys", "/send_keys", map[string]any{"keys": []string{"F5"}}, func(d *fakeDriver) []string { return d.targetWindows }},
		{"type", "/type", map[string]any{"text": "safe"}, func(d *fakeDriver) []string { return d.targetWindows }},
		{"click", "/click", map[string]any{"x": 1, "y": 2}, func(d *fakeDriver) []string { return d.targetWindows }},
		{"screenshot", "/screenshot", map[string]any{}, func(d *fakeDriver) []string { return d.screenshotWindows }},
		{"visible_cells", "/uia/visible_list_cells", map[string]any{"limit": 1}, func(d *fakeDriver) []string { return d.visibleWindows }},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			driver := &fakeDriver{}
			agent := NewAgent(Config{Token: "tok"}, driver)
			tc.body["client_target"] = recordOwnedDisplayTarget(agent)
			resp := request(agent.Handler(), http.MethodPost, tc.path, "tok", tc.body)
			if resp.Code != http.StatusOK {
				t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
			}
			selected := tc.selected(driver)
			if len(selected) != 1 || selected[0] != "client:4321:15444" {
				t.Fatalf("selected windows = %#v", selected)
			}
		})
	}
}

func TestDisplayRequestExplicitWindowCannotOverrideOwnedClientTarget(t *testing.T) {
	done := make(chan struct{})
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	agent.testClients.Record(&launchedTestClientProcess{
		PID: 4321, LifecycleID: "launch-1", Done: done, Terminate: func() error { return nil },
	}, 15444, testClientLaunchContext{})
	resp := request(agent.Handler(), http.MethodPost, "/send_keys", "tok", map[string]any{
		"keys": []string{"F5"}, "window": "class:ExplicitFrame",
		"client_target": map[string]any{
			"kind": "host-agent-testclient", "lifecycle_id": "launch-1", "pid": 4321, "port": 15444,
		},
	})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	if len(driver.targetWindows) != 1 || driver.targetWindows[0] != "client:4321:15444" {
		t.Fatalf("target windows = %#v", driver.targetWindows)
	}
}

func TestDisplayRequestExplicitWindowWithoutOwnedLifecycleNeverCallsDriver(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	resp := request(agent.Handler(), http.MethodPost, "/send_keys", "tok", map[string]any{
		"keys": []string{"F5"}, "window": "class:ExplicitFrame",
	})
	if resp.Code != http.StatusUnprocessableEntity {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	if len(driver.targetWindows) != 0 {
		t.Fatalf("target windows = %#v", driver.targetWindows)
	}
}

func TestDisplayRequestWildcardUsesValidatedClientTarget(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	target := recordOwnedDisplayTarget(agent)
	resp := request(agent.Handler(), http.MethodPost, "/send_keys", "tok", map[string]any{
		"keys": []string{"F5"}, "window": "*",
		"client_target": target,
	})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	if len(driver.targetWindows) != 1 || driver.targetWindows[0] != "client:4321:15444" {
		t.Fatalf("target windows = %#v", driver.targetWindows)
	}
}

func TestDisplayRequestMissingImplicitTargetNeverCallsDriver(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	resp := request(agent.Handler(), http.MethodPost, "/screenshot", "tok", map[string]any{"window": ""})
	if resp.Code != http.StatusUnprocessableEntity {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["error"] != "missing-client-target" || driver.screenshotCalls != 0 {
		t.Fatalf("payload=%#v screenshot_calls=%d", payload, driver.screenshotCalls)
	}
}

func TestDisplayRequestMismatchedOwnedTargetNeverCallsDriver(t *testing.T) {
	done := make(chan struct{})
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	agent.testClients.Record(&launchedTestClientProcess{
		PID: 4321, LifecycleID: "launch-1", Done: done, Terminate: func() error { return nil },
	}, 15444, testClientLaunchContext{})
	resp := request(agent.Handler(), http.MethodPost, "/send_keys", "tok", map[string]any{
		"keys": []string{"F5"},
		"client_target": map[string]any{
			"kind": "host-agent-testclient", "lifecycle_id": "launch-1", "pid": 9999, "port": 15444,
		},
	})
	if resp.Code != http.StatusUnprocessableEntity {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["error"] != "client-target-mismatch" || len(driver.targetWindows) != 0 {
		t.Fatalf("payload=%#v target_windows=%#v", payload, driver.targetWindows)
	}
}

func TestDisplayRequestsReportTypedDesktopSessionStatesBeforeDriver(t *testing.T) {
	states := []struct {
		state desktopSessionState
		code  string
	}{
		{desktopSessionLocked, "desktop-session-locked"},
		{desktopSessionDisconnected, "desktop-session-disconnected"},
		{desktopSessionNonInteractive, "desktop-session-noninteractive"},
	}
	for _, tc := range states {
		t.Run(tc.code, func(t *testing.T) {
			previous := desktopSessionProbe
			desktopSessionProbe = func() desktopSessionState { return tc.state }
			defer func() { desktopSessionProbe = previous }()
			driver := &fakeDriver{}
			agent := NewAgent(Config{Token: "tok"}, driver)
			target := recordOwnedDisplayTarget(agent)
			resp := request(agent.Handler(), http.MethodPost, "/send_keys", "tok", map[string]any{
				"keys": []string{"F5"}, "window": "class:V8TopLevelFrame", "client_target": target,
			})
			if resp.Code != http.StatusConflict {
				t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
			}
			var payload map[string]any
			if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
				t.Fatal(err)
			}
			if payload["error"] != tc.code || len(driver.targetWindows) != 0 {
				t.Fatalf("payload=%#v target_windows=%#v", payload, driver.targetWindows)
			}
		})
	}
}

func TestForegroundDeniedMapsToStructuredConflict(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{sendKeysToErr: ErrForegroundDenied})
	target := recordOwnedDisplayTarget(agent)
	resp := request(agent.Handler(), http.MethodPost, "/send_keys", "tok", map[string]any{
		"keys": []string{"ctrl+s"}, "window": "class:V8TopLevelFrame", "client_target": target,
	})
	if resp.Code != http.StatusConflict {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["ok"] != false || payload["error"] != "foreground-denied" {
		t.Fatalf("payload = %#v", payload)
	}
}

func TestScreenshotAndWindowList(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	target := recordOwnedDisplayTarget(agent)
	handler := agent.Handler()
	previous := clientTargetResolver
	clientTargetResolver = func(pid int, port int) (WindowInfo, error) {
		if pid != 4321 || port != 15444 {
			t.Fatalf("resolver args = %d, %d", pid, port)
		}
		return WindowInfo{HWND: "0x1", Title: "1C", Class: "V8TopLevelFrameSDI", PID: 4321, Visible: true}, nil
	}
	defer func() { clientTargetResolver = previous }()

	shot := request(handler, http.MethodPost, "/screenshot", "tok", map[string]any{
		"window": "1C", "client_target": target,
	})
	if shot.Code != http.StatusOK {
		t.Fatalf("screenshot status = %d body=%s", shot.Code, shot.Body.String())
	}
	if got := shot.Header().Get("Content-Type"); got != "image/png" {
		t.Fatalf("content-type = %q", got)
	}
	if !bytes.HasPrefix(shot.Body.Bytes(), []byte("\x89PNG\r\n\x1a\n")) {
		t.Fatalf("not a png")
	}

	windows := request(handler, http.MethodPost, "/window_list", "tok", map[string]any{
		"geometry": true, "client_target": target,
	})
	if windows.Code != http.StatusOK {
		t.Fatalf("window status = %d", windows.Code)
	}
}

func TestWindowListRequiresOwnedLifecycleBeforeResolution(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)
	resp := request(agent.Handler(), http.MethodPost, "/window_list", "tok", map[string]any{"geometry": true})
	if resp.Code != http.StatusUnprocessableEntity {
		t.Fatalf("window status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["error"] != "missing-client-target" || driver.windowListCalls != 0 {
		t.Fatalf("payload=%#v window_list_calls=%d", payload, driver.windowListCalls)
	}
}

func TestWindowListPreservesUTF8Titles(t *testing.T) {
	driver := &fakeDriver{windows: []WindowInfo{{
		HWND:     "0x42",
		Title:    "Клиент тестирования 3.1.5",
		Class:    "V8TopLevelFrameSDI",
		PID:      1234,
		Geometry: Rect{X: 1, Y: 2, Width: 3, Height: 4},
		Visible:  true,
	}}}
	agent := NewAgent(Config{Token: "tok"}, driver)
	target := recordOwnedDisplayTarget(agent)
	handler := agent.Handler()
	previous := clientTargetResolver
	clientTargetResolver = func(pid int, port int) (WindowInfo, error) {
		if pid != 4321 || port != 15444 {
			t.Fatalf("resolver args = %d, %d", pid, port)
		}
		return driver.windows[0], nil
	}
	defer func() { clientTargetResolver = previous }()

	resp := request(handler, http.MethodPost, "/window_list", "tok", map[string]any{
		"geometry": true, "client_target": target,
	})
	if resp.Code != http.StatusOK {
		t.Fatalf("window status = %d body=%s", resp.Code, resp.Body.String())
	}
	if got := resp.Header().Get("Content-Type"); !strings.Contains(strings.ToLower(got), "charset=utf-8") {
		t.Fatalf("content-type = %q, want utf-8 charset", got)
	}

	var payload struct {
		OK      bool         `json:"ok"`
		Windows []WindowInfo `json:"windows"`
	}
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatalf("decode response: %v", err)
	}
	if len(payload.Windows) != 1 {
		t.Fatalf("windows = %#v", payload.Windows)
	}
	if got := payload.Windows[0].Title; got != "Клиент тестирования 3.1.5" {
		t.Fatalf("title = %q", got)
	}
	if got := payload.Windows[0].Class; got != "V8TopLevelFrameSDI" {
		t.Fatalf("class = %q", got)
	}
	if strings.Contains(resp.Body.String(), "Ð") {
		t.Fatalf("response contains mojibake marker: %s", resp.Body.String())
	}
}

func TestVisibleListCellsRequiresAuth(t *testing.T) {
	driver := &fakeDriver{}
	agent := NewAgent(Config{Token: "tok"}, driver)

	resp := request(agent.Handler(), http.MethodPost, "/uia/visible_list_cells", "", map[string]any{"window": "class:V8TopLevelFrame"})
	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	if driver.visibleCalls != 0 {
		t.Fatalf("VisibleListCells called without auth")
	}
}

func TestVisibleListCellsReturnsTargetAndCells(t *testing.T) {
	driver := &fakeDriver{
		visibleTarget: WindowInfo{HWND: "0x77", Title: "Бухгалтерия предприятия, редакция 3.0", Class: "V8TopLevelFrameSDI", PID: 4321, Visible: true},
		visibleCells:  []string{"Российский рубль Наименование валюты", "643 Цифр. код", "руб. Симв. код"},
	}
	agent := NewAgent(Config{Token: "tok"}, driver)
	target := recordOwnedDisplayTarget(agent)

	resp := request(agent.Handler(), http.MethodPost, "/uia/visible_list_cells", "tok", map[string]any{
		"window":        "class:V8TopLevelFrame",
		"limit":         2,
		"client_target": target,
	})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload struct {
		OK     bool       `json:"ok"`
		Target WindowInfo `json:"target"`
		Count  int        `json:"count"`
		Cells  []string   `json:"cells"`
	}
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if !payload.OK || payload.Target.Class != "V8TopLevelFrameSDI" || payload.Count != 2 {
		t.Fatalf("payload = %#v", payload)
	}
	if len(payload.Cells) != 2 || payload.Cells[0] != "Российский рубль Наименование валюты" {
		t.Fatalf("cells = %#v", payload.Cells)
	}
}

func TestVisibleListCellsWindowNotFoundIsStructured(t *testing.T) {
	driver := &fakeDriver{visibleErr: ErrWindowNotFound}
	agent := NewAgent(Config{Token: "tok"}, driver)
	target := recordOwnedDisplayTarget(agent)

	resp := request(agent.Handler(), http.MethodPost, "/uia/visible_list_cells", "tok", map[string]any{
		"window": "class:V8TopLevelFrame", "client_target": target,
	})
	if resp.Code != http.StatusUnprocessableEntity {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["ok"] != false || payload["error"] != "window-not-found" {
		t.Fatalf("payload = %#v", payload)
	}
}

func TestTestClientLaunchRequiresAuthBeforeBodyValidation(t *testing.T) {
	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{t.TempDir()}}, &fakeDriver{})
	resp := rawRequest(agent.Handler(), http.MethodPost, "/testclient/launch", "", "{")
	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("unauthorized invalid-json status = %d body=%s", resp.Code, resp.Body.String())
	}
	resp = rawRequest(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", "{")
	if resp.Code != http.StatusBadRequest {
		t.Fatalf("authorized invalid-json status = %d body=%s", resp.Code, resp.Body.String())
	}
}

func TestTestClientLaunchRejectsInvalidTargetBeforeSpawn(t *testing.T) {
	root := t.TempDir()
	marker := filepath.Join(root, "spawned")
	writeFakePlatformBinary(t, root, "1cv8", `touch "`+marker+`"`)
	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{root}}, &fakeDriver{})

	resp := request(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", map[string]any{
		"port": 15381,
	})
	if resp.Code != http.StatusBadRequest {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	if !bytes.Contains(resp.Body.Bytes(), []byte("missing-target")) {
		t.Fatalf("missing target not reported: %s", resp.Body.String())
	}
	if _, err := os.Stat(marker); !os.IsNotExist(err) {
		t.Fatalf("invalid request spawned process, marker err=%v", err)
	}
}

func TestTestClientLaunchStartsDetachedAndRedactsSecrets(t *testing.T) {
	root := t.TempDir()
	marker := filepath.Join(root, "spawned")
	writeFakePlatformBinary(t, root, "1cv8", `
touch "`+marker+`"
port=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-TPort" ]; then
    shift
    port="$1"
  fi
  shift || true
done
python3 - "$port" <<'PY'
import socket
import sys
import time
port = int(sys.argv[1])
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", port))
sock.listen(1)
deadline = time.time() + 3
while time.time() < deadline:
    sock.settimeout(0.2)
    try:
        conn, _ = sock.accept()
        conn.close()
    except OSError:
        pass
PY
	`)
	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{root}}, &fakeDriver{})
	port := freeTCPPort(t)

	resp := request(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", map[string]any{
		"infobase_path":    "C:/Bases/vanessa_client",
		"platform_version": "8.3.27.2130",
		"user":             "Администратор",
		"password":         "supersecret",
		"port":             port,
	})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["ok"] != true || payload["response_id"] != "testclient-launch" || payload["password_set"] != true {
		t.Fatalf("payload = %#v", payload)
	}
	if payload["pid"] == nil || payload["reused_existing"] != false {
		t.Fatalf("pid/reuse payload = %#v", payload)
	}
	if payload["alive"] != true || payload["listening"] != true || payload["readiness"] != "ready" {
		t.Fatalf("readiness payload = %#v", payload)
	}
	body := resp.Body.String()
	if strings.Contains(body, "supersecret") {
		t.Fatalf("password leaked in response: %s", body)
	}
	if !strings.Contains(body, "[redacted-secret]") {
		t.Fatalf("redaction marker missing: %s", body)
	}
	deadline := time.Now().Add(2 * time.Second)
	for {
		if _, err := os.Stat(marker); err == nil {
			break
		}
		if time.Now().After(deadline) {
			t.Fatalf("detached fake TestClient did not run")
		}
		time.Sleep(20 * time.Millisecond)
	}
	if pid, ok := payload["pid"].(float64); ok && pid > 0 {
		if proc, err := os.FindProcess(int(pid)); err == nil {
			_ = proc.Kill()
			_, _ = proc.Wait()
		}
	}
}

func TestTestClientLaunchPinsRequestedPlatformVersion(t *testing.T) {
	root := t.TempDir()
	for _, version := range []string{"8.3.27.2130", "8.5.1.1302"} {
		binDir := filepath.Join(root, version, "bin")
		if err := os.MkdirAll(binDir, 0o755); err != nil {
			t.Fatal(err)
		}
		writeFakeCLI(t, binDir, "1cv8", "exit 0")
	}

	resolved, resolveErr := resolvePlatformExecutableVersion("1cv8", []string{root}, "8.3.27.2130")
	if resolveErr != nil {
		t.Fatalf("resolve error: %#v", resolveErr)
	}
	if resolved.Version != "8.3.27.2130" || !strings.Contains(resolved.Path, filepath.Join("8.3.27.2130", "bin")) {
		t.Fatalf("resolved wrong platform: %#v", resolved)
	}
}

func TestTestClientLaunchRejectsInvalidOrMissingRequestedPlatformVersion(t *testing.T) {
	for _, version := range []string{"", "   ", "8.3", "8.3.27.latest", "8.3.27.2130.1", "../8.3.27.2130"} {
		err := validateTestClientLaunch(testClientLaunchRequest{
			InfobasePath: "C:/Bases/demo10413", PlatformVersion: version, Port: 15381,
		})
		if err == nil || err.code != "invalid-platform-version" {
			t.Fatalf("version %q validation = %#v", version, err)
		}
	}
	_, resolveErr := resolvePlatformExecutableVersion("1cv8", []string{t.TempDir()}, "8.3.27.2130")
	if resolveErr == nil || resolveErr.code != "platform-version-not-found" {
		t.Fatalf("missing requested platform error = %#v", resolveErr)
	}
}

func TestTestClientLaunchContextRepairsScheduledTaskEnvironment(t *testing.T) {
	env, keys := testClientLaunchEnvironment([]string{
		`USERNAME=User`,
		`SystemRoot=C:\Windows`,
		`USERPROFILE=C:\Windows\System32\config\systemprofile`,
		`APPDATA=C:\Windows\System32\config\systemprofile\AppData\Roaming`,
		`LOCALAPPDATA=C:\Windows\System32\config\systemprofile\AppData\Local`,
		`TEMP=C:\Windows\Temp`,
		`PATH=C:\Windows\System32`,
	})
	values := map[string]string{}
	for _, item := range env {
		key, value, _ := strings.Cut(item, "=")
		values[strings.ToUpper(key)] = value
	}
	if values["USERPROFILE"] != `C:\Users\User` {
		t.Fatalf("USERPROFILE = %q", values["USERPROFILE"])
	}
	if values["APPDATA"] != `C:\Users\User\AppData\Roaming` {
		t.Fatalf("APPDATA = %q", values["APPDATA"])
	}
	if values["LOCALAPPDATA"] != `C:\Users\User\AppData\Local` {
		t.Fatalf("LOCALAPPDATA = %q", values["LOCALAPPDATA"])
	}
	if values["TEMP"] != `C:\Users\User\AppData\Local\Temp` || values["TMP"] != values["TEMP"] {
		t.Fatalf("temp values = TEMP:%q TMP:%q", values["TEMP"], values["TMP"])
	}
	joined := strings.Join(keys, ",")
	if !strings.Contains(joined, "USERPROFILE") || !strings.Contains(joined, "APPDATA") {
		t.Fatalf("launch context keys = %v", keys)
	}
}

func TestTestClientLaunchResultIncludesInteractiveSessionMetadata(t *testing.T) {
	sessionID := uint32(1)
	payload := testClientLaunchResult(
		nil,
		testClientLaunchRequest{InfobasePath: "C:/Bases/vanessa_client", Port: 15381},
		`File="C:/Bases/vanessa_client";`,
		platformExecutable{Path: `C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe`, Version: "8.3.27.2130"},
		nil,
		false,
		true,
		true,
		"ready",
		testClientLaunchContext{
			Method:    "interactive_session",
			SessionID: &sessionID,
			EnvKeys:   []string{"USERPROFILE", "APPDATA"},
		},
		"",
	)
	launchContext, ok := payload["launch_context"].(map[string]any)
	if !ok {
		t.Fatalf("launch_context missing from %#v", payload)
	}
	if launchContext["method"] != "interactive_session" {
		t.Fatalf("method = %#v", launchContext["method"])
	}
	if launchContext["session_id"] != uint32(1) {
		t.Fatalf("session_id = %#v", launchContext["session_id"])
	}
	keys, ok := launchContext["env_keys"].([]string)
	if !ok || strings.Join(keys, ",") != "APPDATA,USERPROFILE" {
		t.Fatalf("env_keys = %#v", launchContext["env_keys"])
	}
}

func TestTestClientLaunchContextFailureDoesNotFallbackToDirectExec(t *testing.T) {
	root := t.TempDir()
	marker := filepath.Join(root, "spawned")
	writeFakePlatformBinary(t, root, "1cv8", `touch "`+marker+`"`)
	sessionID := uint32(1)
	oldLauncher := testClientProcessLauncher
	testClientProcessLauncher = func(ctx context.Context, executable string, args []string, env []string, port int, ownerWaitTimeout time.Duration, launchContext testClientLaunchContext) (*launchedTestClientProcess, testClientLaunchContext, *testClientProcessStartError) {
		launchContext.Method = "interactive_session"
		launchContext.SessionID = &sessionID
		return nil, launchContext, &testClientProcessStartError{
			Status: http.StatusBadGateway,
			Code:   "testclient-interactive-session-unavailable",
			Detail: "active interactive session token unavailable",
		}
	}
	defer func() { testClientProcessLauncher = oldLauncher }()

	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{root}}, &fakeDriver{})
	resp := request(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", map[string]any{
		"infobase_path":    "C:/Bases/vanessa_client",
		"platform_version": "8.3.27.2130",
		"port":             freeTCPPort(t),
	})
	if resp.Code != http.StatusBadGateway {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["ok"] != false || payload["error"] != "testclient-interactive-session-unavailable" {
		t.Fatalf("payload = %#v", payload)
	}
	launchContext, ok := payload["launch_context"].(map[string]any)
	if !ok || launchContext["method"] != "interactive_session" {
		t.Fatalf("launch_context = %#v", payload["launch_context"])
	}
	if _, err := os.Stat(marker); !os.IsNotExist(err) {
		t.Fatalf("interactive-session failure fell back to direct exec, marker err=%v", err)
	}
}

func TestTestClientLaunchStartErrorPreservesEarlyExitMetadata(t *testing.T) {
	root := t.TempDir()
	writeFakePlatformBinary(t, root, "1cv8", `exit 7`)
	oldLauncher := testClientProcessLauncher
	var gotOwnerWaitTimeout time.Duration
	testClientProcessLauncher = func(ctx context.Context, executable string, args []string, env []string, port int, ownerWaitTimeout time.Duration, launchContext testClientLaunchContext) (*launchedTestClientProcess, testClientLaunchContext, *testClientProcessStartError) {
		gotOwnerWaitTimeout = ownerWaitTimeout
		launchContext.Method = interactiveTaskShellBrokerMethod
		pid := 4510
		return nil, launchContext, &testClientProcessStartError{
			Status:    http.StatusBadGateway,
			Code:      "testclient-exited-early",
			Detail:    "acknowledged TestClient process exited before TPort ownership appeared",
			PID:       &pid,
			Alive:     false,
			Listening: false,
			Readiness: "exited_early",
		}
	}
	defer func() { testClientProcessLauncher = oldLauncher }()

	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{root}}, &fakeDriver{})
	resp := request(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", map[string]any{
		"infobase_path":    "C:/Bases/disposable",
		"platform_version": "8.3.27.2130",
		"port":             freeTCPPort(t),
		"timeout_seconds":  7,
	})
	if resp.Code != http.StatusBadGateway {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["error"] != "testclient-exited-early" || payload["pid"] != float64(4510) {
		t.Fatalf("typed early-exit payload = %#v", payload)
	}
	if payload["alive"] != false || payload["listening"] != false || payload["readiness"] != "exited_early" {
		t.Fatalf("bounded early-exit metadata = %#v", payload)
	}
	if payload["owns_process"] != false || payload["lifecycle_handle"] != nil {
		t.Fatalf("failed start claimed lifecycle ownership: %#v", payload)
	}
	if gotOwnerWaitTimeout != 7*time.Second {
		t.Fatalf("owner wait timeout = %v, want caller-bounded 7s", gotOwnerWaitTimeout)
	}
}

func TestTestClientLaunchReportsEarlyExitInsteadOfReady(t *testing.T) {
	root := t.TempDir()
	writeFakePlatformBinary(t, root, "1cv8", `exit 7`)
	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{root}}, &fakeDriver{})
	port := freeTCPPort(t)

	resp := request(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", map[string]any{
		"infobase_path":    "C:/Bases/vanessa_client",
		"platform_version": "8.3.27.2130",
		"port":             port,
		"timeout_seconds":  1,
	})
	if resp.Code != http.StatusBadGateway {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["ok"] != false || payload["error"] != "testclient-exited-early" {
		t.Fatalf("payload = %#v", payload)
	}
	if payload["listening"] != false || payload["alive"] != false || payload["readiness"] == "ready" {
		t.Fatalf("readiness payload = %#v", payload)
	}
}

func TestTestClientReadinessDoesNotTreatListeningPortAsAliveAfterExit(t *testing.T) {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer ln.Close()
	_, portText, err := net.SplitHostPort(ln.Addr().String())
	if err != nil {
		t.Fatal(err)
	}
	port, err := strconv.Atoi(portText)
	if err != nil {
		t.Fatal(err)
	}
	done := make(chan struct{})
	close(done)
	if got := waitForTestClientReadiness(context.Background(), done, port, time.Second); got != "exited_early" {
		t.Fatalf("readiness = %q, want exited_early", got)
	}
}

func TestTestClientReadinessRequiresPortPersistenceDwell(t *testing.T) {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	_, portText, err := net.SplitHostPort(ln.Addr().String())
	if err != nil {
		t.Fatal(err)
	}
	port, err := strconv.Atoi(portText)
	if err != nil {
		t.Fatal(err)
	}
	done := make(chan struct{})
	errCh := make(chan error, 1)
	go func() {
		defer close(done)
		tcpLn, ok := ln.(*net.TCPListener)
		if !ok {
			errCh <- fmt.Errorf("listener is %T, want *net.TCPListener", ln)
			return
		}
		deadline := time.Now().Add(220 * time.Millisecond)
		for time.Now().Before(deadline) {
			_ = tcpLn.SetDeadline(time.Now().Add(20 * time.Millisecond))
			if conn, err := ln.Accept(); err == nil {
				_ = conn.Close()
			}
		}
		_ = ln.Close()
	}()

	if got := waitForTestClientReadiness(context.Background(), done, port, time.Second); got != "exited_early" {
		t.Fatalf("readiness = %q, want exited_early", got)
	}
	select {
	case err := <-errCh:
		t.Fatal(err)
	default:
	}
}

func TestTestClientReadinessDwellHonorsLaunchTimeout(t *testing.T) {
	ln, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer ln.Close()
	_, portText, err := net.SplitHostPort(ln.Addr().String())
	if err != nil {
		t.Fatal(err)
	}
	port, err := strconv.Atoi(portText)
	if err != nil {
		t.Fatal(err)
	}
	stopAccept := make(chan struct{})
	acceptDone := make(chan struct{})
	go func() {
		defer close(acceptDone)
		tcpLn, ok := ln.(*net.TCPListener)
		if !ok {
			return
		}
		for {
			_ = tcpLn.SetDeadline(time.Now().Add(20 * time.Millisecond))
			conn, err := ln.Accept()
			if err != nil {
				select {
				case <-stopAccept:
					return
				default:
					continue
				}
			}
			_ = conn.Close()
		}
	}()
	processDone := make(chan struct{})

	start := time.Now()
	got := waitForTestClientReadiness(context.Background(), processDone, port, 200*time.Millisecond)
	elapsed := time.Since(start)
	close(stopAccept)
	_ = ln.Close()
	<-acceptDone
	if got != "not_listening" {
		t.Fatalf("readiness = %q, want not_listening", got)
	}
	if elapsed > time.Second {
		t.Fatalf("readiness wait exceeded bounded timeout: %s", elapsed)
	}
}

func TestTestClientLaunchReportsNotListeningProcessInsteadOfReady(t *testing.T) {
	root := t.TempDir()
	writeFakePlatformBinary(t, root, "1cv8", `sleep 3`)
	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{root}}, &fakeDriver{})
	port := freeTCPPort(t)
	var pid int

	resp := request(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", map[string]any{
		"infobase_path":    "C:/Bases/vanessa_client",
		"platform_version": "8.3.27.2130",
		"port":             port,
		"timeout_seconds":  1,
	})
	if resp.Code != http.StatusGatewayTimeout {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["ok"] != false || payload["error"] != "testclient-not-listening" {
		t.Fatalf("payload = %#v", payload)
	}
	if payload["alive"] != true || payload["listening"] != false || payload["readiness"] == "ready" {
		t.Fatalf("readiness payload = %#v", payload)
	}
	if payload["owns_process"] != true {
		t.Fatalf("not-listening launch did not retain owned cleanup handle: %#v", payload)
	}
	handle, ok := payload["lifecycle_handle"].(map[string]any)
	handleID, _ := handle["id"].(string)
	if !ok || handle["kind"] != "host-agent-testclient" || strings.TrimSpace(handleID) == "" {
		t.Fatalf("not-listening launch handle = %#v", payload["lifecycle_handle"])
	}
	if value, ok := payload["pid"].(float64); ok && value > 0 {
		pid = int(value)
		defer func() {
			if !testClientProcessAlive(pid) {
				return
			}
			if proc, err := os.FindProcess(pid); err == nil {
				_ = proc.Kill()
				_, _ = proc.Wait()
			}
		}()
	} else {
		t.Fatalf("not-listening launch did not return a positive pid: %#v", payload)
	}

	stop := request(agent.Handler(), http.MethodPost, "/testclient/stop", "tok", map[string]any{"pid": pid, "port": port, "lifecycle_handle": handle})
	if stop.Code != http.StatusOK {
		t.Fatalf("stop status = %d body=%s", stop.Code, stop.Body.String())
	}
	var stopPayload map[string]any
	if err := json.Unmarshal(stop.Body.Bytes(), &stopPayload); err != nil {
		t.Fatal(err)
	}
	if stopPayload["state"] != "stopped" || stopPayload["stopped"] != true || stopPayload["refused"] != false {
		t.Fatalf("not-listening stop payload = %#v", stopPayload)
	}
	if testClientProcessAlive(pid) {
		t.Fatalf("owned not-listening TestClient pid %d is still alive after stop", pid)
	}
}

func TestTestClientLaunchReportsReadyOnlyWhenProcessAndPortLive(t *testing.T) {
	root := t.TempDir()
	writeFakePlatformBinary(t, root, "1cv8", `
port=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-TPort" ]; then
    shift
    port="$1"
  fi
  shift || true
done
python3 - "$port" <<'PY'
import socket
import sys
import time
port = int(sys.argv[1])
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", port))
sock.listen(1)
deadline = time.time() + 3
while time.time() < deadline:
    sock.settimeout(0.2)
    try:
        conn, _ = sock.accept()
        conn.close()
    except OSError:
        pass
PY
`)
	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{root}}, &fakeDriver{})
	port := freeTCPPort(t)

	resp := request(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", map[string]any{
		"infobase_path":    "C:/Bases/vanessa_client",
		"platform_version": "8.3.27.2130",
		"port":             port,
		"timeout_seconds":  2,
	})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["ok"] != true || payload["alive"] != true || payload["listening"] != true || payload["readiness"] != "ready" {
		t.Fatalf("payload = %#v", payload)
	}
	if pid, ok := payload["pid"].(float64); ok && pid > 0 {
		if proc, err := os.FindProcess(int(pid)); err == nil {
			_ = proc.Kill()
			_, _ = proc.Wait()
		}
	}
}

func TestTestClientStopStopsOwnedLaunchAndIsIdempotent(t *testing.T) {
	root := t.TempDir()
	writeFakePlatformBinary(t, root, "1cv8", `
port=""
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-TPort" ]; then
    shift
    port="$1"
  fi
  shift || true
done
python3 - "$port" <<'PY'
import socket
import sys
import time
port = int(sys.argv[1])
sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", port))
sock.listen(1)
deadline = time.time() + 30
while time.time() < deadline:
    sock.settimeout(0.2)
    try:
        conn, _ = sock.accept()
        conn.close()
    except OSError:
        pass
PY
`)
	agent := NewAgent(Config{Token: "tok", PlatformCatalogRoots: []string{root}}, &fakeDriver{})
	port := freeTCPPort(t)

	launch := request(agent.Handler(), http.MethodPost, "/testclient/launch", "tok", map[string]any{
		"infobase_path":    "C:/Bases/vanessa_client",
		"platform_version": "8.3.27.2130",
		"port":             port,
		"timeout_seconds":  2,
	})
	if launch.Code != http.StatusOK {
		t.Fatalf("launch status = %d body=%s", launch.Code, launch.Body.String())
	}
	var launchPayload map[string]any
	if err := json.Unmarshal(launch.Body.Bytes(), &launchPayload); err != nil {
		t.Fatal(err)
	}
	pid := int(launchPayload["pid"].(float64))
	if launchPayload["owns_process"] != true {
		t.Fatalf("launch did not report owned process: %#v", launchPayload)
	}
	handle, ok := launchPayload["lifecycle_handle"].(map[string]any)
	handleID, _ := handle["id"].(string)
	if !ok || handle["kind"] != "host-agent-testclient" || strings.TrimSpace(handleID) == "" {
		t.Fatalf("launch handle = %#v", launchPayload["lifecycle_handle"])
	}

	stop := request(agent.Handler(), http.MethodPost, "/testclient/stop", "tok", map[string]any{"pid": pid, "lifecycle_handle": handle})
	if stop.Code != http.StatusOK {
		t.Fatalf("stop status = %d body=%s", stop.Code, stop.Body.String())
	}
	var stopPayload map[string]any
	if err := json.Unmarshal(stop.Body.Bytes(), &stopPayload); err != nil {
		t.Fatal(err)
	}
	if stopPayload["state"] != "stopped" || stopPayload["stopped"] != true || stopPayload["refused"] != false {
		t.Fatalf("stop payload = %#v", stopPayload)
	}
	if testClientProcessAlive(pid) {
		t.Fatalf("owned TestClient pid %d is still alive after stop", pid)
	}

	again := request(agent.Handler(), http.MethodPost, "/testclient/stop", "tok", map[string]any{"pid": pid, "lifecycle_handle": handle})
	if again.Code != http.StatusOK {
		t.Fatalf("repeat stop status = %d body=%s", again.Code, again.Body.String())
	}
	stopPayload = map[string]any{}
	if err := json.Unmarshal(again.Body.Bytes(), &stopPayload); err != nil {
		t.Fatal(err)
	}
	if stopPayload["state"] != "already_stopped" || stopPayload["refused"] != false {
		t.Fatalf("repeat stop payload = %#v", stopPayload)
	}
}

func TestTestClientStopRefusesUnknownPIDWithoutKilling(t *testing.T) {
	proc, err := os.StartProcess("/bin/sh", []string{"sh", "-c", "sleep 30"}, &os.ProcAttr{
		Files: []*os.File{nil, nil, nil},
	})
	if err != nil {
		t.Fatal(err)
	}
	defer func() {
		_ = proc.Kill()
		_, _ = proc.Wait()
	}()
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})

	resp := request(agent.Handler(), http.MethodPost, "/testclient/stop", "tok", map[string]any{"pid": proc.Pid})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["state"] != "not_owned" || payload["stopped"] != false || payload["refused"] != true {
		t.Fatalf("payload = %#v", payload)
	}
	if !testClientProcessAlive(proc.Pid) {
		t.Fatalf("unknown pid %d was killed by refusal path", proc.Pid)
	}
}

func TestTestClientStopTreatsCompletedRecordAsStaleWithoutKilling(t *testing.T) {
	unrelated := exec.Command("sh", "-c", "sleep 30")
	if err := unrelated.Start(); err != nil {
		t.Fatal(err)
	}
	unrelatedDone := make(chan error, 1)
	go func() {
		unrelatedDone <- unrelated.Wait()
	}()
	waitConsumed := false
	defer func() {
		if testClientProcessAlive(unrelated.Process.Pid) {
			_ = unrelated.Process.Kill()
		}
		if !waitConsumed {
			<-unrelatedDone
		}
	}()

	done := make(chan struct{})
	close(done)
	store := newTestClientLifecycleStore()
	lifecycleID := "completed-lifecycle"
	store.Record(
		&launchedTestClientProcess{
			PID:         unrelated.Process.Pid,
			LifecycleID: lifecycleID,
			Done:        done,
			Terminate: func() error {
				return unrelated.Process.Kill()
			},
		},
		15444,
		testClientLaunchContext{},
	)

	result := store.Stop(unrelated.Process.Pid, 15444, lifecycleID)
	if result["state"] != "already_stopped" || result["stopped"] != false || result["reason"] != "process_exited" {
		t.Fatalf("stale stop result = %#v", result)
	}
	select {
	case waitErr := <-unrelatedDone:
		waitConsumed = true
		t.Fatalf("stale lifecycle record killed unrelated reused PID; wait=%v stop result=%#v", waitErr, result)
	default:
	}
}

func TestTestClientStopUsesLifecycleIDAcrossPIDReuse(t *testing.T) {
	store := newTestClientLifecycleStore()
	reusedPID := 4242
	oldDone := make(chan struct{})
	close(oldDone)
	newDone := make(chan struct{})
	newTerminated := false

	store.Record(
		&launchedTestClientProcess{
			PID:         reusedPID,
			LifecycleID: "old-lifecycle",
			Done:        oldDone,
			Terminate: func() error {
				t.Fatal("old finalized lifecycle must not terminate during record setup")
				return nil
			},
		},
		15553,
		testClientLaunchContext{},
	)
	store.Record(
		&launchedTestClientProcess{
			PID:         reusedPID,
			LifecycleID: "new-lifecycle",
			Done:        newDone,
			Terminate: func() error {
				newTerminated = true
				close(newDone)
				return nil
			},
		},
		15554,
		testClientLaunchContext{},
	)

	oldResult := store.Stop(reusedPID, 15553, "old-lifecycle")
	if oldResult["state"] != "already_stopped" || oldResult["reason"] != "process_exited" || oldResult["refused"] != false {
		t.Fatalf("old lifecycle stop result = %#v", oldResult)
	}
	if newTerminated {
		t.Fatalf("old lifecycle stop terminated a newer same-PID record")
	}

	missingHandle := store.Stop(reusedPID, 15554, "")
	if missingHandle["state"] != "not_owned" || missingHandle["reason"] != "missing_lifecycle_handle" || missingHandle["refused"] != true {
		t.Fatalf("missing-handle stop result = %#v", missingHandle)
	}
	if newTerminated {
		t.Fatalf("PID-only stop terminated a lifecycle-protected same-PID record")
	}

	newResult := store.Stop(reusedPID, 15554, "new-lifecycle")
	if newResult["state"] != "stopped" || newResult["stopped"] != true || newResult["refused"] != false {
		t.Fatalf("new lifecycle stop result = %#v", newResult)
	}
	if !newTerminated {
		t.Fatalf("new lifecycle stop did not terminate the matching record")
	}
}

func TestTestClientStopRejectsMismatchedLifecycleIDs(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	resp := request(agent.Handler(), http.MethodPost, "/testclient/stop", "tok", map[string]any{
		"pid":          1234,
		"lifecycle_id": "top-level",
		"lifecycle_handle": map[string]any{
			"kind": "host-agent-testclient",
			"id":   "nested",
			"pid":  1234,
		},
	})
	if resp.Code != http.StatusBadRequest {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["error"] != "invalid-lifecycle-handle" {
		t.Fatalf("payload = %#v", payload)
	}
}

func TestTestClientStopRequiresAuth(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	resp := request(agent.Handler(), http.MethodPost, "/testclient/stop", "", map[string]any{"pid": 1234})
	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
}

func TestTestClientStatusReportsPIDLiveness(t *testing.T) {
	proc, err := os.StartProcess("/bin/sh", []string{"sh", "-c", "sleep 3"}, &os.ProcAttr{
		Files: []*os.File{nil, nil, nil},
	})
	if err != nil {
		t.Fatal(err)
	}
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})

	resp := request(agent.Handler(), http.MethodPost, "/testclient/status", "tok", map[string]any{"pid": proc.Pid})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["alive"] != true {
		t.Fatalf("alive status = %#v", payload)
	}

	_ = proc.Kill()
	_, _ = proc.Wait()
	resp = request(agent.Handler(), http.MethodPost, "/testclient/status", "tok", map[string]any{"pid": proc.Pid})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	payload = map[string]any{}
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["alive"] != false {
		t.Fatalf("dead status = %#v", payload)
	}
}

func TestTestClientStatusReturnsBoundedAttachTarget(t *testing.T) {
	previous := clientTargetResolver
	clientTargetResolver = func(pid int, port int) (WindowInfo, error) {
		if pid != 0 || port != 15444 {
			t.Fatalf("resolver args = %d, %d", pid, port)
		}
		return WindowInfo{HWND: "0x77", Title: "", Class: "V8TopLevelFrameSDI", PID: 4321, Visible: true}, nil
	}
	defer func() { clientTargetResolver = previous }()

	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	resp := request(agent.Handler(), http.MethodPost, "/testclient/status", "tok", map[string]any{"port": 15444})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	target, ok := payload["client_target"].(map[string]any)
	if !ok || target["kind"] != "host-agent-testclient" || target["pid"] != float64(4321) || target["port"] != float64(15444) {
		t.Fatalf("target = %#v", payload["client_target"])
	}
	if payload["window_bound"] != true || payload["window_title_empty"] != true || payload["window_class_1c"] != true {
		t.Fatalf("payload = %#v", payload)
	}
	if _, leaked := target["hwnd"]; leaked {
		t.Fatalf("target leaked window handle: %#v", target)
	}
}

func TestTestClientStatusReturnsOwnedLifecycleTargetForBootstrapAttach(t *testing.T) {
	previous := clientTargetResolver
	clientTargetResolver = func(pid int, port int) (WindowInfo, error) {
		return WindowInfo{PID: 4321, Class: "V8TopLevelFrameSDI", Visible: true}, nil
	}
	defer func() { clientTargetResolver = previous }()

	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	recordOwnedDisplayTarget(agent)
	resp := request(agent.Handler(), http.MethodPost, "/testclient/status", "tok", map[string]any{"port": 15444})
	if resp.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	var payload map[string]any
	if err := json.Unmarshal(resp.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	target := payload["client_target"].(map[string]any)
	if target["lifecycle_id"] != "launch-1" || payload["lifecycle_owner"] != "host-agent" {
		t.Fatalf("payload = %#v", payload)
	}
}

func TestTestClientStatusRequiresAuth(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	resp := request(agent.Handler(), http.MethodPost, "/testclient/status", "", map[string]any{"port": 15381})
	if resp.Code != http.StatusUnauthorized {
		t.Fatalf("status = %d body=%s", resp.Code, resp.Body.String())
	}
	resp = request(agent.Handler(), http.MethodPost, "/testclient/status", "tok", map[string]any{"port": 15381})
	if resp.Code != http.StatusOK {
		t.Fatalf("authorized status = %d body=%s", resp.Code, resp.Body.String())
	}
}
