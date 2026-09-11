package main

import (
	"encoding/json"
	"net/http"
	"strings"
	"testing"
)

func TestStandaloneCapabilityHandshake(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	rec := request(agent.Handler(), http.MethodGet, "/v1/capabilities", "tok", nil)
	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", rec.Code, rec.Body.String())
	}
	var payload struct {
		APIMajor     int      `json:"api_major"`
		Capabilities []string `json:"capabilities"`
		Endpoints    []string `json:"endpoints"`
	}
	if err := json.Unmarshal(rec.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload.APIMajor != StandaloneAPIMajor {
		t.Fatalf("api_major = %d", payload.APIMajor)
	}
	if len(payload.Capabilities) != len(StandaloneCapabilities) {
		t.Fatalf("capabilities = %#v", payload.Capabilities)
	}
	joined := strings.Join(append(payload.Capabilities, payload.Endpoints...), " ")
	for _, forbidden := range []string{"agent", "bsl", "com", "onboarding", "path", "platform", "registry", "team"} {
		if strings.Contains(strings.ToLower(joined), forbidden) {
			t.Fatalf("standalone handshake contains %q: %s", forbidden, joined)
		}
	}
}

func TestProductSpecificRoutesAreAbsent(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	for _, route := range []string{
		"/agent/complete", "/bsl/diagnostics", "/bsl/resync", "/com/doctor",
		"/com/execute", "/path/infobase", "/platform/execute", "/team/register",
	} {
		rec := request(agent.Handler(), http.MethodPost, route, "tok", map[string]any{})
		if rec.Code != http.StatusNotFound {
			t.Errorf("%s status = %d", route, rec.Code)
		}
	}
}

func TestStandaloneHealthOmitsProductFields(t *testing.T) {
	agent := NewAgent(Config{Token: "tok"}, &fakeDriver{})
	rec := request(agent.Handler(), http.MethodGet, "/health", "tok", nil)
	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d body=%s", rec.Code, rec.Body.String())
	}
	for _, field := range []string{"agent_cli", "bsl_agent", "com_worker", "platform_catalog", "registration"} {
		if strings.Contains(rec.Body.String(), `"`+field+`"`) {
			t.Errorf("health contains removed field %q: %s", field, rec.Body.String())
		}
	}
}
