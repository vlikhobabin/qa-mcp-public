# Card: read_list_grid on a COLD [redacted third-party configuration] client can return an empty descriptor (first-read race)

Status: done
Owner: qa-mcp
Capability: `qa-mcp-tool-endpoint-contract`
Change: `retry-empty-descriptor-cold-client` (archived `2026-07-09-…`)

## Resolved diagnosis (regression-check done 2026-07-09 — NOT a regression)

Initial symptom: `read_list_grid` / `read_form_descriptor` for `Справочник.Валюты` on a
[redacted third-party configuration] ([redacted product] 3.0) base returned `list-table-unresolved` with an EMPTY live form
descriptor (`opened: null`, 0 elements). A head-to-head regression-check (released
`qa-mcp-thin:v0.2.4` vs HEAD, driven against the SAME redacted-third-party-configuration client) PROVED this is
**not a HEAD regression and not a "no Table" parse bug** — it is a **cold-client first-read
race**: the read ran seconds after the heavy [redacted third-party configuration] client launched, before its managed
form was ready over the protocol.

### Evidence (LIVE .201, redacted-third-party-configuration, TPort 15385, host-agent 0.1.4 :8002)

- **Cold** (first read right after launch): `opened: null`, 0 elements → `list-table-unresolved`
  — reproduced on BOTH HEAD and v0.2.4.
- **Warm**, HEAD + `client_port=15385` + **NO window override**: `ok: true`, `row_count: 10`,
  `opened: "Валюты"`, `list_refresh: f5 nonzero` — confirmed **2×**.
- **Warm**, v0.2.4 + explicit window: enumerated (`opened: "Валюты"`) but F5 failed → 0 rows.
  So HEAD ≥ v0.2.4 on this read (HEAD's F5/client_port works where v0.2.4's did not).

Conclusions: (a) the `client_port` auto-window (host-agent 0.1.4 / rebuilt thin image) is now
**PROVEN on [redacted third-party configuration] too** (warm, no `QA_MCP_HOST_AGENT_WINDOW` needed) — the prior
[[third-party-config-base-credentials-and-read-proof]] "10 Валюты rows" result stands; (b) the empty
descriptor was purely a cold-start artifact of a very heavy config.

## Change 1: `retry-empty-descriptor-cold-client`

Capability: `qa-mcp-tool-endpoint-contract`.

**What.** `_resolve_list_table_for_read` (used by `read_list_grid` / `read_list_column`) retries
the live form-descriptor read a bounded number of times when the descriptor is **empty**
(`opened` is falsy AND 0 elements) — a cold-client / not-yet-rendered form, distinct from a
genuinely empty catalog (which still exposes a `Table` element). New config knobs
`QA_MCP_DESCRIPTOR_WARMUP_ATTEMPTS` (default 3) and `QA_MCP_DESCRIPTOR_WARMUP_DELAY_SEC`
(default 1.5). When all attempts still return empty, the diagnostic reports
`descriptor_empty: true`, `warmup_attempts`, and a "client may still be warming up" reason.

**Why.** A heavy configuration ([redacted third-party configuration] / Бухгалтерия 3.0) returns an empty descriptor on
the first read right after client launch (proven this session — see the diagnosis above); the
read now self-heals instead of failing with `list-table-unresolved`.

**Tasks.**
- [x] `config.py`: add `descriptor_warmup_attempts` / `descriptor_warmup_delay_sec` + env consts + `from_env`
- [x] `mcp_server.py`: `_descriptor_is_empty` helper + bounded retry loop in `_resolve_list_table_for_read` + warm-up-aware diagnostic
- [x] `tests/test_form_descriptor.py`: retry-then-succeed + exhaust-then-report tests (offline)
- [x] Full `uv run pytest` green (798)
- [ ] Live cold-client re-verify on .201 (needs an image rebuild to compile the change into the `.so` + hitting the cold window) — deferred; offline-proven, low-risk defensive change

## Log
- 2026-07-09: Filed as a suspected regression / empty-descriptor bug. Regression-check
  (v0.2.4 ↔ HEAD on the same redacted-third-party-configuration client) reclassified it as a cold-client first-read
  race; `client_port` auto-window confirmed working on [redacted third-party configuration] once warm (10 rows, no
  override, 2×). Rescoped to optional retry-on-empty-descriptor hardening.
- 2026-07-09: Change `retry-empty-descriptor-cold-client` DELIVERED. Implemented the bounded
  descriptor-warmup retry + config knobs + warm-up diagnostic; offline tests (retry-then-succeed
  / exhaust-then-report) added; full `uv run pytest` green (798); `openspec validate --strict`
  pass; spec `qa-mcp-tool-endpoint-contract` synced (+1 requirement); change archived. Live
  cold-client re-verify deferred (needs image rebuild to compile into the `.so`).
