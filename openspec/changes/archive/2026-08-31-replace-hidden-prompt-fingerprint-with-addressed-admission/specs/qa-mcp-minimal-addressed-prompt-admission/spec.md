## ADDED Requirements

### Requirement: Prompt admission binds exact lifecycle identity
S5-R1 MUST begin from the unchanged S4 main-window identity and MUST admit one
security prompt only when its non-zero HWND, PID, lifecycle job, hidden desktop,
fixed class and owner-main HWND are exact, it was absent from the launch
baseline, and the same prompt identity is observed in two consecutive bounded
samples.

#### Scenario: One new lifecycle prompt becomes stable
- **WHEN** one new job-owned prompt on the requested hidden desktop remains
  owned by the exact S4 main HWND for two consecutive observations
- **THEN** S5-R1 evaluates target-action candidates from that prompt

#### Scenario: Prompt identity is stale, foreign or ambiguous
- **WHEN** the prompt is absent, old, duplicated or changes HWND, PID, job,
  desktop, class or owner
- **THEN** S5-R1 returns a typed refusal with zero focus, key and action calls

### Requirement: Admission selects one exact addressed action
S5-R1 MUST complete a bounded UIA traversal and MUST select exactly one action
whose PID, control type, predeclared structural path, enabled/visible/non-read-
only Invoke state, local relative selector and non-empty root/action geometry
identity match. A traversal or row-read failure, missing target, duplicate
target or malformed target identity MUST fail before action.

#### Scenario: One complete traversal yields one exact action
- **WHEN** traversal completes and exactly one candidate matches every target-
  action predicate
- **THEN** S5-R1 retains only its sanitized identity for immediate re-admission

#### Scenario: Target identity cannot be proved unique
- **WHEN** traversal is incomplete or the target is missing, duplicated,
  foreign, disabled, read-only, offscreen, non-invokable or malformed
- **THEN** S5-R1 refuses admission with zero focus, key and action calls

### Requirement: Whole-prompt fingerprint is diagnostic only
S5-R1 MUST NOT require a fixed total UIA control count, fixed total Invoke or
Value count, or fixed hash of the complete prompt topology. Those observations
MAY appear only as bounded sanitized diagnostics and MUST NOT change the
admission result when the exact prompt and unique target action remain equal.

#### Scenario: Unrelated controls drift harmlessly
- **WHEN** complete observations differ only in non-target control count,
  properties or whole-topology hash while the exact prompt/action tuple remains
  unchanged and unique
- **THEN** S5-R1 continues to immediate target re-admission

#### Scenario: Diagnostic drift affects target uniqueness
- **WHEN** inventory drift adds, removes or changes a target-action candidate or
  prevents complete enumeration
- **THEN** S5-R1 fails closed before action

### Requirement: Confirmation is freshly re-admitted and single-use
S5-R1 MUST repeat a complete traversal immediately before action and MUST
require the same exact main, prompt and target-action identity with a zero per-
run ledger. Only then MAY it perform one hidden-desktop-local focus followed by
one Return key-down/key-up pair addressed to the exact prompt HWND. It MUST set
the action-attempt ledger before the callback and MUST NOT retry.

#### Scenario: Fresh exact target receives one confirmation
- **WHEN** the prompt/action identity is equal across admission and immediate
  re-admission and the ledger is zero
- **THEN** S5-R1 records one attempt, one exact local focus and two messages to
  the exact prompt HWND

#### Scenario: Identity changes or the ledger is used
- **WHEN** main, prompt or target-action identity changes or any attempt is
  already recorded
- **THEN** no focus or key callback executes and no retry is permitted

### Requirement: Passive post-state proves addressed action outcome
After the addressed pair, S5-R1 MUST require the original prompt to close with
no replacement prompt, the exact main identity to remain, published S4 to
observe exactly one expected marker with stable topology, and zero operator-
desktop windows. Failure MUST return a typed result without another action.

#### Scenario: Prompt closes into exact S4 post-state
- **WHEN** one addressed confirmation closes the prompt and passive observation
  proves the unchanged main and exact marker/topology
- **THEN** S5-R1 returns one sanitized successful internal receipt

#### Scenario: Transition or passive post-state is unproved
- **WHEN** the prompt persists or is replaced, main identity changes, marker is
  missing or duplicated, topology changes or an operator-desktop window appears
- **THEN** S5-R1 fails without retry and preserves exact cleanup identity

### Requirement: Diagnostics and authority remain bounded
S5-R1 diagnostics MUST contain only typed response codes, bounded counts,
booleans and canonical hashes. Raw UI text, titles, automation identifiers,
coordinates, credentials, screenshots and exception details MUST NOT cross the
observer boundary or enter evidence. Production additions MUST remain at most
`300` physical lines, published S1-S4 MUST remain byte-identical, and the
primitive MUST have no non-test caller, Python/MCP/public/profile admission or
S6/S7 behavior.

#### Scenario: Bounded dormant scope is inspected
- **WHEN** privacy, LOC, predecessor, caller and forbidden-action gates inspect
  the candidate
- **THEN** only sanitized dormant S5-R1 policy/adapter behavior is present

#### Scenario: Content or authority escapes the boundary
- **WHEN** raw UI is retained, production scope exceeds the limit, predecessor
  bytes change or a public/forbidden action path appears
- **THEN** verification fails and independent review cannot start

### Requirement: Exact-source native proof separates prompt and contour facts
S5-R1 MUST compose from published
`81c60ef0254935a8683d7343016dfc8b88c3911e` plus only exact replacement paths.
It MUST use distinct fresh per-run EPFs for prompt-on and recovery proof and
MUST retain one addressed action, exact passive post-state and exact current-
run cleanup per run. Listener `18081` is unrelated diagnostic-only inventory:
S5-R1 MUST NOT connect to, restart, stop or reconfigure it, and its presence,
absence, ownership or independent drift MUST NOT gate prompt certification.

#### Scenario: Exact prompt and recovery proof passes
- **WHEN** the trusted Windows contour confirms one fresh prompt per run, one
  addressed action, exact S4 post-state, zero global input/desktop switches/
  operator-desktop windows and exact-owned cleanup without any S5 operation on
  unrelated listeners
- **THEN** evidence binds the exact source/artifact hashes and permits review

#### Scenario: Prompt, cleanup or contour integrity is unproved
- **WHEN** target identity, fresh fixture, action/post-state or exact-owned
  cleanup is missing or mismatched, or S5 attempts to operate on an unrelated
  listener
- **THEN** delivery records a typed blocker and cannot substitute stale,
  visible-desktop, synthetic or action-assisted evidence
