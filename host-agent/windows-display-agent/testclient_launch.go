package main

import (
	"context"
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"net/http"
	"os"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

const (
	defaultTestClientLaunchTimeout   = 30 * time.Second
	maxTestClientLaunchTimeout       = 120 * time.Second
	testClientReadinessDwell         = 500 * time.Millisecond
	testClientReadinessPoll          = 100 * time.Millisecond
	testClientReadinessProbe         = 50 * time.Millisecond
	testClientStopTimeout            = 5 * time.Second
	interactiveTaskShellBrokerMethod = "interactive_task_shell_broker"
)

type testClientLaunchRequest struct {
	InfobasePath     string  `json:"infobase_path"`
	ConnectionString string  `json:"connection_string"`
	User             string  `json:"user"`
	Password         string  `json:"password"`
	PlatformVersion  string  `json:"platform_version"`
	UseHWLicenses    bool    `json:"use_hardware_licenses"`
	Port             int     `json:"port"`
	TimeoutSeconds   float64 `json:"timeout_seconds"`
}

type testClientStatusRequest struct {
	PID  int `json:"pid"`
	Port int `json:"port"`
}

type testClientLifecycleHandle struct {
	Kind string `json:"kind"`
	ID   string `json:"id"`
	PID  int    `json:"pid"`
	Port int    `json:"port"`
}

type testClientStopRequest struct {
	PID             int                        `json:"pid"`
	Port            int                        `json:"port"`
	LifecycleID     string                     `json:"lifecycle_id"`
	LifecycleHandle *testClientLifecycleHandle `json:"lifecycle_handle"`
}

type testClientLaunchError struct {
	status int
	code   string
	detail string
	fields map[string]any
}

type testClientLaunchContext struct {
	Method    string
	SessionID *uint32
	EnvKeys   []string
}

type launchedTestClientProcess struct {
	PID         int
	LifecycleID string
	Done        <-chan struct{}
	Terminate   func() error
}

type ownedTestClientRecord struct {
	PID           int
	Port          int
	LifecycleID   string
	Done          <-chan struct{}
	Terminate     func() error
	LaunchContext testClientLaunchContext
	Finalized     bool
	FinalReason   string
}

type testClientLifecycleStore struct {
	mu          sync.Mutex
	recordsByID map[string]*ownedTestClientRecord
}

func newTestClientLifecycleStore() *testClientLifecycleStore {
	return &testClientLifecycleStore{recordsByID: map[string]*ownedTestClientRecord{}}
}

func (store *testClientLifecycleStore) Record(process *launchedTestClientProcess, port int, launchContext testClientLaunchContext) {
	if store == nil || process == nil || process.PID <= 0 || process.Done == nil || process.Terminate == nil {
		return
	}
	lifecycleID := strings.TrimSpace(process.LifecycleID)
	if lifecycleID == "" {
		lifecycleID = newTestClientLifecycleID()
		process.LifecycleID = lifecycleID
	}
	store.mu.Lock()
	defer store.mu.Unlock()
	store.recordsByID[lifecycleID] = &ownedTestClientRecord{
		PID:           process.PID,
		Port:          port,
		LifecycleID:   lifecycleID,
		Done:          process.Done,
		Terminate:     process.Terminate,
		LaunchContext: launchContext,
	}
}

func (store *testClientLifecycleStore) ValidateDisplayTarget(target clientTarget) error {
	if store == nil || strings.TrimSpace(target.LifecycleID) == "" {
		return ErrClientTargetStale
	}
	store.mu.Lock()
	defer store.mu.Unlock()
	record := store.recordsByID[strings.TrimSpace(target.LifecycleID)]
	if record == nil || record.Finalized || testClientProcessDone(record.Done) {
		return ErrClientTargetStale
	}
	if record.PID != target.PID || record.Port != target.Port {
		return ErrClientTargetMismatch
	}
	return nil
}

func (store *testClientLifecycleStore) OwnedDisplayTarget(pid int, port int) (clientTarget, bool) {
	if store == nil || !validTCPPort(port) {
		return clientTarget{}, false
	}
	store.mu.Lock()
	defer store.mu.Unlock()
	var matched *ownedTestClientRecord
	for _, record := range store.recordsByID {
		if record == nil || record.Finalized || testClientProcessDone(record.Done) || record.Port != port {
			continue
		}
		if pid > 0 && record.PID != pid {
			continue
		}
		if matched != nil {
			return clientTarget{}, false
		}
		matched = record
	}
	if matched == nil {
		return clientTarget{}, false
	}
	return clientTarget{
		Kind: "host-agent-testclient", LifecycleID: matched.LifecycleID, PID: matched.PID, Port: matched.Port,
	}, true
}

func (store *testClientLifecycleStore) Stop(pid int, port int, lifecycleID string) map[string]any {
	lifecycleID = strings.TrimSpace(lifecycleID)
	if store == nil {
		return testClientStopResult(pid, port, lifecycleID, "not_owned", false, true, "not_owned", false, testClientLaunchContext{})
	}
	if lifecycleID == "" {
		return testClientStopResult(pid, port, lifecycleID, "not_owned", false, true, "missing_lifecycle_handle", testClientProcessAlive(pid), testClientLaunchContext{})
	}
	store.mu.Lock()
	defer store.mu.Unlock()
	record := store.recordsByID[lifecycleID]
	if record == nil {
		return testClientStopResult(pid, port, lifecycleID, "not_owned", false, true, "stale_lifecycle_handle", testClientProcessAlive(pid), testClientLaunchContext{})
	}
	if pid != 0 && record.PID != pid {
		return testClientStopResult(pid, port, lifecycleID, "not_owned", false, true, "pid_mismatch", testClientProcessAlive(pid), record.LaunchContext)
	}
	if port != 0 && record.Port != port {
		return testClientStopResult(record.PID, port, lifecycleID, "not_owned", false, true, "port_mismatch", testClientProcessAlive(record.PID), record.LaunchContext)
	}
	if record.Finalized {
		return testClientStopResult(record.PID, record.Port, lifecycleID, "already_stopped", false, false, record.FinalReason, false, record.LaunchContext)
	}
	if testClientProcessDone(record.Done) {
		record.Finalized = true
		record.FinalReason = "process_exited"
		return testClientStopResult(record.PID, record.Port, lifecycleID, "already_stopped", false, false, record.FinalReason, false, record.LaunchContext)
	}

	if record.Terminate == nil {
		record.Finalized = true
		record.FinalReason = "process_handle_unavailable"
		return testClientStopResult(record.PID, record.Port, lifecycleID, "already_stopped", false, false, record.FinalReason, false, record.LaunchContext)
	}
	if err := record.Terminate(); err != nil && !testClientProcessDone(record.Done) {
		return testClientStopResult(record.PID, record.Port, lifecycleID, "stop_failed", false, false, "terminate_failed", testClientProcessAlive(record.PID), record.LaunchContext)
	}
	done := waitForOwnedTestClientDone(record.Done, testClientStopTimeout)
	alive := testClientProcessAlive(record.PID)
	if done || !alive {
		record.Finalized = true
		record.FinalReason = "stopped"
		return testClientStopResult(record.PID, record.Port, lifecycleID, "stopped", true, false, "stopped", false, record.LaunchContext)
	}
	return testClientStopResult(record.PID, record.Port, lifecycleID, "stop_failed", false, false, "still_alive", true, record.LaunchContext)
}

func newTestClientLifecycleID() string {
	random := make([]byte, 18)
	if _, err := rand.Read(random); err == nil {
		return base64.RawURLEncoding.EncodeToString(random)
	}
	return strconv.FormatInt(time.Now().UnixNano(), 36)
}

func testClientProcessDone(done <-chan struct{}) bool {
	if done == nil {
		return false
	}
	select {
	case <-done:
		return true
	default:
		return false
	}
}

func waitForOwnedTestClientDone(done <-chan struct{}, timeout time.Duration) bool {
	if done == nil {
		return false
	}
	if testClientProcessDone(done) {
		return true
	}
	timer := time.NewTimer(timeout)
	defer timer.Stop()
	select {
	case <-done:
		return true
	case <-timer.C:
		return false
	}
}

func testClientStopResult(
	pid int,
	port int,
	lifecycleID string,
	state string,
	stopped bool,
	refused bool,
	reason string,
	alive bool,
	launchContext testClientLaunchContext,
) map[string]any {
	payload := map[string]any{
		"ok":              true,
		"response_id":     "testclient-stop",
		"pid":             pid,
		"port":            port,
		"state":           state,
		"stopped":         stopped,
		"refused":         refused,
		"reason":          reason,
		"alive":           alive,
		"lifecycle_owner": "host-agent",
	}
	if strings.TrimSpace(lifecycleID) != "" {
		payload["lifecycle_id"] = strings.TrimSpace(lifecycleID)
		payload["lifecycle_handle"] = map[string]any{
			"kind": "host-agent-testclient",
			"id":   strings.TrimSpace(lifecycleID),
			"pid":  pid,
			"port": port,
		}
	}
	if state != "not_owned" && port != 0 {
		payload["listening"] = testClientPortListening(port, 250*time.Millisecond)
	}
	launchContextPayload := testClientLaunchContextPayload(launchContext)
	if len(launchContextPayload) > 0 {
		payload["launch_context"] = launchContextPayload
	}
	return payload
}

type testClientProcessStartError struct {
	Status    int
	Code      string
	Detail    string
	PID       *int
	Alive     any
	Listening bool
	Readiness string
}

type testClientProcessLauncherFunc func(
	ctx context.Context,
	executable string,
	args []string,
	env []string,
	port int,
	ownerWaitTimeout time.Duration,
	launchContext testClientLaunchContext,
) (*launchedTestClientProcess, testClientLaunchContext, *testClientProcessStartError)

var testClientProcessLauncher testClientProcessLauncherFunc = startTestClientProcess

func (a *Agent) handleTestClientLaunch(w http.ResponseWriter, r *http.Request) {
	var req testClientLaunchRequest
	if !decodeJSON(w, r, &req) {
		return
	}
	result, process, launchContext, launchErr := launchHostTestClient(r.Context(), req, a.config.PlatformCatalogRoots)
	a.testClients.Record(process, req.Port, launchContext)
	if launchErr != nil {
		writeTestClientLaunchError(w, launchErr)
		return
	}
	writeJSON(w, http.StatusOK, result)
}

func (a *Agent) handleTestClientStatus(w http.ResponseWriter, r *http.Request) {
	var req testClientStatusRequest
	if !decodeJSON(w, r, &req) {
		return
	}
	if req.Port != 0 && !validTCPPort(req.Port) {
		writeError(w, http.StatusBadRequest, "invalid-port", "port must be between 1 and 65535")
		return
	}
	alive := any(nil)
	if req.PID > 0 {
		alive = testClientProcessAlive(req.PID)
	}
	payload := map[string]any{
		"ok":        true,
		"pid":       nullablePID(req.PID),
		"port":      req.Port,
		"listening": req.Port != 0 && testClientPortListening(req.Port, 500*time.Millisecond),
		"alive":     alive,
		"host":      "127.0.0.1",
	}
	if req.Port > 0 {
		info, err := clientTargetResolver(req.PID, req.Port)
		if err == nil && info.PID == 0 {
			err = ErrClientTargetInvalid
		}
		if err == nil && info.PID > 0 {
			target := map[string]any{
				"kind": "host-agent-testclient",
				"pid":  int(info.PID),
				"port": req.Port,
			}
			if owned, ok := a.testClients.OwnedDisplayTarget(int(info.PID), req.Port); ok {
				target["lifecycle_id"] = owned.LifecycleID
				payload["lifecycle_owner"] = "host-agent"
			}
			payload["client_target"] = target
			payload["window_bound"] = true
			payload["window_title_empty"] = strings.TrimSpace(info.Title) == ""
			payload["window_class_1c"] = strings.HasPrefix(strings.ToLower(info.Class), "v8toplevelframe")
		} else {
			payload["client_target_error"] = errorCode(err)
			payload["window_bound"] = false
		}
	}
	writeJSON(w, http.StatusOK, payload)
}

func (a *Agent) handleTestClientStop(w http.ResponseWriter, r *http.Request) {
	var req testClientStopRequest
	if !decodeJSON(w, r, &req) {
		return
	}
	pid := req.requestedPID()
	if pid <= 0 {
		writeError(w, http.StatusBadRequest, "invalid-pid", "pid must be a positive process id")
		return
	}
	port := req.requestedPort()
	if port != 0 && !validTCPPort(port) {
		writeError(w, http.StatusBadRequest, "invalid-port", "port must be between 1 and 65535")
		return
	}
	if req.lifecycleIDMismatch() {
		writeError(w, http.StatusBadRequest, "invalid-lifecycle-handle", "lifecycle_id must match lifecycle_handle.id")
		return
	}
	writeJSON(w, http.StatusOK, a.testClients.Stop(pid, port, req.requestedLifecycleID()))
}

func writeTestClientLaunchError(w http.ResponseWriter, launchErr *testClientLaunchError) {
	payload := map[string]any{"ok": false, "status": launchErr.status, "error": launchErr.code, "detail": launchErr.detail}
	for key, value := range launchErr.fields {
		payload[key] = value
	}
	writeJSON(w, launchErr.status, payload)
}

func launchHostTestClient(ctx context.Context, req testClientLaunchRequest, roots []string) (map[string]any, *launchedTestClientProcess, testClientLaunchContext, *testClientLaunchError) {
	if err := validateTestClientLaunch(req); err != nil {
		return nil, nil, testClientLaunchContext{}, err
	}
	connection := testClientConnectionString(req)
	if testClientPortListening(req.Port, 250*time.Millisecond) {
		return testClientLaunchResult(nil, req, connection, platformExecutable{}, nil, true, true, nil, "ready", testClientLaunchContext{}, ""), nil, testClientLaunchContext{}, nil
	}

	resolved, platformErr := resolvePlatformExecutableVersion("1cv8", roots, req.PlatformVersion)
	if platformErr != nil {
		return nil, nil, testClientLaunchContext{}, &testClientLaunchError{status: platformErr.status, code: platformErr.code, detail: platformErr.detail}
	}
	args := testClientLaunchArgs(req, connection)
	secrets := collectSensitiveArgs(args)
	launchEnv, launchContextKeys := testClientLaunchEnvironment(os.Environ())
	launchContext := testClientLaunchContext{EnvKeys: launchContextKeys}
	launchTimeout := normalizeTestClientLaunchTimeout(req.TimeoutSeconds)
	process, launchContext, startErr := testClientProcessLauncher(
		ctx, resolved.Path, args, launchEnv, req.Port, launchTimeout, launchContext,
	)
	if startErr != nil {
		status := startErr.Status
		if status == 0 {
			status = http.StatusBadGateway
		}
		code := strings.TrimSpace(startErr.Code)
		if code == "" {
			code = "testclient-launch-start-failed"
		}
		detail := strings.TrimSpace(startErr.Detail)
		if detail == "" {
			detail = "TestClient process could not be started"
		}
		readiness := strings.TrimSpace(startErr.Readiness)
		if readiness == "" {
			readiness = "start_failed"
		}
		return nil, nil, launchContext, &testClientLaunchError{
			status: status,
			code:   code,
			detail: boundedPlatformOutput(detail, secrets),
			fields: testClientLaunchMetadata(startErr.PID, req, connection, resolved, args, false, startErr.Listening, startErr.Alive, readiness, launchContext, ""),
		}
	}
	if strings.TrimSpace(process.LifecycleID) == "" {
		process.LifecycleID = newTestClientLifecycleID()
	}
	pid := process.PID
	readiness := waitForTestClientReadiness(ctx, process.Done, req.Port, launchTimeout)
	switch readiness {
	case "ready":
		return testClientLaunchResult(&pid, req, connection, resolved, args, false, true, true, "ready", launchContext, process.LifecycleID), process, launchContext, nil
	case "exited_early":
		return nil, process, launchContext, &testClientLaunchError{
			status: http.StatusBadGateway,
			code:   "testclient-exited-early",
			detail: "TestClient process exited before its TPort became listening",
			fields: testClientLaunchMetadata(&pid, req, connection, resolved, args, false, false, false, "exited_early", launchContext, process.LifecycleID),
		}
	case "canceled":
		return nil, process, launchContext, &testClientLaunchError{
			status: http.StatusGatewayTimeout,
			code:   "testclient-launch-canceled",
			detail: "TestClient launch was canceled before readiness could be established",
			fields: testClientLaunchMetadata(&pid, req, connection, resolved, args, false, false, nil, "canceled", launchContext, process.LifecycleID),
		}
	default:
		return nil, process, launchContext, &testClientLaunchError{
			status: http.StatusGatewayTimeout,
			code:   "testclient-not-listening",
			detail: "TestClient process started but its TPort did not become listening before the launch timeout",
			fields: testClientLaunchMetadata(&pid, req, connection, resolved, args, false, false, true, "not_listening", launchContext, process.LifecycleID),
		}
	}
}

func validateTestClientLaunch(req testClientLaunchRequest) *testClientLaunchError {
	if !validTCPPort(req.Port) {
		return &testClientLaunchError{status: http.StatusBadRequest, code: "invalid-port", detail: "port must be between 1 and 65535"}
	}
	for label, value := range map[string]string{
		"infobase_path":     req.InfobasePath,
		"connection_string": req.ConnectionString,
		"user":              req.User,
		"password":          req.Password,
	} {
		if strings.Contains(value, "\x00") {
			return &testClientLaunchError{status: http.StatusBadRequest, code: "invalid-field", detail: label + " must not contain NUL bytes"}
		}
	}
	if strings.TrimSpace(req.ConnectionString) == "" && strings.TrimSpace(req.InfobasePath) == "" {
		return &testClientLaunchError{status: http.StatusBadRequest, code: "missing-target", detail: "connection_string or infobase_path is required"}
	}
	if version := strings.TrimSpace(req.PlatformVersion); version == "" || !validPlatformVersion(version) {
		return &testClientLaunchError{status: http.StatusBadRequest, code: "invalid-platform-version", detail: "platform_version must contain exactly four numeric components"}
	}
	return nil
}

func validPlatformVersion(value string) bool {
	parts := strings.Split(value, ".")
	if len(parts) != 4 {
		return false
	}
	for _, part := range parts {
		if part == "" {
			return false
		}
		for _, char := range part {
			if char < '0' || char > '9' {
				return false
			}
		}
	}
	return true
}

func validTCPPort(port int) bool {
	return port >= 1 && port <= 65535
}

func testClientConnectionString(req testClientLaunchRequest) string {
	if strings.TrimSpace(req.ConnectionString) != "" {
		return strings.TrimSpace(req.ConnectionString)
	}
	return fmt.Sprintf(`File="%s";`, strings.TrimSpace(req.InfobasePath))
}

func testClientLaunchArgs(req testClientLaunchRequest, connection string) []string {
	args := []string{"ENTERPRISE", "/IBConnectionString", connection}
	if strings.TrimSpace(req.User) != "" {
		args = append(args, "/N"+strings.TrimSpace(req.User))
	}
	if req.Password != "" {
		args = append(args, "/P"+req.Password)
	}
	if req.UseHWLicenses {
		args = append(args, "/UseHWLicenses+")
	}
	args = append(args, "/TESTCLIENT", "-TPort", strconv.Itoa(req.Port), "/DisableStartupDialogs", "/DisableStartupMessages")
	return args
}

func normalizeTestClientLaunchTimeout(seconds float64) time.Duration {
	if seconds <= 0 {
		return defaultTestClientLaunchTimeout
	}
	if seconds >= maxTestClientLaunchTimeout.Seconds() {
		return maxTestClientLaunchTimeout
	}
	timeout := time.Duration(seconds * float64(time.Second))
	if timeout < time.Second {
		return time.Second
	}
	return timeout
}

func waitForTestClientReadiness(ctx context.Context, done <-chan struct{}, port int, timeout time.Duration) string {
	deadline := time.NewTimer(timeout)
	defer deadline.Stop()
	ticker := time.NewTicker(testClientReadinessPoll)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return "canceled"
		case <-done:
			return "exited_early"
		case <-ticker.C:
			if testClientPortListening(port, testClientReadinessProbe) {
				return dwellForTestClientReadiness(ctx, done, deadline.C, port)
			}
		case <-deadline.C:
			select {
			case <-done:
				return "exited_early"
			default:
				return "not_listening"
			}
		}
	}
}

func dwellForTestClientReadiness(ctx context.Context, done <-chan struct{}, deadline <-chan time.Time, port int) string {
	dwell := time.NewTimer(testClientReadinessDwell)
	defer dwell.Stop()
	ticker := time.NewTicker(testClientReadinessPoll)
	defer ticker.Stop()
	for {
		select {
		case <-ctx.Done():
			return "canceled"
		case <-done:
			return "exited_early"
		case <-deadline:
			select {
			case <-done:
				return "exited_early"
			default:
				return "not_listening"
			}
		case <-ticker.C:
			if !testClientPortListening(port, testClientReadinessProbe) {
				select {
				case <-done:
					return "exited_early"
				default:
					return "not_listening"
				}
			}
		case <-dwell.C:
			if !testClientPortListening(port, testClientReadinessProbe) {
				select {
				case <-done:
					return "exited_early"
				default:
					return "not_listening"
				}
			}
			select {
			case <-done:
				return "exited_early"
			default:
				return "ready"
			}
		}
	}
}

func testClientLaunchResult(
	pid *int,
	req testClientLaunchRequest,
	connection string,
	resolved platformExecutable,
	args []string,
	reusedExisting bool,
	listening bool,
	alive any,
	readiness string,
	launchContext testClientLaunchContext,
	lifecycleID string,
) map[string]any {
	result := testClientLaunchMetadata(pid, req, connection, resolved, args, reusedExisting, listening, alive, readiness, launchContext, lifecycleID)
	result["ok"] = true
	return result
}

func testClientLaunchMetadata(
	pid *int,
	req testClientLaunchRequest,
	connection string,
	resolved platformExecutable,
	args []string,
	reusedExisting bool,
	listening bool,
	alive any,
	readiness string,
	launchContext testClientLaunchContext,
	lifecycleID string,
) map[string]any {
	commandArgs := args
	if commandArgs == nil {
		commandArgs = testClientLaunchArgs(req, connection)
	}
	secrets := collectSensitiveArgs(commandArgs)
	summary := append([]string{resolved.Path}, commandArgs...)
	if resolved.Path == "" {
		summary[0] = "1cv8"
	}
	for index, item := range summary {
		summary[index] = redactSensitiveText(item, secrets)
	}
	if readiness == "" {
		readiness = "unknown"
	}
	lifecycleID = strings.TrimSpace(lifecycleID)
	ownsProcess := ownsLaunchedTestClient(pid, reusedExisting, alive) && lifecycleID != ""
	result := map[string]any{
		"pid":                 nullablePIDValue(pid),
		"port":                req.Port,
		"host":                "127.0.0.1",
		"listening":           listening,
		"alive":               alive,
		"readiness":           readiness,
		"reused_existing":     reusedExisting,
		"response_id":         "testclient-launch",
		"executable":          "1cv8",
		"executable_resolved": resolved.Path,
		"platform_version":    resolved.Version,
		"password_set":        req.Password != "",
		"connection":          redactedConnectionSummary(connection, req.Password),
		"command_summary":     strings.Join(summary, " "),
		"launch_context":      testClientLaunchContextPayload(launchContext),
		"owns_process":        ownsProcess,
	}
	if ownsProcess {
		result["lifecycle_owner"] = "host-agent"
		result["lifecycle_id"] = lifecycleID
		result["lifecycle_handle"] = map[string]any{
			"kind": "host-agent-testclient",
			"id":   lifecycleID,
			"pid":  nullablePIDValue(pid),
			"port": req.Port,
		}
		result["client_target"] = map[string]any{
			"kind":         "host-agent-testclient",
			"lifecycle_id": lifecycleID,
			"pid":          nullablePIDValue(pid),
			"port":         req.Port,
		}
	}
	return result
}

func ownsLaunchedTestClient(pid *int, reusedExisting bool, alive any) bool {
	if pid == nil || reusedExisting {
		return false
	}
	if aliveValue, ok := alive.(bool); ok && !aliveValue {
		return false
	}
	return true
}

func (req testClientStopRequest) requestedPID() int {
	if req.PID > 0 {
		return req.PID
	}
	if req.LifecycleHandle != nil {
		return req.LifecycleHandle.PID
	}
	return 0
}

func (req testClientStopRequest) requestedPort() int {
	if req.Port != 0 {
		return req.Port
	}
	if req.LifecycleHandle != nil {
		return req.LifecycleHandle.Port
	}
	return 0
}

func (req testClientStopRequest) requestedLifecycleID() string {
	if strings.TrimSpace(req.LifecycleID) != "" {
		return strings.TrimSpace(req.LifecycleID)
	}
	if req.LifecycleHandle != nil {
		return strings.TrimSpace(req.LifecycleHandle.ID)
	}
	return ""
}

func (req testClientStopRequest) lifecycleIDMismatch() bool {
	topLevelID := strings.TrimSpace(req.LifecycleID)
	handleID := ""
	if req.LifecycleHandle != nil {
		handleID = strings.TrimSpace(req.LifecycleHandle.ID)
	}
	return topLevelID != "" && handleID != "" && topLevelID != handleID
}

func testClientLaunchContextPayload(launchContext testClientLaunchContext) map[string]any {
	launchContextPayload := map[string]any{}
	if strings.TrimSpace(launchContext.Method) != "" {
		launchContextPayload["method"] = strings.TrimSpace(launchContext.Method)
	}
	if launchContext.SessionID != nil {
		launchContextPayload["session_id"] = *launchContext.SessionID
	}
	if len(launchContext.EnvKeys) > 0 {
		keys := append([]string(nil), launchContext.EnvKeys...)
		sort.Strings(keys)
		launchContextPayload["env_keys"] = keys
	}
	return launchContextPayload
}

func testClientLaunchEnvironment(base []string) ([]string, []string) {
	values := map[string]string{}
	for _, item := range base {
		key, value, ok := strings.Cut(item, "=")
		if !ok || strings.TrimSpace(key) == "" {
			continue
		}
		values[strings.ToUpper(key)] = value
	}
	username := firstNonEmpty(values["USERNAME"], values["USER"])
	userProfile := values["USERPROFILE"]
	if badWindowsUserProfile(userProfile) {
		userProfile = ""
	}
	for _, key := range []string{"APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "HOMEPATH"} {
		if badWindowsUserProfile(values[key]) {
			values[key] = ""
		}
	}
	if userProfile == "" {
		homeDrive := firstNonEmpty(values["HOMEDRIVE"], "C:")
		homePath := values["HOMEPATH"]
		if homePath != "" && !strings.Contains(strings.ToLower(strings.ReplaceAll(homePath, "\\", "/")), "system32/config/systemprofile") {
			userProfile = strings.TrimRight(homeDrive, `\/`) + `\` + strings.TrimLeft(homePath, `\/`)
		} else if username != "" {
			userProfile = `C:\Users\` + username
		}
	}
	setIfNotEmpty(values, "USERPROFILE", userProfile)
	if userProfile != "" {
		setIfNotEmpty(values, "APPDATA", firstNonEmpty(values["APPDATA"], joinWindowsPath(userProfile, "AppData", "Roaming")))
		setIfNotEmpty(values, "LOCALAPPDATA", firstNonEmpty(values["LOCALAPPDATA"], joinWindowsPath(userProfile, "AppData", "Local")))
		localAppData := values["LOCALAPPDATA"]
		tempDir := firstNonEmpty(values["TEMP"], values["TMP"], joinWindowsPath(localAppData, "Temp"))
		setIfNotEmpty(values, "TEMP", tempDir)
		setIfNotEmpty(values, "TMP", tempDir)
		if values["HOMEDRIVE"] == "" || values["HOMEPATH"] == "" {
			if drive, path, ok := splitWindowsProfile(userProfile); ok {
				setIfNotEmpty(values, "HOMEDRIVE", firstNonEmpty(values["HOMEDRIVE"], drive))
				setIfNotEmpty(values, "HOMEPATH", firstNonEmpty(values["HOMEPATH"], path))
			}
		}
	}
	important := []string{"USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "HOMEDRIVE", "HOMEPATH", "PATH", "SYSTEMROOT"}
	contextKeys := []string{}
	for _, key := range important {
		if values[key] != "" {
			contextKeys = append(contextKeys, key)
		}
	}
	keys := make([]string, 0, len(values))
	for key := range values {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	env := make([]string, 0, len(keys))
	for _, key := range keys {
		env = append(env, key+"="+values[key])
	}
	sort.Strings(contextKeys)
	return env, contextKeys
}

func firstNonEmpty(values ...string) string {
	for _, value := range values {
		if strings.TrimSpace(value) != "" {
			return strings.TrimSpace(value)
		}
	}
	return ""
}

func setIfNotEmpty(values map[string]string, key string, value string) {
	if strings.TrimSpace(value) != "" {
		values[key] = strings.TrimSpace(value)
	}
}

func badWindowsUserProfile(value string) bool {
	normalized := strings.ToLower(strings.ReplaceAll(value, "\\", "/"))
	return strings.TrimSpace(value) == "" ||
		strings.Contains(normalized, "/windows/system32/config/systemprofile") ||
		strings.Contains(normalized, ":/windows/temp")
}

func joinWindowsPath(base string, parts ...string) string {
	out := strings.TrimRight(base, `\/`)
	for _, part := range parts {
		out += `\` + strings.Trim(part, `\/`)
	}
	return out
}

func splitWindowsProfile(profile string) (string, string, bool) {
	if len(profile) < 3 || profile[1] != ':' {
		return "", "", false
	}
	return profile[:2], profile[2:], true
}

func nullablePID(pid int) any {
	if pid <= 0 {
		return nil
	}
	return pid
}

func nullablePIDValue(pid *int) any {
	if pid == nil || *pid <= 0 {
		return nil
	}
	return *pid
}

func redactedConnectionSummary(connection string, password string) string {
	secrets := []string{}
	if password != "" {
		secrets = appendSecret(secrets, password)
	}
	if value, ok := valueAfterMarker(connection, strings.ToLower(connection), "password="); ok {
		secrets = appendSecret(secrets, value)
	}
	if value, ok := valueAfterMarker(connection, strings.ToLower(connection), "pwd="); ok {
		secrets = appendSecret(secrets, value)
	}
	return redactSensitiveText(connection, secrets)
}
