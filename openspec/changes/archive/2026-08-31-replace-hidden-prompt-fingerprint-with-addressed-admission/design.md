## Context

Published S1-R1 through S4 provide exact hidden-desktop process ownership,
worker/job/TPort lifecycle, top-level-window isolation and passive main/marker/
UIA observation. The unpublished S5 candidate adds prompt confirmation but
requires exactly `26` UIA controls, exactly `5` enabled visible Invoke controls,
zero enabled visible Value controls and a fixed hash of every prompt row.

The authorized fresh-EPF micro-fix caused the expected prompt to appear, then
failed at that complete-inventory gate before focus, key delivery or action.
The result does not show that the exact target action was unsafe; it shows that
the observer currently cannot distinguish harmless full-tree drift from a
target-action ambiguity. S5-R1 therefore narrows admission to facts that can
affect the addressed action.

This change does not alter the TestClient protocol, capture tools or replay
logic. There are no protocol frame ranges or dynamic protocol fields. Dynamic
HWND, PID, desktop, action and geometry identity remains in memory; retained
evidence contains only typed outcomes, counts, booleans and hashes.

## Goals / Non-Goals

**Goals:**

- admit exactly one new lifecycle-owned prompt after two consecutive equal
  bounded observations;
- identify exactly one enabled, visible and invokable target action using its
  exact PID, structural path and local relative selector;
- re-admit the same prompt/action immediately before one addressed action;
- ignore harmless changes to non-target prompt controls while failing closed
  when enumeration completeness or target uniqueness cannot be proved;
- require prompt transition and the exact passive S4 post-state;
- retain sanitized cause-level diagnostics and exact-owned cleanup evidence.

**Non-Goals:**

- admitting by raw title, name, localized text, OCR or screenshot;
- chooser, global input, cursor/mouse, foreground activation or desktop switch;
- retrying an action or weakening exact PID/job/desktop/main-owner binding;
- Python/MCP/public route, receipt binding, stable certification or S6/S7;
- connecting to, repairing, restarting, stopping or reconfiguring unrelated
  listener `18081`.

## Decisions

### Separate the safety selector from diagnostic inventory

The observer completes one bounded UIA traversal rooted at the exact prompt and
reports whether enumeration completed. Admission examines only:

- the exact prompt HWND/PID/job/desktop/class/main-owner tuple;
- target-action candidates with the exact PID, button control type and
  predeclared structural path;
- enabled, visible, non-read-only Invoke capability;
- the predeclared bottom-region/local horizontal selector;
- non-empty root/action geometry hashes.

The candidate selector must yield exactly one action. Total row count, total
Invoke/Value counts and the hash of all rows remain sanitized diagnostics but
are not admission predicates. A traversal/row-read failure remains fatal
because it could hide a duplicate target action. Foreign or unrelated fully
observed rows do not reject the exact target.

Keeping the `26/5/0` totals as tolerances or versioned fingerprints was
rejected: it would retain the same false-negative class and create recurring
per-build certification work without strengthening target selection.

### Use two equal admission snapshots with bounded readiness

The worker observes until it obtains two consecutive equal prompt/action
identities within the existing bounded readiness window. The second observation
is the immediate pre-action re-admission; no third stability traversal is
required. Equality covers the exact prompt tuple and selected action path,
local selector and root/action geometry. Non-target inventory diagnostics may
differ.

Three samples were useful during investigation but do not add a distinct
safety fact after exact ownership, uniqueness and immediate re-admission are
enforced. A single sample was rejected because replacement between discovery
and action would be insufficiently guarded.

### Re-admit the target, not the whole window

The second consecutive observation occurs immediately before action and must
yield the same exact prompt and one identical target action while the per-run
ledger is zero. Only then may the existing hidden-local focus plus exact-prompt
`WM_KEYDOWN`/`WM_KEYUP` Return pair execute. The ledger moves to one before the
callback, and no failure path retries.

The complete inventory hash is deliberately excluded from equality. A change
to an unrelated label or container cannot redirect an action that remains
uniquely selected by exact path, local rank, PID and geometry.

### Treat post-state as the final action oracle

Queued addressed messages alone do not prove confirmation. Success requires
the original prompt to disappear without replacement, the exact main identity
to remain, published S4 to observe the expected unique marker/stable topology,
and zero operator-desktop windows. Failure returns a typed outcome without a
second action.

### Diagnose without retaining UI content

The Windows adapter returns a bounded internal diagnostic with a response code,
enumeration-complete boolean, observed row count, valid-hash boolean, exact-PID
row count, target-candidate count and bounded topology/action hashes. It never
retains raw names, titles, automation identifiers, coordinates, credentials,
PowerShell exception text or screenshots.

This is sufficient to distinguish command/runtime failure, incomplete
enumeration, malformed response, target absence and target ambiguity without
reintroducing full fingerprint admission.

### Keep unrelated listener inventory diagnostic-only

Before and after a Windows run, bounded inventory may record whether listener
`18081` is present. S5-R1 never connects to, restarts, stops or reconfigures
it. Its presence, absence, unknown ownership or independent drift is retained
only as a diagnostic and does not decide prompt admission, cleanup success or
native certification.

## Risks / Trade-offs

- [A duplicate action is hidden by an incomplete UIA traversal] -> require a
  completed bounded traversal and fail closed on any traversal or row-read
  failure before evaluating uniqueness.
- [A platform build changes the target action path or local selector] -> fail
  closed and require reviewed exact-source evidence for that target identity;
  do not fall back to text or whole-window guesses.
- [Action geometry changes harmlessly between runs] -> geometry is dynamic per
  run but must remain identical across the two admission snapshots and the
  immediate re-admission; a new run may establish a new in-memory geometry.
- [Fewer stability samples admit a transient prompt] -> exact ownership,
  uniqueness, two consecutive samples and immediate re-admission preserve the
  temporal boundary while reducing unnecessary delay.
- [Unrelated listener state changes independently] -> retain the bounded
  diagnostic, prove S5 issued no operation against it and continue evaluating
  only exact-owned cleanup.
- [Dirty combined payload contaminates replacement scope] -> clean-compose
  from published S4, overlay only the four isolated S5-R1 paths and stage only
  the delivery manifest.

## Migration Plan

There is no public migration because the primitive remains dormant. Delivery
replaces the unpublished four-file S5 candidate in the scoped composition,
syncs only the new minimal-addressed capability and archives only this change.
Rollback removes those isolated paths and artifacts; published S1-S4 and the
public profile remain unchanged.

## Open Questions

- None for implementation. Listener ownership is unrelated diagnostic context;
  unknown ownership or independent drift is explicitly non-gating for S5.
