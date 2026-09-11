# Write-Frame Decode Findings (Warehouse "Не использовать" toggle)

Two independent reference captures of the same real mutation, compared by
`tools/protocol-research/compare_probe_reference.py` (mode `stability`):

- `mut-warehouse-donotuse-20260610` (first)
- `mut-warehouse-donotuse-20260611-repeat` (repeat)

Verdict: **`fully_stable`** — `structural_match=True`, `typed_result_match=True`,
`all_hashes_match=True`, `residual_dynamic_bytes=0`. The write-frame normalizer is
now complete and the two runs are byte-identical after normalization. Report:
`stability_first_vs_repeat.json`. The acceptance-gate mechanism was validated on
the same data (`acceptance_gate_demo.json` → `accepted`).

## Structural stability (proven)

The `action_write` phase is **byte-for-byte structurally identical** across the
two runs:

- 28 frames both runs (14 `manager_to_client` + 14 `client_to_manager`);
- every frame has the **same size** in both runs, frame-for-frame;
- the same typed effect both runs (`Нет` → `Да` → `Нет`).

This proves the write is a deterministic, repeatable protocol exchange — the
prerequisite for decoding a stable template.

## Dynamic-field inventory of the write frames

The remaining cross-run differences are localized to a small, characterized set
of dynamic fields (this is the input for the Python-manager write template):

| Field | Where | Length | Kind | Notes |
| --- | --- | ---: | --- | --- |
| frame token | offset 2 | 4 B | per-frame counter | session base + per-frame increment (`3a..47` run A, `e7..f4` run B); repeated throughout each frame |
| session GUID | `manager_to_client` offset 6 | 16 B | per-session uuid (binary LE) | constant within a run (A=`dc13ed4a…`, B=`6026304c…`), repeated; the manager/connection id |
| nonce(s) | `client_to_manager` offset ~30 | 16 B | per-frame random | differ every frame and every run — random by design |
| UI-path GUIDs | ASCII text | 36 B | per-session | `SecondaryFrame[…]`, `ManagedForm[…]` — already normalized |

The complete, verified dynamic-field map of the write command frames:

| Field | Offset | Length | Kind |
| --- | ---: | ---: | --- |
| message id | 2 | 16 | per-frame UUID |
| sequence | 19 | 2 | uint16 LE |
| nonce | 68 (manager) / 30 (client) | 16 | per-frame, varies across runs |
| session GUIDs | located | 36 / 72 | ASCII + UTF-16LE path text |

Encoded in `compare_probe_reference.py` (`normalize_payload`) and in the write
template `write_template_fieldmap.json` (compact; full `body_hex` template under
ignored `runtime/protocol-research/templates/`).

**Note (2026-06-11):** a package-native probe initially mismatched live and the
offset-68 field was briefly suspected. That was disproven: the rendered write
frames were verified **byte-identical to the accepted replay frames** (render
leaves zero stale captured GUIDs in any encoding, and equals
`rebinder.apply(captured)` offline). So the write-frame field map above is
correct and offset-68 is an ordinary per-frame field. The native live mismatch
is a separate cross-session reproduction issue (see
`python_manager_native_step.md`), not a frame-construction error.

## What this unblocks and what remains

- **Done:** the write exchange is deterministic; its dynamic fields are fully
  decoded; two reference runs reach `fully_stable` (byte-identical normalized
  hash); the comparator grades both stability and acceptance; the acceptance
  gate returns `accepted` on a reproducing run; the Python manager can
  **construct** a write command frame from the template
  (`qa_mcp.protocol.mutation.render_write_frame`, unit-tested).
- **Remaining for an accepted mapping (one live step):** drive the rendered
  write frames from the Python manager directly against a TestClient (replacing
  the Vanessa manager), capturing the probe, then run
  `compare_probe_reference.py --mode acceptance` against these references. A
  `fully_stable`/`accepted` verdict from a **Python-manager-driven** probe
  promotes `TestedFormButton.Click` from `candidate` to accepted in
  `mutation-evidence-map.json` and the scope tracker. Until then the mapping
  stays `candidate` — the gate has only been validated reference↔reference.

Raw streams, parsed frames and the full `body_hex` template stay under ignored
`runtime/protocol-research/`; only this compact characterization is in reviewed git.
