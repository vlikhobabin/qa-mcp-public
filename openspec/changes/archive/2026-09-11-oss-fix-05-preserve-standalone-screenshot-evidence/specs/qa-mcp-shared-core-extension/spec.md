## ADDED Requirements

### Requirement: Standalone screenshot success retains readable image evidence
A successful screenshot through the unbound standalone application factory MUST
return a readable path whose file still contains the captured bytes after the
call. The unbound ledger's default policy MUST NOT be interpreted as admitted
project-bound raw-image deletion authority. Deliberate direct-call compatibility
MUST remain useful.

#### Scenario: Standalone screenshot uses default output
- **WHEN** the real unbound factory captures an image using default output selection
- **THEN** its returned path exists after the call and contains the exact captured bytes.

#### Scenario: Standalone screenshot uses explicit output
- **WHEN** the real unbound factory captures an image to an explicit relative or absolute output path
- **THEN** its returned readable path identifies that output and retains the exact image bytes.

### Requirement: Bound screenshot retention remains governed by admitted policy
Project-bound screenshot evidence MUST remain governed by the admitted evidence
root and sanitized or explicitly approved full_local policy. Standalone retention
MUST NOT grant raw-image retention to a bound application.

#### Scenario: Bound sanitized screenshot succeeds
- **WHEN** an exact admitted bound session captures an image under sanitized policy
- **THEN** the result retains safe artifact identity and digest without a raw path or image
- **AND** the raw captured image is removed from the admitted evidence location.

#### Scenario: Bound full_local screenshot succeeds
- **WHEN** an exact admitted bound session captures an image under approved full_local policy
- **THEN** only its authorized image remains in the admitted evidence root with matching content and digest.

### Requirement: Screenshot failures report evidence truthfully
Capture or required-cleanup failure MUST NOT claim successful readable evidence.
The failure path MUST preserve unrelated files and MUST NOT expose raw paths or
backend-secret prose in bound public results.

#### Scenario: Capture fails to produce readable evidence
- **WHEN** the synthetic screenshot backend fails or produces no readable image through a real factory tool
- **THEN** the tool reports failure without a successful readable artifact
- **AND** unrelated fixture files remain byte-identical.

#### Scenario: Sanitized cleanup fails
- **WHEN** required removal of a bound sanitized screenshot fails
- **THEN** the public result reports cleanup failure without a successful raw artifact/path
- **AND** unrelated files remain unchanged and the failed cleanup is not described as successful privacy enforcement.
