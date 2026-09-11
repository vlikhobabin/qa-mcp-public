## Context

`POST /agent/complete` is the qa-mcp host-agent side of the agentic-rag LLM CLI
bridge. The request is decoded directly into `agentCompleteRequest`. Because
`TimeoutSeconds` is an `int`, Go's JSON decoder rejects a wire value such as
`300.0` with `cannot unmarshal number 300.0 into Go struct field ... of type
int`.

The consumer observed in the real Windows E2E sends a Python float field on the
wire. JSON does not distinguish "integer field" at the schema level strongly
enough for this bridge to require exact Go `int` syntax, so the receiver should
be tolerant while continuing to clamp the value before constructing a context
timeout.

## Goals / Non-Goals

**Goals:**

- Decode `timeout_seconds` values like `300` and `300.0` successfully.
- Keep absent, zero or negative timeouts on the existing default path.
- Keep sub-second positive values floored to one second and oversized values
  capped at `maxAgentTimeout`.
- Add regression coverage at the authenticated HTTP handler boundary.

**Non-Goals:**

- Changing the agentic-rag transport payload type.
- Changing CLI allowlists, auth, prompt redaction, command construction or
  process-group cleanup.
- Running live 1C, TestClient, Vanessa or protocol replay evidence.

## Decisions

- Represent `TimeoutSeconds` as `float64` in `agentCompleteRequest`.
  This lets the standard Go JSON decoder accept both `300` and `300.0` without
  adding a custom unmarshal path.
- Change `normalizeAgentTimeout` to accept `float64` and convert with
  `time.Duration(seconds * float64(time.Second))`.
  This preserves fractional timeout support if a caller sends it, while the
  existing one-second floor prevents accidental immediate cancellation.
- Exercise the behavior through `rawRequest` with a literal JSON float body.
  Existing helper requests use `json.Marshal` from Go values and can hide the
  exact wire shape that regressed in the cross-process path.

## Risks / Trade-offs

- Floating-point conversion could represent very large values imprecisely.
  Mitigation: the result is clamped to `maxAgentTimeout`, and non-positive
  values still use the default timeout.
- Sub-second values now reach normalization instead of being impossible to
  express with the request struct. Mitigation: the existing minimum clamp
  floors them to one second.

## Migration Plan

Rebuild and redeploy the Windows host-agent binary. Rollback is the prior
binary; requests with decimal `timeout_seconds` would again fail with HTTP 400.
