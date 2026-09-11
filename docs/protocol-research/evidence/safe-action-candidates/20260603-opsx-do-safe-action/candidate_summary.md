# Safe Action Candidate Manifest 20260603-opsx-do-safe-action

This manifest selects the first non-mutating action candidate for live protocol
capture: activating an already-open internal TestClient window through the
Vanessa `activate_window` tool.

The action is permitted by `docs/protocol-research/safe-ui-action-scope.md`
because it changes transient active-window state and does not invoke a business
command, enter text, toggle values, edit tables, save, post or delete data.

## Candidate

| Case id | Action | Target | Replay status before capture |
| --- | --- | --- | --- |
| `safe-activate-existing-window` | `activate_window` | Existing internal TestClient window selected at runtime | `pending` |

## Prerequisite Gates

| Gate | Status | Decision |
| --- | --- | --- |
| Safe action scope | implemented | Candidate uses allowed `activate_window` family. |
| Action event contract | implemented | Manifest includes pre-state, action, post-state, recovery and result marker fields. |
| Controlled fixture families | deferred/unresolved | Not required for existing-window activation; cannot prove action frame behavior. |
| Read-only element hash gaps | deferred/unresolved | Not required for window activation; cannot promote element actions. |

## Evidence Boundary

The live capture may produce a pending row if the first analyzer pass cannot
join the Vanessa `activate_window` call to a precise native frame range. That
is an unresolved protocol outcome, not an accepted mapping.
