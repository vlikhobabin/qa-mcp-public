# 94. 🚩 Validate capture-free synthesis on ANOTHER config (lab-demo → product boundary)

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): folded into **card 98** (Product boundary) as **change 5 — the 🚩 GATE** on the
  "100% replacement" claim. The full plan below is preserved as working detail; card 98 is the active surface.

## Order Index
94

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-17 (next-epic roadmap E4): **EVERYTHING so far is proven on ONE config** —
  `ФикстураПротоколаTestClient` in `vanessa_client`. To truly replace the standard Test Manager in REAL
  projects we must drive forms in other configs. Element addressing is by-NAME (generic), but three things are
  UNPROVEN: (1) is `bootstrap_synth` (the handshake) config-agnostic, or does it encode fixture/infobase
  specifics? (2) do the per-type genuine templates (captures) replay against ARBITRARY forms/configs, or is a
  per-config capture needed? (3) can we read a FOREIGN form's descriptor well enough to know field names+types?
  (Card 87 "form introspection" is the independent piece.)

## Summary
Validate the capture-free synthesis against ≥1 real (non-fixture) config; classify every shipped action as
"generalizes as-is / needs a per-config capture / fixture-only"; produce a per-config onboarding recipe. **This
card GATES the "100% replacement" claim** — it is the boundary between a lab demo and a product.

## Acceptance
- A native TestClient stood up against a 2nd config in the lab (`/opt/1c-dev/{demo10413, redacted-third-party-config,
  demo_1_0_41_3}`), the IB FREE (mind apache/W^X — [[ibsrv-odata-vs-httpservice]]).
- READ first: `read_active_window` / `read_form_value(field)` against a form there — does the read path work with
  NO fixture-specific capture? Documented.
- WRITE: `write_form_value` into a field of a foreign form — does the genuine string-SET template replay (only
  GUIDs differ), or is a per-config SET capture needed? Documented.
- A **generality matrix**: every shipped action ✅ generalizes / ⚠ needs a per-config capture / ❌ fixture-only.
- A **per-config onboarding recipe**: the minimal captures a new config needs (if any).
- The capture-free claim restated honestly ("universally capture-free" vs "per-config-capture-free after a
  one-time connect capture"). Evidence note / validation report.

## Notes / constraints
- The handshake may carry config metadata (infobase id, config version/hash) → a per-config connect capture may
  be required; if so, that is the per-config onboarding cost.
- Foreign forms may use element kinds/controls not yet decoded.
- Licensing / W^X / exclusive access per IB (lab notes: [[ibsrv-odata-vs-httpservice]], [[lab-infobase-access]]).
- Relates to card 87 (general form introspection) — reading a foreign form's descriptor.

## Plan for the new session (start here)
Read `docs/protocol-research/capture-free-epic-next-roadmap.md` **§E4**.
1. Pick a 2nd config; stand up a native client (free IB); try `read_active_window` capture-free.
2. Try `write_form_value` into a foreign field; identify what (if anything) is fixture/config-specific.
3. Build the generality matrix + onboarding recipe; write the validation report.
