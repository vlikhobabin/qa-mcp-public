## ADDED Requirements

### Requirement: Protected build fails loudly on leaf-module surface drift

The protected thin-image build SHALL ship every non-`__init__` leaf module of the
shipped `qa_mcp` package either as a compiled native `.so` (with its `.py` source
removed) or as an explicitly dropped module, and SHALL fail the build with an
actionable, module-naming error when any shipped leaf `.py` remains readable.
The build's tool-count assertions SHALL agree on the true shipped tool count
across the protected-package stage smoke, the final-stage smoke, and the
standalone `docker/verify_protected_image.py` verifier.

#### Scenario: A newly added leaf module that is neither compiled nor dropped fails the build loudly

- **WHEN** the protected thin image is built and a shipped `qa_mcp` leaf module
  (for example `com_host.py` or `doctor.py`) is in neither the
  `docker/compile_modules.sh` compile list nor the `docker/Dockerfile.thin` drop loop
- **THEN** the build fails at the "no readable source" gate with an error that
  names the offending `.py` file(s) and points at both lists, rather than a
  cryptic empty-string test

#### Scenario: Tool-count assertions agree on the shipped surface

- **WHEN** the protected thin image is built from HEAD
- **THEN** the protected-package stage smoke, the final-stage smoke, and
  `docker/verify_protected_image.py` all assert the same true shipped tool count,
  and the build succeeds
