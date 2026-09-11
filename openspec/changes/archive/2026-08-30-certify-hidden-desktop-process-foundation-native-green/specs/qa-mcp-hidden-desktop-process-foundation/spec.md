## MODIFIED Requirements

### Requirement: Desktop and process creation remain exact-owned
On Windows, the foundation MUST create only the validated named desktop, MUST
launch the exact absolute executable with that explicit desktop and no
inherited handles or visible console.

#### Scenario: Exact hidden child starts successfully
- **WHEN** a native focused test supplies a valid identity, exact worker
  executable and bounded environment
- **THEN** the child starts on the named hidden desktop without a visible
  console and all current-run handles are closed exactly

#### Scenario: Desktop or process creation fails
- **WHEN** a native creation operation fails
- **THEN** only handles created by that call are closed and no unrelated
  process, desktop or input surface is touched

#### Scenario: Process termination fails during exact cleanup
- **WHEN** cleanup of a just-created exact process encounters a termination
  failure
- **THEN** the foundation attempts both exact thread and process handle closes,
  clears only successfully closed handles, joins the cause, termination and
  close errors, and touches no unrelated handle
