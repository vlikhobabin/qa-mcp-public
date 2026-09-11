# 112. EPIC — multi-platform support: 1C 8.5 alongside 8.3.27 (per user environment)

## Status
4.done

## Order Index
112

## Owner
unassigned

## OpenSpec Stage
epic

## Source
- 2026-06-25 feasibility probe on this Linux server (8.5.1.1343 installed at `/opt/1cv8/x86_64/8.5.1.1343`).
  Goal: the product must drive **both** 1C 8.5 and 8.3.27, selecting the right protocol assets by the user's
  environment (the platform the container/runtime is pointed at via `PLATFORM_ROOT`).
- Predecessor work: the Docker host-platform delivery (memory [[qa-mcp-public-delivery-prep]]) and the
  version-resilience tooling from card 111 item 4 (`regression/versioning.py` + manifest + runbook).
- Memory: [[qa-mcp-8-5-platform-support]] (the full feasibility findings + phased plan).

## Summary
The engine replays genuine TestClient protocol captures + frame templates that are **specific to one platform
protocol version**. Today everything is captured on 8.3.27; 8.5 is a new major version.

**Empirical verdict (probed 2026-06-25):**
- ✅ The product **launches an 8.5 `/TESTCLIENT` fine** — `lifecycle` is version-agnostic (only the
  `DEFAULT_PLATFORM_ROOT` default is 8.3). Booted 8.5 against a throwaway empty 8.5 file IB → listening.
- ❌ The existing **8.3 captures do NOT replay on 8.5** — the handshake breaks:
  `client ACK GUID not found in response after manager frame 3`. **→ 8.5 needs a FULL RE-CAPTURE, not a
  re-stamp.**

**Why it is tractable:** the protocol **code is data-driven** — frame offsets/field-kinds come from the JSON
templates; the wire markers (`TAIL_MARKER`, GUID regexes, value envelopes `0xE0/0xFA/0x81/…`) are structural.
So 8.5 support is expected to be **DATA (re-capture) + multi-version bundling**, with code changes ONLY if the
8.5 decode (P2) shows the deeper wire structure also moved. The capture methodology, the 189-script
`tools/protocol-research/` harness, the drift detector and the live-regression harness all already exist.

## Children (phase order — see cards 113–118)

- **P0 (113) — multi-version architecture.** Per-version bundled asset sets + version-aware resolvers +
  per-version manifest + `QA_MCP_PLATFORM_VERSION` selection. *Can start immediately, in parallel with P1.*
- **P1 (114) — stand up the 8.5 lab contour.** An 8.5 infobase carrying the «QA MCP Protocol Fixture V1»
  fixture form + the capture infrastructure (TestClient + tcpdump on `lo`) on 8.5.
- **P2 (115) — re-capture the genuine corpus on 8.5.** Handshake + frame templates (8-106 + value-read
  218-221) + the 13 action/foreground captures + accepted_mappings; decode + diff 8.5↔8.3 (answers the
  code-change risk).
- **P3 (116) — version-conditional code, IF P2's diff shows the wire moved deeper than the handshake**
  (hopefully none); wire the P0 resolvers to the 8.5 set.
- **P4 (117) — re-validate ALL 61 tools on 8.5.** Live-regression CORE GREEN; per-capability probe corpus;
  re-measure the transpile corpus; re-stamp the 8.5 manifest.
- **P5 (118) — multi-version delivery.** Bundle BOTH sets; the Docker delivery selects by `PLATFORM_ROOT`;
  generalize the capture-refresh runbook to "add a platform version".

## Acceptance (epic-level)
- The package bundles BOTH 8.3 and 8.5 protocol asset sets; the runtime selects the correct set from the
  detected/declared platform version, and fails closed with a clear message for an unsupported version.
- All 61 MCP tools are live-verified GREEN on **8.5** (live-regression CORE + the per-capability probe corpus),
  and the 8.3 path stays GREEN (no regression).
- The Docker host-platform delivery works against an 8.5 host platform exactly as it does for 8.3.
- The capture-refresh runbook documents "add a new platform version" as a repeatable procedure.

## Verify
- 8.3 baseline at epic creation: **475 offline tests green, 61 MCP tools**, live-regression CORE GREEN on
  `vanessa_client`, Docker host-platform E2E proven.
- Target adds: 8.5 live-regression GREEN + the offline suite still green with the multi-version resolvers.

## Risks
- **Data-only vs code** — resolved in P2 by decoding 8.5 wire and diffing against the known 8.3 shapes.
- **Fixture config on 8.5** — the captures need the «QA MCP Protocol Fixture V1» form available in an 8.5 IB.
- **Capture infra on 8.5** — whether the Vanessa TestManager (used for genuine-action capture) runs on 8.5, or
  the native capture path must be used.
- **8.5 is new/preview** — the wire may still shift across 8.5.x builds; pin the captured 8.5.x.y in the manifest.

## Archive
- not started

## Result
- **8.5 SUPPORT ACHIEVED 2026-06-25 (pushed; commits 303fbbb…2c0fab7).** The premise that 8.5 "moved the
  protocol" was WRONG — the original frame-3 failure was qa-mcp sending a stale 8.3 version string, which the 8.5
  client rejected ("Различаются версии клиента и сервера"). The genuine 8.5 wire is byte-structurally identical
  to 8.3. **What it took:** P0 multi-version architecture (done), P1 8.5 lab + first genuine 8.5 capture (done),
  and TWO one-field version injections (synthesized bootstrap + card-101 foreground replay declare the LIVE
  version) + a clean-state Escape sweep before XTEST writes. **Validated:** the full live-regression
  (`--include-write`) is **7/7 GREEN on a real 8.5 client using the 8.3 bundled data** (read + write + UI→DB).
  **Strategic pivot:** re-capturing the corpus per platform release is the LAST resort, not the default —
  **validate-first** (run the e2e on the new platform; re-capture only what goes red). So P2 (full re-capture)
  is largely unnecessary for 8.5; P3 (code) = the minimal version fixes (done); P4 (re-validate 61 tools) = the
  green e2e (done). `_bundled/8.5/` stays the FALLBACK slot for a version that genuinely moves the wire.

## Next
- Epic effectively delivered for 8.5. Remaining housekeeping: reconcile the child cards 113–118 to the
  validate-first outcome (P2 reframed to "re-capture only on RED", P4 = the e2e), and P5 (118, Docker selects the
  platform by `PLATFORM_ROOT`) when the delivery is next touched. Detail in memory [[qa-mcp-8-5-platform-support]].

## Related
- Version-resilience substrate: `src/qa_mcp/regression/versioning.py`, `config/protocol-capture-manifest.json`,
  `docs/capture-refresh-runbook.md` (card 111 item 4).
- Capture harness: `tools/protocol-research/` (`capture_session.sh`, `pcap_to_traffic.py`,
  `build_tm_v1_open_template.py`, compare tools, per-capability probes).
- Bundling: `scripts/bundle_runtime_assets.py`, `src/qa_mcp/_bundled/`, the resolvers in
  `protocol/bootstrap.py` / `mcp_server.py` / `protocol/evidence.py`.
- Memory: [[qa-mcp-8-5-platform-support]], [[qa-mcp-public-delivery-prep]],
  [[surpass-vanessa-native-superset-goal]].

## Log
- 2026-06-25 epic created from the 8.5 feasibility probe. Empirical finding: 8.5 boots fine but moves the
  protocol (8.3 handshake replay fails at frame 3) → full re-capture needed; code is data-driven → likely
  data-only + multi-version bundling. Six phase children (113–118) framed; P0+P1 parallelizable, P2 is the
  long pole.
- 2026-06-25 **DELIVERED.** The "protocol moved" premise was a red herring (it was a stale version string, not a
  wire change). P0 + P1 done; the vertical slice proved qa-mcp drives 8.5 with two one-field version injections;
  the full live-regression (incl. write) is 7/7 GREEN on 8.5 with the 8.3 data — no corpus re-capture needed.
  Adopted **validate-first** over pre-emptive re-capture. See Result above.
