## Context

S1 publishes exact hidden-desktop process creation and S2 publishes a dormant
authenticated worker/job/TPort lifecycle. The unpublished investigation source
contains broader window, UIA, marker and prompt behavior, but S3 may adopt only
the read-only window-isolation slice and must compose cleanly from published
`c7a2c20...`.

The primitive is Windows-only at runtime, has no production caller and must fit
within `300` added production lines. It must not read window titles/text or
operator input, and it must not resolve or call any global-input, foreground or
desktop-switch function.

## Goals / Non-Goals

**Goals:**
- enumerate top-level HWND/PID/class/owner identity on one exact hidden desktop
  and on `Winsta0\\Default`;
- reject foreign, ambiguous and topology-drifted candidates through portable
  exact predicates;
- emit a sanitized isolation receipt with hashes/counts/booleans only;
- prove the primitive with synthetic owner topology and a real hidden 1C
  TestClient lifecycle on the exact Windows platform/target.

**Non-Goals:**
- marker, UIA, capture, chooser, prompt, form-open or post-state observation;
- any window/control/key/mouse action or desktop activation;
- public API, wire/profile, Python or stable route changes;
- S4-S7 implementation.

## Decisions

### Keep policy portable and Win32 enumeration separate

`hidden_desktop_window_isolation.go` defines bounded window identity,
predicate, receipt and fail-closed admission. A caller supplies a membership
predicate, so hostile unit tests can cover job ownership without Windows.
`hidden_desktop_window_isolation_windows.go` performs only `OpenDesktopW`,
`EnumDesktopWindows`, `GetWindowThreadProcessId`, `GetClassNameW`,
`GetWindow(GW_OWNER)` and S2 job-membership checks.

This separation keeps the decision logic deterministic and prevents synthetic
Windows tables from masquerading as native proof.

### Treat the newly created hidden desktop as an exact-owned boundary

The hidden inventory is invalid when it contains a non-zero PID outside the
exact lifecycle job. The operator inventory is invalid when it contains any
job-member window. Exact selection then requires one and only one candidate
matching non-zero PID, fixed case-insensitive class and exact owner HWND.
Missing, duplicate, foreign, outside-job, wrong-class or wrong-owner surfaces
return an error and no candidate.

Normal unrelated windows on `Default` are counted neither as owned nor as
foreign failures because only exact job membership defines the current run.

### Retain raw identity only in memory

Internal identity contains HWND, PID, class and owner HWND because later stages
must re-admit the same topology. The receipt never serializes raw class, title,
text, geometry or operator identity; it retains SHA-256 class hashes, bounded
counts and zero-input booleans. No title/text API is linked.

### Bind native evidence to published S2

The clean candidate starts from `HEAD:host-agent` and overlays exactly four S3
paths. One native case runs a synthetic listener child that creates an empty
`Static` root and owned popup on the S2 hidden desktop, proving class/owner
selection and cleanup. A second case launches platform `8.3.27.2214` as an
actual TestClient against the declared `vanessa_client`, proves at least one
job-owned hidden window and zero job-owned `Default` windows, then closes the
exact S2 lifecycle. Neither case activates the desktop or sends UI input.

### Use explicit source and runtime zero-input oracles

Portable source guards reject references to `SendInput`, `SetCursorPos`,
`SetForegroundWindow`, `SwitchDesktop`, `mouse_event`, `keybd_event`,
`PostMessage`, `SendMessage` or UIA/action helpers in the S3 production files.
The native receipt must keep global-input and desktop-switch counters at zero.

## Risks / Trade-offs

- [HWND reuse after inventory] -> S3 authorizes no action; S4/S5 must re-enumerate
  and re-admit exact identity before their own observation/action boundaries.
- [Platform class topology changes] -> class/owner predicates fail closed and
  native evidence becomes non-pass; no class is inferred from title/text.
- [Foreign helper appears on the hidden desktop] -> the isolation receipt fails
  rather than silently excluding it.
- [Real TestClient target is unavailable] -> record a typed verification
  blocker; synthetic proof cannot replace the required real-platform case.
- [Receipt hashes are mistaken for user content] -> hash only Win32 class names;
  never request titles, text, controls, geometry or screenshots.

## Migration Plan

No runtime migration is needed because the primitive remains dormant. Publish
only after clean composition, exact-source Windows proof, exact cleanup and a
fresh ordinary/high review. Rollback is removal of the four S3 files and its
capability artifacts; S1/S2 behavior remains unchanged.

## Open Questions

None for S3. Marker/UIA topology and observation semantics are intentionally
deferred to S4.
