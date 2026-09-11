# Shared-core extension contract

qa-mcp exposes a product-neutral Python seam for standalone runtimes and
downstream products. The public core owns TestClient protocol/scenario
semantics; a downstream supplies primitive execution without copying the MCP
tool layer or importing its implementation into this repository.

## Composition root

Use `qa_mcp.mcp_server.create_mcp_server` instead of mutating the compatibility
module-global server:

```python
from qa_mcp.config import Settings
from qa_mcp.mcp_server import create_mcp_server

server = create_mcp_server(
    settings=Settings.from_env(),
    executor=my_executor,
    tool_profile="standalone",
)
```

Each call creates an independent `ApplicationContext` containing settings,
executor, optional immutable runtime-target resolution, target/session identity,
attachment state, scenario-result log, a sealed operation-schema catalog and an
application-owned evidence ledger.
Context-bound tools cannot read or clear another server instance's state.
The `qa_mcp.mcp_server.mcp` object remains the complete compatibility surface
for existing imports; the CLI constructs a fresh standalone application.

### Display and host-agent configuration ownership

Composed display and host-agent lifecycle calls use only the active
`ApplicationContext.settings`.  That includes display mode, remote address and
token, compatibility pins, timeout, window selector, and native TestClient
port.  Each lifecycle operation constructs or binds its backend from the
current admitted attachment, so replacing an attachment cannot retain a
previous application's target; stopping one application cannot signal or clear
another application's attachment.

An explicitly absent remote address remains absent: composed availability and
configuration errors never inherit a process host or fall back to local X11.
Public diagnostics describe the selected application mode with bounded,
secret-safe text: typed host-agent failures retain only locally allowlisted
codes and HTTP-range integer status values. Unknown codes, including well-formed
identifiers, become the constant `host-agent-error`; the public boundary never
serializes a host-agent response body, transport cause, token or private
configuration. Failed launches may additionally return a validated cleanup
identity (PID, native port and lifecycle handle), so an owned process can still
be stopped. Ownership, matching identifiers and the handle shape are checked;
untrusted payload fields and configured secrets are not copied into that handle.
Direct legacy callers may continue to use the explicit
environment-backed display adapters; those adapters are outside application
composition and retain their existing pin, timeout, and port semantics.

The same ownership applies to list refresh and clean-state sweep errors,
uncertain-zero classification, and window/visible-cell diagnostics. A remote
application enables those diagnostics even when process mode is local; a local
application does not enable them merely because process mode is remote.
Typed failures share the public serializer used by direct display tools.
Generic display failures use a fixed diagnostic instead of exception prose.
Legacy direct-call diagnostics still select mode through their environment
adapter, with the same bounded public error contract.

The routing proof for this boundary is offline only: real application factories
are exercised against fake HTTP/X11/socket/signal boundaries, including nested,
interleaved, and exceptional contexts.  It does not qualify a Linux or Windows
native desktop runtime.  Final-source native qualification remains owned by
FIX-11/FIX-12 under separately authorized runtime preflight and evidence.

### Workspace and lifecycle ownership roots

Composed factory calls resolve ordinary capture/template lookup and default
runtime output from their active `Settings.home`, never from another
application's process environment. An explicitly empty `home` selects the
static package/repository fallback; only deliberately unbound direct helpers
retain the environment-backed `QA_MCP_HOME` adapter.

Lifecycle ownership is separate: `QA_MCP_TESTCLIENT_OWNERSHIP_ROOT`, when set
on the active Settings, takes precedence. Otherwise the lifecycle root is
`<home>/runtime/protocol-research/testclient-lifecycle`, or its documented
static fallback for empty Settings. Composed local launches place their output
and marker below that ownership root, so a later stateless stop discovers the
same marker after process-environment drift. This boundary neither scans other
application roots nor changes PID, start-tick, process-group, target/session,
or unowned-process refusal checks. Runtime-target evidence roots and retention
policy remain separately admitted and are not workspace fallbacks.

### TestClient relay transport configuration ownership

Composed native transport and relay-listener readiness resolve relay endpoint
and token only from the active `ApplicationContext.settings`.  Each factory
therefore keeps its own relay destination and authentication even when the
process environment names a different relay.  A factory with neither relay
field remains direct; it does not inherit a process relay.  Partial, malformed,
or preface-unsafe scoped fields fail before a socket is opened, and public
errors do not expose relay tokens or peer reply text.

Authentication is sent only to the exact configured relay endpoint.  A direct
endpoint receives no relay preface, while listener-only readiness connects and
closes without authentication, TestClient protocol bytes, or manager-session
acquisition.  Application activation restores the preceding transport scope on
nested, asynchronous, threaded, and exceptional exits without changing process
environment or another application's attachment.

The low-level transport helpers retain their explicit environment-mapping
adapter for direct legacy callers outside application composition.  An active
application scope is authoritative and cannot be overridden by that adapter.
The factory/socket checks for this contract are hermetic offline evidence only;
they do not certify a live Linux or Windows TestClient or relay.

Project-bound startup may pass a validated `RuntimeTargetResolution` through
`runtime_target`, or an explicit provider handoff mapping through
`runtime_target_env`. The latter is resolved exactly once during composition;
an absent handoff leaves the application unbound and a malformed handoff stops
startup with `RuntimeTargetBindingError`. The CLI uses its process environment
as that explicit mapping. Doctor reports `runtime_target_binding` first and
exposes only logical identity, evidence policy and observation fingerprints—
never provider-local paths, credentials or connection values. Composition and
this readiness check do not launch or attach a TestClient.

## Public contracts

`qa_mcp.core` exports:

- `TargetIdentity` and `SessionIdentity`: logical, secret-free identities;
- `OperationRequest`, `OperationKind` and `QAExecutor`: read, write, lifecycle
  and display primitives rather than one handler per MCP tool;
- `OperationResult`, `OperationVerdict`, `OperationError` and
  `ArtifactReference`: one result taxonomy for MCP and scenario paths;
- `LocalQAExecutor` and `WindowsHostQAExecutor`: adapters over explicit
  primitive handlers;
- `RuntimeTargetResolution`, `resolve_runtime_target` and
  `runtime_target_readiness`: frozen provider resolution and secret-safe,
  non-mutating readiness serialization;
- `execute_mcp_operation` and `execute_scenario_operation`: two entrypoints
  that delegate to the same operation implementation and verdict taxonomy.

The registered `get_window_list` primitive is the compatibility seam for the
legacy display helper: its trusted adapter translates that helper's typed
failure dictionary into an `OperationResult.FAILURE` before the composed
boundary. Generic `HandlerQAExecutor` dispatch remains data-preserving, so an
unrelated successful dictionary containing keys such as `ok` or `error` is not
treated as a failure. Direct unbound helper calls retain the documented legacy
inventory and error dictionaries.

## Positive operation result boundary

R7 adds the direct core normalizer and R8 integrates it into the MCP and
ScenarioRunner operation entrypoints. `ApplicationContext` composes
its `operation_schemas` and `evidence_ledger` itself. Neither is a constructor
input: the catalog is a read-only mapping of sealed source rules, while the
ledger root/policy comes only from the validated immutable runtime-target
binding (or the sanitized unbound default).

The public primitives are:

- `OperationFieldClass` and `OperationProvenance` for the finite class catalog
  and admitted logical identity;
- `admit_operation_provenance(...)` for exact logical operation, target,
  optional session, binding, lowercase SHA-256 fingerprint, positive signed
  64-bit generation and evidence-policy admission;
- `EvidenceLedger`, `EvidenceScope` and `EvidenceReceipt` for context-local,
  current-operation artifact authority;
- `normalize_operation_result(context, request, raw, provenance, ...)` for
  closed positive reconstruction into a total `OperationResult`.

The source schema selected by exact `read_active_window` identity is a finite
observation: `value.window_state` is one of `observed`, `missing` or
`ambiguous`, `value.marker_count` is a bounded reference count, and an
explicit request may add the boolean `value.assertion_passed`. Raw window
references, markers, captions and paths never cross this boundary. The shared
error-details schema retains the existing finite-class, URL and receipt
protections; unknown keys are omitted without reading their values and any
declared wrong class/subclass or invalid domain yields fixed
`invalid-executor-result`.

Bound window assertions use the admitted boolean even when it is missing; a
missing boolean fails the assertion without searching the public preview.
Malformed native fields or a success result carrying an error retain
`invalid-executor-result`; mapping/marker collection overflow retains
`result-too-large`. An unsuccessful native status remains `executor-failure`.

For screenshot capture, the sanitized policy applies only after a runtime target
has been admitted. The unbound standalone factory retains its returned image so
legacy/direct callers can read it; standalone retention does not grant any bound
raw-image authority. Sanitized artifacts never include `path`. Approved `full_local` output requires
one current receipt from the exact context ledger and operation scope. Receipts
are registered by the trusted screenshot producer against its fresh destination
and actual SHA-256 bytes; executor-returned paths and hashes cannot mint them:

The following explicit low-level API is a trusted registration call, not an
executor result claim. It snapshots the actual file hash and identity. An omitted
optional artifact hash stays compatible here; a supplied hash must match. Shared
screenshot results always require the exact producer hash. Only the source-owned
screenshot producer allocates and automatically cleans its own temporary files.

```python
from qa_mcp.core import admit_operation_provenance, normalize_operation_result

provenance = admit_operation_provenance(
    operation="read_active_window",
    target="project.demo",
    session="session-1",
    binding="qa.demo",
    fingerprint="sha256:" + "a" * 64,
    generation=1,
    evidence_policy=context.evidence_ledger.policy,
)

with context.evidence_ledger.operation() as scope:
    receipt = scope.record("screenshot", owned_screenshot_path)
    public_result = normalize_operation_result(
        context,
        request,
        executor_result,
        provenance,
        scope=scope,
        receipts=(receipt,),
    )
```

Receipts are valid only while that scope is active, for the exact ledger,
artifact id, actual content hash/file identity and canonical non-symlink path
strictly below the frozen root. Shared capture validates before scope cleanup:
sanitation removes only its allocated raw file and leaves the verified digest in
the result; full_local retains the current readable file. A failed operation also
cleans its own allocated file, and cleanup failure cannot report success.
Hash validation describes completion, not permanent filesystem immutability.
Executor path, callback, schema or receipt-like data grants no authority.

Reconstruction bounds admitted containers to depth 8 and 64 items, shares a
512-node budget across value/error/artifacts, limits admitted strings and
receipt paths to 2,048 Unicode scalars, and finally limits the complete compact
sorted DTO to 65,536 UTF-8 bytes. Structural or final aggregate overflow uses
fixed `result-too-large`; invalid receipts use fixed
`invalid-evidence-receipt`. Documentation URLs must converge within four
separate authority/path decode rounds to canonical public HTTP(S), with no
userinfo, private/local address, credential assignment, query or fragment.

Every native-session-bound operation, independently of the sealed positive
result-schema catalog, first admits the immutable binding provenance and checks
the current target/session/attachment/generation tuple. Explicit host, port or
display arguments must match that attachment exactly. A missing, malformed or
mismatched route returns fixed `runtime-target-route-blocked` before hidden
provider callbacks, endpoint probes, display callbacks, either Local or Windows
adapter, or protocol work. Unknown operations in a bound application fail
closed; schema membership controls result normalization only, never permission.
Only after route admission does the application open one evidence scope, invoke
the adapter once and normalize a declared result once; the scope closes in
`finally`. Executor failure, serialization and fallback never retry or change
route/path authority.

Each registered public tool is classified as native-session-bound, lifecycle,
provider-data or pure/readiness. Lifecycle tools retain their dedicated
launch/attach/status/cleanup policy, while provider-data and pure/readiness
tools retain their own contracts without acquiring native-session authority.
Declared unbound contexts retain explicit compatibility behavior. In particular,
R8 adds no lifecycle attachment authority and no MCP tools or wire fields.
FastMCP extensions use `execute_mcp_operation`; ScenarioRunner uses
`execute_scenario_operation` and records the normalized DTO in its step preview
or bounded error text, so both paths expose the same trusted provenance and
verdict taxonomy.

The contracts intentionally contain no product environment, relay, tenant,
registry or private transport model. A logical target may carry public opaque
metadata, but raw credentials and physical connection ownership remain outside
the models. Immutable descriptor binding is owned by the follow-up
`oss-04-bind-testclient-to-declared-project-runtime-target` card.

## Tool profiles

`standalone` is the current pre-stable CLI-default runtime catalog. `research`
is explicit and contains the complete compatibility surface. Tools omitted
from either code-level catalog are not registered and therefore do not appear
as structured-unavailable placeholders. The selected name/schema surface is
pinned by deterministic digest tests.

Stable release support is a narrower contract than the current pre-stable
catalog: the I16 release decision also omits `open_external_processor`, leaving
63 tools in the declared stable standalone support profile. The dormant tool
remains registered in the unchanged 64-tool pre-stable `standalone` catalog so
its implementation/tests/foundations are preserved; catalog membership is not
stable admission. A later release/cutover change MUST enforce the declared
63-tool stable allowlist and its public support assertion before promotion, or
the release fails closed.

Current research-only tools are:

- `echo_jsonrpc_arguments`;
- `generate_smoke_suite`;
- `autofill_required_fields`;
- `measure_scenario`.

Set `QA_MCP_TOOL_PROFILE=research` only for an explicit research runtime. A
downstream may add context-bound tools through the `extra_tools` argument, but
a name collision with a public tool fails during composition. A bound extension
is blocked by default. The only explicit bound extension classification is
`extra_tool_classes={"name": "shared-operation"}`: it may compose
`execute_mcp_operation`, whose own admission still controls every native route.
That classification is not permission for direct native/protocol/display work;
unknown or unclassified bound extensions fail before their callback. Intact
unbound extension contexts retain their compatibility behavior.

## Compatibility and contribution policy

The first public contract is a compatibility candidate until the initial
open-source stable release. Changes to names, required fields, verdicts or
profile membership require an OpenSpec delta, contract-test update and release
note. Existing protocol templates, replay algorithms, lifecycle ownership and
mutation authority are not extension points.

Generic protocol, scenario, result-model and executor corrections are made in
public qa-mcp first. Downstream products adopt a released semantic version and
run the public consumer contract; they do not cherry-pick a private fork back
into the core. Product-specific transports and integrations stay in their
owning repositories and depend inward on this contract.
