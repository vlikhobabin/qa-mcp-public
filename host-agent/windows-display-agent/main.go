package main

import (
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"time"
)

const (
	AgentVersion                      = "1.0.0-standalone"
	DisplayProtocol                   = "qa-mcp.windows-host-bridge.v1"
	StandaloneAPI                     = "qa-mcp.windows-host-bridge"
	StandaloneAPIMajor                = 1
	TestClientWindowTargetCapability  = "testclient-window-target"
	TestClientLifecycleStopCapability = "testclient-lifecycle-handle-stop"
)

var StandaloneCapabilities = []string{
	"health",
	"testclient-lifecycle",
	"testclient-relay",
	"window-list",
	"bounded-input",
	"screenshot",
	"uia-visible-list-cells",
	TestClientWindowTargetCapability,
	TestClientLifecycleStopCapability,
}

var StandaloneEndpoints = []string{
	"/v1/capabilities", "/version", "/health",
	"/send_keys", "/type", "/click", "/screenshot", "/window_list",
	"/uia/visible_list_cells", "/testclient/launch", "/testclient/status", "/testclient/stop",
}

type Config struct {
	Addr                 string
	Token                string
	TokenFile            string
	AllowedOrigins       []string
	PlatformCatalogRoots []string
	TestClientRelay      *TestClientRelay
}

type Rect struct {
	X      int `json:"x"`
	Y      int `json:"y"`
	Width  int `json:"width"`
	Height int `json:"height"`
}

type WindowInfo struct {
	HWND     string `json:"hwnd"`
	Title    string `json:"title"`
	Class    string `json:"class,omitempty"`
	PID      uint32 `json:"pid,omitempty"`
	Geometry Rect   `json:"geometry"`
	Visible  bool   `json:"visible"`
}

type clientTarget struct {
	Kind        string `json:"kind"`
	LifecycleID string `json:"lifecycle_id"`
	PID         int    `json:"pid"`
	Port        int    `json:"port"`
}

type Driver interface {
	Health() map[string]any
	Focus(window string) (WindowInfo, error)
	SendKeys(keys []string, settle time.Duration) error
	SendKeysTo(window string, keys []string, settle time.Duration) (WindowInfo, error)
	TypeText(text string, delay time.Duration) error
	Click(x int, y int, button int) error
	Screenshot(window string) ([]byte, WindowInfo, error)
	WindowList() ([]WindowInfo, error)
	VisibleListCells(window string, limit int) (WindowInfo, []string, error)
}

type Agent struct {
	config       Config
	driver       Driver
	hash         string
	failureLimit *failureLimiter
	execLimit    *executionLimiter
	testClients  *testClientLifecycleStore
}

func NewAgent(config Config, driver Driver) *Agent {
	return &Agent{
		config:       config,
		driver:       driver,
		hash:         binaryHash(),
		failureLimit: newFailureLimiter(5, time.Minute),
		execLimit:    newExecutionLimiter(defaultMaxConcurrentExec),
		testClients:  newTestClientLifecycleStore(),
	}
}

func (a *Agent) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/v1/capabilities", a.withAuth(a.handleVersion))
	mux.HandleFunc("/version", a.withAuth(a.handleVersion))
	mux.HandleFunc("/health", a.withAuth(a.handleHealth))
	mux.HandleFunc("/send_keys", a.withAuth(a.withExecutionLimit(a.handleSendKeys)))
	mux.HandleFunc("/type", a.withAuth(a.withExecutionLimit(a.handleType)))
	mux.HandleFunc("/click", a.withAuth(a.withExecutionLimit(a.handleClick)))
	mux.HandleFunc("/screenshot", a.withAuth(a.withExecutionLimit(a.handleScreenshot)))
	mux.HandleFunc("/window_list", a.withAuth(a.withExecutionLimit(a.handleWindowList)))
	mux.HandleFunc("/uia/visible_list_cells", a.withAuth(a.withExecutionLimit(a.handleVisibleListCells)))
	mux.HandleFunc("/testclient/launch", a.withAuth(a.withExecutionLimit(a.handleTestClientLaunch)))
	mux.HandleFunc("/testclient/status", a.withAuth(a.withExecutionLimit(a.handleTestClientStatus)))
	mux.HandleFunc("/testclient/stop", a.withAuth(a.withExecutionLimit(a.handleTestClientStop)))
	return mux
}

func (a *Agent) withExecutionLimit(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		release, ok := a.execLimit.acquire()
		if !ok {
			writeError(w, http.StatusTooManyRequests, "execution-capacity-exhausted", "host bridge execution capacity is exhausted")
			return
		}
		defer release()
		next(w, r)
	}
}

func (a *Agent) withAuth(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if a.config.Token == "" {
			writeError(w, http.StatusServiceUnavailable, "token-not-configured", "QA_MCP_HOST_AGENT_TOKEN is required")
			return
		}
		if !a.originAllowed(r.Header.Get("Origin")) {
			writeError(w, http.StatusForbidden, "origin-not-allowed", "request Origin is not allowlisted")
			return
		}
		if !tokenMatches(r.Header.Get("X-QA-MCP-Agent-Token"), a.config.Token) {
			if !a.failureLimit.allow(clientKey(r)) {
				writeError(w, http.StatusTooManyRequests, "rate-limited", "too many failed authentication attempts")
				return
			}
			writeError(w, http.StatusUnauthorized, "auth-failed", "invalid or missing X-QA-MCP-Agent-Token")
			return
		}
		next(w, r)
	}
}

func (a *Agent) originAllowed(origin string) bool {
	origin = strings.TrimSpace(origin)
	if origin == "" {
		return true
	}
	for _, allowed := range a.config.AllowedOrigins {
		allowed = strings.TrimSpace(allowed)
		if allowed == "*" || strings.EqualFold(origin, allowed) {
			return true
		}
	}
	return false
}

func (a *Agent) handleVersion(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeError(w, http.StatusMethodNotAllowed, "method-not-allowed", "use GET")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"ok": true, "api": StandaloneAPI, "api_major": StandaloneAPIMajor,
		"version": AgentVersion, "sha256": a.hash, "display_protocol": DisplayProtocol,
		"capabilities": StandaloneCapabilities, "endpoints": StandaloneEndpoints,
	})
}

func (a *Agent) handleHealth(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		writeError(w, http.StatusMethodNotAllowed, "method-not-allowed", "use GET")
		return
	}
	health := a.driver.Health()
	health["ok"] = health["ok"] != false
	health["version"] = AgentVersion
	health["api"] = StandaloneAPI
	health["api_major"] = StandaloneAPIMajor
	if a.config.TestClientRelay != nil {
		health["testclient_relay"] = a.config.TestClientRelay.Status()
	} else {
		health["testclient_relay"] = map[string]any{"configured": false, "state": "disabled", "active_sessions": 0}
	}
	writeJSON(w, http.StatusOK, health)
}

// effectiveWindow resolves the window selector a display primitive should
// target. An explicit `window` (title substring or class:/hwnd:/pid: selector)
// always wins. Otherwise, when a driven-client TPort is supplied, target the
// window owned by the process listening on that port (`port:<N>`), so callers
// need not hard-code a per-configuration window caption. Empty when neither is
// given; request dispatch then fails closed instead of selecting foreground.
func effectiveWindow(window string, clientPort int) string {
	if explicit := explicitWindowSelector(window); explicit != "" {
		return explicit
	}
	if clientPort > 0 {
		return fmt.Sprintf("port:%d", clientPort)
	}
	return ""
}

func explicitWindowSelector(window string) string {
	selector := strings.TrimSpace(window)
	if selector == "" || selector == "*" {
		return ""
	}
	return selector
}

func (a *Agent) resolveDisplayWindow(window string, target *clientTarget, clientPort int) (string, error) {
	if target == nil {
		return "", ErrMissingClientTarget
	}
	if target.PID <= 0 || !validTCPPort(target.Port) || strings.TrimSpace(target.LifecycleID) == "" {
		return "", ErrClientTargetInvalid
	}
	if target.Kind != "" && target.Kind != "host-agent-testclient" {
		return "", ErrClientTargetInvalid
	}
	if err := a.testClients.ValidateDisplayTarget(*target); err != nil {
		return "", err
	}
	return fmt.Sprintf("client:%d:%d", target.PID, target.Port), nil
}

func requireInteractiveDesktop() error {
	switch desktopSessionProbe() {
	case desktopSessionActive:
		return nil
	case desktopSessionLocked:
		return ErrDesktopSessionLocked
	case desktopSessionDisconnected:
		return ErrDesktopSessionDisconnected
	default:
		return ErrDesktopSessionNonInteractive
	}
}

func (a *Agent) handleSendKeys(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Keys         []string      `json:"keys"`
		SettleSec    float64       `json:"settle_sec"`
		Window       string        `json:"window"`
		ClientPort   int           `json:"client_port"`
		ClientTarget *clientTarget `json:"client_target"`
	}
	if !decodeJSON(w, r, &req) {
		return
	}
	if len(req.Keys) == 0 {
		writeError(w, http.StatusBadRequest, "empty-keys", "keys must contain at least one key or chord")
		return
	}
	window, err := a.resolveDisplayWindow(req.Window, req.ClientTarget, req.ClientPort)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	if err := requireInteractiveDesktop(); err != nil {
		writeDriverError(w, err)
		return
	}
	target, err := a.driver.SendKeysTo(window, req.Keys, seconds(req.SettleSec))
	if err != nil {
		writeDriverError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "sent": len(req.Keys), "keys": req.Keys, "target": target})
}

func (a *Agent) handleType(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Text         string        `json:"text"`
		DelayMS      int           `json:"delay_ms"`
		Window       string        `json:"window"`
		ClientPort   int           `json:"client_port"`
		ClientTarget *clientTarget `json:"client_target"`
	}
	if !decodeJSON(w, r, &req) {
		return
	}
	window, err := a.resolveDisplayWindow(req.Window, req.ClientTarget, req.ClientPort)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	if err := requireInteractiveDesktop(); err != nil {
		writeDriverError(w, err)
		return
	}
	target, err := a.driver.Focus(window)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	if err := a.driver.TypeText(req.Text, time.Duration(req.DelayMS)*time.Millisecond); err != nil {
		writeDriverError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "typed": true, "text_length": len([]rune(req.Text)), "target": target})
}

func (a *Agent) handleClick(w http.ResponseWriter, r *http.Request) {
	var req struct {
		X            int           `json:"x"`
		Y            int           `json:"y"`
		Button       int           `json:"button"`
		Window       string        `json:"window"`
		ClientPort   int           `json:"client_port"`
		ClientTarget *clientTarget `json:"client_target"`
	}
	if !decodeJSON(w, r, &req) {
		return
	}
	if req.Button == 0 {
		req.Button = 1
	}
	window, err := a.resolveDisplayWindow(req.Window, req.ClientTarget, req.ClientPort)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	if err := requireInteractiveDesktop(); err != nil {
		writeDriverError(w, err)
		return
	}
	target, err := a.driver.Focus(window)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	if err := a.driver.Click(req.X, req.Y, req.Button); err != nil {
		writeDriverError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "clicked": true, "x": req.X, "y": req.Y, "button": req.Button, "target": target})
}

func (a *Agent) handleScreenshot(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Window       string        `json:"window"`
		ClientPort   int           `json:"client_port"`
		ClientTarget *clientTarget `json:"client_target"`
	}
	if !decodeJSON(w, r, &req) {
		return
	}
	window, err := a.resolveDisplayWindow(req.Window, req.ClientTarget, req.ClientPort)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	if err := requireInteractiveDesktop(); err != nil {
		writeDriverError(w, err)
		return
	}
	png, target, err := a.driver.Screenshot(window)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	w.Header().Set("Content-Type", "image/png")
	w.Header().Set("X-QA-MCP-Window", target.Title)
	w.Header().Set("X-QA-MCP-HWND", target.HWND)
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write(png)
}

func (a *Agent) handleWindowList(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Geometry     bool          `json:"geometry"`
		Window       string        `json:"window"`
		ClientPort   int           `json:"client_port"`
		ClientTarget *clientTarget `json:"client_target"`
	}
	if !decodeJSON(w, r, &req) {
		return
	}
	if _, err := a.resolveDisplayWindow(req.Window, req.ClientTarget, req.ClientPort); err != nil {
		writeDriverError(w, err)
		return
	}
	if err := requireInteractiveDesktop(); err != nil {
		writeDriverError(w, err)
		return
	}
	target, err := clientTargetResolver(req.ClientTarget.PID, req.ClientTarget.Port)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	if !req.Geometry {
		target.Geometry = Rect{}
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "count": 1, "windows": []WindowInfo{target}})
}

func (a *Agent) handleVisibleListCells(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Window       string        `json:"window"`
		Limit        int           `json:"limit"`
		ClientPort   int           `json:"client_port"`
		ClientTarget *clientTarget `json:"client_target"`
	}
	if !decodeJSON(w, r, &req) {
		return
	}
	window, err := a.resolveDisplayWindow(req.Window, req.ClientTarget, req.ClientPort)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	if err := requireInteractiveDesktop(); err != nil {
		writeDriverError(w, err)
		return
	}
	target, cells, err := a.driver.VisibleListCells(window, req.Limit)
	if err != nil {
		writeDriverError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"ok":     true,
		"target": target,
		"count":  len(cells),
		"cells":  cells,
	})
}

func decodeJSON(w http.ResponseWriter, r *http.Request, out any) bool {
	if r.Method != http.MethodPost {
		writeError(w, http.StatusMethodNotAllowed, "method-not-allowed", "use POST")
		return false
	}
	defer r.Body.Close()
	if err := json.NewDecoder(io.LimitReader(r.Body, 1<<20)).Decode(out); err != nil {
		writeError(w, http.StatusBadRequest, "invalid-json", err.Error())
		return false
	}
	return true
}

func writeDriverError(w http.ResponseWriter, err error) {
	status := http.StatusInternalServerError
	if errors.Is(err, ErrUnsupported) || errors.Is(err, ErrWindowNotFound) ||
		errors.Is(err, ErrMissingClientTarget) || errors.Is(err, ErrClientTargetInvalid) ||
		errors.Is(err, ErrClientTargetStale) || errors.Is(err, ErrClientTargetMismatch) {
		status = http.StatusUnprocessableEntity
	} else if errors.Is(err, ErrForegroundDenied) || errors.Is(err, ErrDesktopSessionLocked) ||
		errors.Is(err, ErrDesktopSessionDisconnected) || errors.Is(err, ErrDesktopSessionNonInteractive) {
		status = http.StatusConflict
	}
	writeError(w, status, errorCode(err), err.Error())
}

func writeError(w http.ResponseWriter, status int, code string, detail string) {
	writeJSON(w, status, map[string]any{"ok": false, "status": status, "error": code, "detail": detail})
}

func writeJSON(w http.ResponseWriter, status int, payload any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(payload)
}

func seconds(value float64) time.Duration {
	if value <= 0 {
		return 0
	}
	return time.Duration(value * float64(time.Second))
}

func binaryHash() string {
	exe, err := os.Executable()
	if err != nil {
		return ""
	}
	f, err := os.Open(exe)
	if err != nil {
		return ""
	}
	defer f.Close()
	sum := sha256.New()
	if _, err := io.Copy(sum, f); err != nil {
		return ""
	}
	return hex.EncodeToString(sum.Sum(nil))
}

func tokenMatches(got string, expected string) bool {
	if got == "" || expected == "" {
		return false
	}
	gotSum := sha256.Sum256([]byte(got))
	expectedSum := sha256.Sum256([]byte(expected))
	return subtle.ConstantTimeCompare(gotSum[:], expectedSum[:]) == 1
}

type failureLimiter struct {
	mu       sync.Mutex
	attempts map[string][]time.Time
	limit    int
	window   time.Duration
}

func newFailureLimiter(limit int, window time.Duration) *failureLimiter {
	return &failureLimiter{attempts: map[string][]time.Time{}, limit: limit, window: window}
}

func (l *failureLimiter) allow(key string) bool {
	return l.allowAt(key, time.Now())
}

func (l *failureLimiter) allowAt(key string, now time.Time) bool {
	cutoff := now.Add(-l.window)
	l.mu.Lock()
	defer l.mu.Unlock()
	l.pruneLocked(cutoff)
	var kept []time.Time
	for _, seen := range l.attempts[key] {
		if seen.After(cutoff) {
			kept = append(kept, seen)
		}
	}
	if len(kept) >= l.limit {
		l.attempts[key] = kept
		return false
	}
	l.attempts[key] = append(kept, now)
	return true
}

func (l *failureLimiter) pruneLocked(cutoff time.Time) {
	for key, attempts := range l.attempts {
		var kept []time.Time
		for _, seen := range attempts {
			if seen.After(cutoff) {
				kept = append(kept, seen)
			}
		}
		if len(kept) == 0 {
			delete(l.attempts, key)
			continue
		}
		l.attempts[key] = kept
	}
}

const defaultMaxConcurrentExec = 4

type executionLimiter struct {
	slots chan struct{}
}

func newExecutionLimiter(limit int) *executionLimiter {
	if limit < 1 {
		limit = 1
	}
	return &executionLimiter{slots: make(chan struct{}, limit)}
}

func (l *executionLimiter) acquire() (func(), bool) {
	if l == nil {
		return func() {}, true
	}
	select {
	case l.slots <- struct{}{}:
		return func() { <-l.slots }, true
	default:
		return nil, false
	}
}

func clientKey(r *http.Request) string {
	host, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil || host == "" {
		return r.RemoteAddr
	}
	return host
}

var (
	ErrUnsupported                  = errors.New("win32 primitives are supported only on Windows")
	ErrWindowNotFound               = errors.New("target window not found")
	ErrForegroundDenied             = errors.New("foreground denied")
	ErrMissingClientTarget          = errors.New("missing client target")
	ErrClientTargetInvalid          = errors.New("invalid client target")
	ErrClientTargetStale            = errors.New("stale client target")
	ErrClientTargetMismatch         = errors.New("client target mismatch")
	ErrDesktopSessionLocked         = errors.New("desktop session locked")
	ErrDesktopSessionDisconnected   = errors.New("desktop session disconnected")
	ErrDesktopSessionNonInteractive = errors.New("desktop session noninteractive")
)

func errorCode(err error) string {
	switch {
	case errors.Is(err, ErrUnsupported):
		return "unsupported-platform"
	case errors.Is(err, ErrWindowNotFound):
		return "window-not-found"
	case errors.Is(err, ErrForegroundDenied):
		return "foreground-denied"
	case errors.Is(err, ErrMissingClientTarget):
		return "missing-client-target"
	case errors.Is(err, ErrClientTargetInvalid):
		return "invalid-client-target"
	case errors.Is(err, ErrClientTargetStale):
		return "stale-client-target"
	case errors.Is(err, ErrClientTargetMismatch):
		return "client-target-mismatch"
	case errors.Is(err, ErrDesktopSessionLocked):
		return "desktop-session-locked"
	case errors.Is(err, ErrDesktopSessionDisconnected):
		return "desktop-session-disconnected"
	case errors.Is(err, ErrDesktopSessionNonInteractive):
		return "desktop-session-noninteractive"
	default:
		return "primitive-failed"
	}
}

func main() {
	addr := flag.String("addr", envDefault("QA_MCP_HOST_AGENT_ADDR", "127.0.0.1:8001"), "host/port to bind")
	token := flag.String("token", os.Getenv("QA_MCP_HOST_AGENT_TOKEN"), "shared token for primitive endpoints")
	tokenFile := flag.String("token-file", os.Getenv("QA_MCP_HOST_AGENT_TOKEN_FILE"), "file containing the shared token")
	allowedOrigins := flag.String("allowed-origin", os.Getenv("QA_MCP_HOST_AGENT_ALLOWED_ORIGINS"), "comma-separated browser Origin allowlist; empty rejects browser-origin requests")
	platformCatalog := flag.String("platform-catalog", platformCatalogFlagDefault(), "comma- or semicolon-separated 1C platform catalog roots such as C:\\Program Files\\1cv8")
	testClientRelayAddr := flag.String("testclient-relay-addr", os.Getenv("QA_MCP_TESTCLIENT_RELAY_ADDR"), "optional authenticated TestClient relay listen address")
	testClientRelayPort := flag.Int("testclient-relay-target-port", intEnvDefault("QA_MCP_TESTCLIENT_RELAY_TARGET_PORT", 15381), "fixed loopback TestClient target port for the authenticated relay")
	testClientBrokerPort := flag.Int("testclient-broker-port", 0, "internal: transient TestClient broker rendezvous port")
	testClientBrokerNonce := flag.String("testclient-broker-nonce", "", "internal: transient TestClient broker rendezvous nonce")
	logPath := flag.String("log", os.Getenv("QA_MCP_HOST_AGENT_LOG"), "optional log file (recommended for the windowless build, which has no console to print to)")
	flag.Parse()
	if *testClientBrokerPort != 0 || strings.TrimSpace(*testClientBrokerNonce) != "" {
		if err := runTestClientTaskBroker(*testClientBrokerPort, strings.TrimSpace(*testClientBrokerNonce)); err != nil {
			log.Printf("TestClient broker: %v", err)
			os.Exit(1)
		}
		return
	}

	// The shipped binary is built with `-ldflags -H windowsgui` so the scheduled task does NOT pop a console
	// window on the interactive desktop. That subsystem has no console, so route logs to a file when one is given
	// (the installer passes one); otherwise logs go to the default stderr (visible when run from a dev console).
	if *logPath != "" {
		if f, err := os.OpenFile(*logPath, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644); err == nil {
			log.SetOutput(f)
		}
	}
	listener, err := net.Listen("tcp", *addr)
	if err != nil {
		log.Fatalf("listen %s: %v", *addr, err)
	}
	resolvedToken, err := loadToken(*token, *tokenFile)
	if err != nil {
		log.Fatalf("load token: %v", err)
	}
	config := Config{
		Addr:                 *addr,
		Token:                resolvedToken,
		TokenFile:            *tokenFile,
		AllowedOrigins:       splitCSV(*allowedOrigins),
		PlatformCatalogRoots: configuredPlatformCatalogRoots(*platformCatalog),
	}
	if !validTCPPort(*testClientRelayPort) {
		log.Fatalf("testclient relay target port must be between 1 and 65535")
	}
	testClientRelay, err := NewTestClientRelay(TestClientRelayConfig{
		Listen: *testClientRelayAddr,
		Token:  resolvedToken,
		Target: net.JoinHostPort("127.0.0.1", fmt.Sprintf("%d", *testClientRelayPort)),
	})
	if err != nil {
		log.Fatalf("testclient relay configuration: %v", err)
	}
	if err := testClientRelay.Start(); err != nil {
		log.Fatalf("testclient relay listen: %v", err)
	}
	defer testClientRelay.Close()
	config.TestClientRelay = testClientRelay
	agent := NewAgent(config, NewWin32Driver())
	log.Printf("qa-mcp host agent %s listening on %s", AgentVersion, listener.Addr())
	if resolvedToken == "" {
		log.Printf("QA_MCP_HOST_AGENT_TOKEN or QA_MCP_HOST_AGENT_TOKEN_FILE is not set; endpoints will reject requests")
	}
	if err := http.Serve(listener, agent.Handler()); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatalf("serve: %v", err)
	}
}

func loadToken(token string, tokenFile string) (string, error) {
	token = normalizeToken(token)
	if token != "" {
		return token, nil
	}
	tokenFile = strings.TrimSpace(tokenFile)
	if tokenFile == "" {
		return "", nil
	}
	raw, err := os.ReadFile(tokenFile)
	if err != nil {
		return "", err
	}
	return normalizeToken(string(raw)), nil
}

func normalizeToken(value string) string {
	token := strings.TrimSpace(value)
	token = strings.TrimPrefix(token, "\ufeff")
	return strings.TrimSpace(token)
}

func splitCSV(value string) []string {
	var out []string
	for _, part := range strings.Split(value, ",") {
		part = strings.TrimSpace(part)
		if part != "" {
			out = append(out, part)
		}
	}
	return out
}

func envDefault(name string, fallback string) string {
	if value := os.Getenv(name); value != "" {
		return value
	}
	return fallback
}

func intEnvDefault(name string, fallback int) int {
	value := strings.TrimSpace(os.Getenv(name))
	if value == "" {
		return fallback
	}
	parsed, err := strconv.Atoi(value)
	if err != nil {
		return fallback
	}
	return parsed
}

func platformCatalogFlagDefault() string {
	if value := os.Getenv("QA_MCP_PLATFORM_CATALOG"); value != "" {
		return value
	}
	return os.Getenv("QA_MCP_PLATFORM_CATALOG_ROOTS")
}

func configuredPlatformCatalogRoots(value string) []string {
	var roots []string
	for _, part := range strings.FieldsFunc(value, func(r rune) bool { return r == ',' || r == ';' }) {
		if part = strings.TrimSpace(part); part != "" {
			roots = append(roots, part)
		}
	}
	if len(roots) == 0 && runtime.GOOS == "windows" {
		roots = []string{`C:\Program Files\1cv8`, `C:\Program Files (x86)\1cv8`}
	}
	return roots
}

func hwndString(hwnd uintptr) string {
	return fmt.Sprintf("0x%X", hwnd)
}
