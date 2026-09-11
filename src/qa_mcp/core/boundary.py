from __future__ import annotations
import contextvars, hashlib, ipaddress, json, math, os, re, stat, tempfile, threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Iterator, Sequence
from urllib.parse import quote, unquote_to_bytes, urlsplit, urlunsplit
from .contracts import (ArtifactReference, OperationError, OperationKind, OperationRequest,
                        OperationResult, OperationVerdict)
_PROVENANCE_SEAL, _SCHEMA_SEAL = object(), object()
_CURRENT_EVIDENCE_SCOPE: contextvars.ContextVar["EvidenceScope | None"] = contextvars.ContextVar(
    "qa_mcp_evidence_scope", default=None
)

def _current_evidence_scope() -> "EvidenceScope | None":
    return _CURRENT_EVIDENCE_SCOPE.get()

_PATH_TYPE, _PROXY_TYPE = type(Path()), type(MappingProxyType({}))
_LOGICAL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
_OPERATION = re.compile(r"[a-z][a-z0-9_.-]{0,63}")
_FINGERPRINT = re.compile(r"sha256:[0-9a-f]{64}")
_ARTIFACT = re.compile(r"[a-z][a-z0-9._-]{0,127}")
_MEDIA = re.compile(r"[a-z0-9][a-z0-9.+-]{0,62}/[a-z0-9][a-z0-9.+-]{0,62}")
_SHA, _BAD_PERCENT = _FINGERPRINT, re.compile(r"%(?![0-9A-Fa-f]{2})")
_CREDENTIAL = re.compile(r"(?i)(?:password|passwd|pwd|secret|token|api[_ -]?key|private[_ -]?key|credential|authorization|connection(?:string)?|data[ _]?source|user[ _]?id|server)\s*[:=]")
_DOC_NETWORKS = tuple(ipaddress.ip_network(v) for v in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "2001:db8::/32"))
class OperationFieldClass(str, Enum):
    BOOLEAN = "boolean"; INT64 = "int64"; FINITE_NUMBER = "finite_number"
    REFERENCE_COUNT = "reference_count"; LITERAL_TEXT = "literal_text"
    DOCUMENTATION_URL = "documentation_url"
class OperationBoundaryError(ValueError):
    """Typed rejection carrying only a fixed public code."""
    def __init__(self, code: str = "invalid-operation-provenance") -> None:
        self.code = code; super().__init__(code)
class _TooLarge(Exception): pass
@dataclass(frozen=True)
class OperationProvenance:
    operation: str; target: str; session: str | None; binding: str
    fingerprint: str; generation: int; evidence_policy: str
    _seal: object = field(default=None, repr=False, compare=False)
    def to_dict(self) -> dict[str, Any]:
        result = {"operation": self.operation, "target": self.target, "binding": self.binding,
                  "fingerprint": self.fingerprint, "generation": self.generation,
                  "evidence_policy": self.evidence_policy}
        if self.session is not None: result["session"] = self.session
        return result
_BOOL, _INT = ("leaf", OperationFieldClass.BOOLEAN, ()), ("leaf", OperationFieldClass.INT64, ())
_NUMBER, _COUNT = ("leaf", OperationFieldClass.FINITE_NUMBER, ()), ("leaf", OperationFieldClass.REFERENCE_COUNT, ())
_LABEL, _URL = ("leaf", OperationFieldClass.LITERAL_TEXT, ("Reference label 7",)), ("leaf", OperationFieldClass.DOCUMENTATION_URL, ())
_COMMON = ("object", (("active", _BOOL), ("sequence", _INT), ("duration", _NUMBER),
                      ("referenceCount", _COUNT), ("referenceLabel", _LABEL),
                      ("documentationURL", _URL), ("samples", ("array", _INT, False)),
                      ("matrix", ("array", ("array", _INT, False), False)),
                      ("nested", ("array", _BOOL, True)), ("links", ("array", _URL, False))))
# Active-window reads have an operation-specific, deliberately tiny public
# value.  The historical finite-class matrix remains available through the
# common error.details schema (and other declared operations), but raw window
# references/markers must never cross this boundary.
_WINDOW_OBSERVATION = ("object", (("window_state", ("leaf", OperationFieldClass.LITERAL_TEXT,
                                                       ("observed", "missing", "ambiguous"))),
                                   ("marker_count", _COUNT),
                                   ("assertion_passed", _BOOL)))
_READ_SCHEMA = ("read_active_window", _WINDOW_OBSERVATION, _COMMON, True)
_WINDOW_SCHEMA = ("get_window_list", ("object", (("count", _COUNT),)), _COMMON, False)
_SCREENSHOT_SCHEMA = ("capture_screenshot", ("object", (("size_bytes", _COUNT),)), _COMMON, True)
_SOURCE_SCHEMAS = MappingProxyType({
    schema[0]: schema for schema in (_READ_SCHEMA, _WINDOW_SCHEMA, _SCREENSHOT_SCHEMA)
})
def _compose_operation_schemas() -> MappingProxyType:
    return MappingProxyType(dict(_SOURCE_SCHEMAS))
def _logical(value: Any, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None: raise OperationBoundaryError()
    return value
def admit_operation_provenance(*, operation: Any, target: Any, session: Any, binding: Any,
                               fingerprint: Any, generation: Any,
                               evidence_policy: Any) -> OperationProvenance:
    """Admit exact logical provenance without physical or dynamic values."""
    admitted_session = None if session is None else _logical(session, _LOGICAL)
    if type(generation) is not int or not 0 < generation < 2**63: raise OperationBoundaryError()
    if type(evidence_policy) is not str or evidence_policy not in {"sanitized", "full_local"}: raise OperationBoundaryError()
    return OperationProvenance(_logical(operation, _OPERATION), _logical(target, _LOGICAL), admitted_session,
                               _logical(binding, _LOGICAL), _logical(fingerprint, _FINGERPRINT),
                               generation, evidence_policy, _PROVENANCE_SEAL)
@dataclass(frozen=True)
class EvidenceReceipt:
    artifact_id: str; path: Path
    _ledger: object = field(repr=False, compare=False)
    _scope: object = field(repr=False, compare=False)
@dataclass(frozen=True)
class _EvidenceRecord:
    path: Path
    sha256: str
    identity: tuple[int, int, int, int]

class EvidenceScope:
    __slots__ = ("_ledger", "_token", "_operation", "_owned", "_retained")
    def __init__(self, ledger: "EvidenceLedger", token: object, operation: str | None = None) -> None:
        self._ledger, self._token, self._operation = ledger, token, operation
        self._owned: set[Path] = set()
        self._retained: set[Path] = set()

    def record(self, artifact_id: Any, path: Any) -> EvidenceReceipt:
        """Trusted low-level registration; captures current file identity and hash."""
        try: return self._ledger._record(self, artifact_id, path)
        except OperationBoundaryError: raise
        except Exception: raise OperationBoundaryError("invalid-evidence-receipt") from None

    def _allocate_screenshot(self) -> Path:
        self._ledger._check_scope(self)
        root = self._ledger.root
        if type(root) is not _PATH_TYPE or root.is_symlink() or root.resolve(strict=True) != root:
            raise OperationBoundaryError("invalid-evidence-receipt")
        fd, name = tempfile.mkstemp(prefix="capture_screenshot-", suffix=".png", dir=root)
        os.close(fd)
        path = Path(name)
        self._owned.add(path)
        return path

    def _retain(self) -> None:
        if self._ledger.policy == "full_local":
            self._retained.update(self._owned)

    def _cleanup(self) -> None:
        failed = False
        for path in self._owned - self._retained:
            try:
                # These names were exclusively allocated by this scope. Unlink
                # an own symlink entry too, never follow it to a borrowed file.
                if path.parent.is_symlink() or path.parent.resolve(strict=True) != self._ledger.root:
                    raise OSError("evidence root changed")
                path.unlink(missing_ok=True)
            except OSError:
                failed = True
        if failed:
            raise OperationBoundaryError("invalid-evidence-receipt")

class EvidenceLedger:
    """One application's frozen evidence authority and active receipt scopes."""
    __slots__ = ("_authority", "_guard", "_seal", "_active", "_records", "_lock")
    def __init__(self, root: Path | None = None, policy: str = "sanitized") -> None:
        if type(policy) is not str or policy not in {"sanitized", "full_local"} or (policy == "full_local" and root is None): raise OperationBoundaryError("invalid-evidence-policy")
        if root is not None and type(root) is not _PATH_TYPE: raise OperationBoundaryError("invalid-evidence-receipt")
        failed, resolved = False, None
        try:
            failed = root is not None and (root.is_symlink() or not root.is_dir())
            resolved = root.resolve(strict=True) if root is not None else None
        except Exception: failed = True
        if failed: raise OperationBoundaryError("invalid-evidence-receipt")
        seal = object(); self._authority, self._guard = (resolved, policy), (resolved, policy, seal)
        self._seal, self._active, self._records, self._lock = seal, {}, {}, threading.RLock()
    @property
    def root(self) -> Path | None: return self._authority[0]
    @property
    def policy(self) -> str: return self._authority[1]
    def _valid(self) -> bool: return self._guard == (*self._authority, self._seal)
    @contextmanager
    def operation(self, operation: str | None = None) -> Iterator[EvidenceScope]:
        if not self._valid(): raise OperationBoundaryError("invalid-evidence-receipt")
        if operation is not None: _logical(operation, _OPERATION)
        token = object(); scope = EvidenceScope(self, token, operation)
        with self._lock: self._active[token] = scope
        carrier = _CURRENT_EVIDENCE_SCOPE.set(scope)
        try:
            yield scope
        finally:
            try:
                scope._cleanup()
            finally:
                _CURRENT_EVIDENCE_SCOPE.reset(carrier)
                with self._lock:
                    self._active.pop(token, None)
                    self._records = {k: v for k, v in self._records.items() if k[0] is not token}

    def _check_scope(self, scope: EvidenceScope) -> None:
        if (not self._valid() or type(scope) is not EvidenceScope
                or getattr(scope, "_ledger", None) is not self
                or self._active.get(getattr(scope, "_token", None)) is not scope):
            raise OperationBoundaryError("invalid-evidence-receipt")

    def _contained(self, path: Any) -> Path:
        root = self.root
        if not self._valid() or type(path) is not _PATH_TYPE or type(root) is not _PATH_TYPE: raise OperationBoundaryError("invalid-evidence-receipt")
        failed, resolved = False, None
        try:
            resolved, cursor = path.resolve(strict=True), path.absolute()
            while cursor != root and cursor.parent != cursor:
                failed = failed or cursor.is_symlink(); cursor = cursor.parent
            failed = failed or cursor != root or resolved == root or not resolved.is_relative_to(root) or len(str(resolved)) > 2048
        except Exception: failed = True
        if failed: raise OperationBoundaryError("invalid-evidence-receipt")
        return resolved
    def _file_record(self, path: Path) -> _EvidenceRecord:
        resolved = self._contained(path)
        try:
            flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                     | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
            fd = os.open(resolved, flags)
            with os.fdopen(fd, "rb") as stream:
                before = os.fstat(stream.fileno())
                if not stat.S_ISREG(before.st_mode):
                    raise OperationBoundaryError("invalid-evidence-receipt")
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
                after = os.fstat(stream.fileno())
            identity = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
            current = resolved.stat(follow_symlinks=False)
            if identity(before) != identity(after) or identity(after) != identity(current):
                raise OperationBoundaryError("invalid-evidence-receipt")
            if self._contained(path) != resolved:
                raise OperationBoundaryError("invalid-evidence-receipt")
            return _EvidenceRecord(resolved, "sha256:" + digest, identity(after))
        except OperationBoundaryError: raise
        except Exception: raise OperationBoundaryError("invalid-evidence-receipt") from None

    def _record(self, scope: EvidenceScope, artifact_id: Any, path: Any) -> EvidenceReceipt:
        self._check_scope(scope)
        item = _logical(artifact_id, _ARTIFACT)
        record = self._file_record(path)
        key = (scope._token, item)
        with self._lock:
            self._check_scope(scope)
            if key in self._records: raise OperationBoundaryError("invalid-evidence-receipt")
            self._records[key] = record
        return EvidenceReceipt(item, record.path, self._seal, scope._token)

    def _scope_receipts(self, scope: EvidenceScope) -> tuple[EvidenceReceipt, ...]:
        with self._lock:
            self._check_scope(scope)
            return tuple(EvidenceReceipt(item, record.path, self._seal, scope._token)
                         for (token, item), record in self._records.items() if token is scope._token)

    def _path(self, receipt: Any, artifact_id: str, scope: Any, sha256: str = "") -> str:
        try:
            self._check_scope(scope)
            if (type(receipt) is not EvidenceReceipt
                    or type(getattr(receipt, "path", None)) is not _PATH_TYPE
                    or type(getattr(receipt, "artifact_id", None)) is not str):
                raise OperationBoundaryError("invalid-evidence-receipt")
            with self._lock:
                expected = self._records.get((scope._token, artifact_id))
                valid = (getattr(receipt, "_ledger", None) is self._seal
                         and getattr(receipt, "_scope", None) is scope._token
                         and getattr(receipt, "artifact_id", None) == artifact_id
                         and type(expected) is _EvidenceRecord
                         and expected.path == getattr(receipt, "path", None))
            if not valid or self._file_record(expected.path) != expected:
                raise OperationBoundaryError("invalid-evidence-receipt")
            # Legacy low-level callers can omit optional metadata; shared
            # operation results must state the exact registered content hash.
            if (scope._operation is not None or sha256) and sha256 != expected.sha256:
                raise OperationBoundaryError("invalid-evidence-receipt")
            return str(expected.path)
        except OperationBoundaryError: raise
        except Exception: raise OperationBoundaryError("invalid-evidence-receipt") from None
def _decode(value: str) -> str | None:
    if _BAD_PERCENT.search(value): return None
    try: return unquote_to_bytes(value).decode("utf-8", "strict")
    except Exception: return None
def _documentation_url(value: Any) -> str | None:
    if type(value) is not str or not 0 < len(value) <= 2048 or any(ord(c) < 32 or ord(c) == 127 for c in value): return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment: return None
        authority, path, fixed = parsed.netloc, parsed.path, False
        for _ in range(4):
            if "@" in authority or _CREDENTIAL.search(path) or "?" in path or "#" in path or any(ord(c) < 32 or ord(c) == 127 for c in authority + path): return None
            next_authority, next_path = _decode(authority), _decode(path)
            if next_authority is None or next_path is None: return None
            if (next_authority, next_path) == (authority, path): fixed = True; break
            authority, path = next_authority, next_path
        if not fixed: fixed = (_decode(authority), _decode(path)) == (authority, path)
        if not fixed or "@" in authority or _CREDENTIAL.search(path) or "?" in path or "#" in path or any(ord(c) < 32 or ord(c) == 127 for c in authority + path): return None
        final = urlsplit(f"{parsed.scheme.lower()}://{authority}{path}")
        if final.netloc != authority or final.path != path or final.query or final.fragment: return None
        if final.username is not None or final.password is not None or final.hostname is None: return None
        host = final.hostname.encode("idna").decode("ascii").lower()
        try:
            address = ipaddress.ip_address(host); public = (address.is_global and not (address.is_multicast or address.is_unspecified or address.is_reserved or address.is_loopback or address.is_link_local or address.is_private)) or any(address in n for n in _DOC_NETWORKS); host = address.compressed
            if address.version == 6 and (address.ipv4_mapped or address.sixtofour or address.teredo or address in ipaddress.ip_network("64:ff9b::/96") or address in ipaddress.ip_network("64:ff9b:1::/48")): return None
        except ValueError:
            labels, numeric = host.split("."), re.fullmatch(r"[0-9a-fx.]+", host, re.I) is not None
            public = not numeric and len(labels) > 1 and not host.endswith((".local", ".internal", ".localhost")) and all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in labels)
        if not public: return None
        port = final.port; default = (final.scheme == "http" and port == 80) or (final.scheme == "https" and port == 443)
        authority = f"[{host}]" if ":" in host else host
        if port is not None and not default: authority += f":{port}"
        return urlunsplit((final.scheme, authority, quote(path, safe="/!$&'()*+,-.:;=@~"), "", ""))
    except Exception: return None
def _charge(state: list[int], depth: int, amount: int = 1) -> None:
    state[0] += amount
    if depth > 8 or state[0] > 512: raise _TooLarge()
def _rebuild(rule: Any, value: Any, depth: int, state: list[int]) -> Any:
    if type(rule) is not tuple: raise OperationBoundaryError("invalid-executor-result")
    _charge(state, depth)
    if rule[0] == "object":
        if type(value) is not dict or any(type(k) is not str for k in value): raise OperationBoundaryError("invalid-executor-result")
        if len(value) > 64: raise _TooLarge()
        return {name: _rebuild(child, value[name], depth + 1, state) for name, child in rule[1] if name in value}
    if rule[0] == "array":
        if type(value) is not list: raise OperationBoundaryError("invalid-executor-result")
        if len(value) > 64: raise _TooLarge()
        return [_rebuild(rule if rule[2] and type(item) is list else rule[1], item, depth + 1, state) for item in value]
    if rule[0] != "leaf": raise OperationBoundaryError("invalid-executor-result")
    kind = rule[1]
    if kind is OperationFieldClass.BOOLEAN and type(value) is bool: return value
    if kind is OperationFieldClass.INT64 and type(value) is int and -(2**63) <= value < 2**63: return value
    if kind is OperationFieldClass.FINITE_NUMBER and ((type(value) is int and -(2**63) <= value < 2**63) or (type(value) is float and math.isfinite(value))): return value
    if kind is OperationFieldClass.REFERENCE_COUNT and type(value) is int and 0 <= value <= 2_147_483_647: return value
    if kind is OperationFieldClass.LITERAL_TEXT and type(value) is str and value in rule[2]: return value
    if kind is OperationFieldClass.DOCUMENTATION_URL:
        admitted = _documentation_url(value)
        if admitted is not None: return admitted
    raise OperationBoundaryError("invalid-executor-result")
_ERRORS = {OperationVerdict.BLOCKED: ("executor-blocked", "executor reported a blocked operation"), OperationVerdict.AMBIGUOUS: ("executor-ambiguous", "executor reported an ambiguous operation"), OperationVerdict.FAILURE: ("executor-failure", "executor reported an operation failure")}
def _failure(kind: OperationKind, provenance: OperationProvenance | None, code: str) -> OperationResult:
    message = "operation result exceeded public limits" if code == "result-too-large" else "operation result was not admitted"
    return OperationResult(OperationRequest(kind, provenance.operation if provenance else "invalid_operation"), OperationVerdict.FAILURE, error=OperationError(code, message), provenance=provenance)
def normalize_operation_result(context: Any, request: Any, raw: Any, provenance: Any, *,
                               scope: EvidenceScope | None = None,
                               receipts: Sequence[EvidenceReceipt] = ()) -> OperationResult:
    """Rebuild one executor DTO through the application's exact positive schema."""
    kind, admitted = OperationKind.READ, None
    try:
        from .application import ApplicationContext
        if type(context) is not ApplicationContext: raise OperationBoundaryError("invalid-executor-result")
        if type(request) is not OperationRequest or type(request.kind) is not OperationKind: raise OperationBoundaryError("invalid-executor-result")
        kind = request.kind
        if type(provenance) is not OperationProvenance or provenance._seal is not _PROVENANCE_SEAL: raise OperationBoundaryError("invalid-executor-result")
        admitted = admit_operation_provenance(operation=provenance.operation, target=provenance.target, session=provenance.session, binding=provenance.binding, fingerprint=provenance.fingerprint, generation=provenance.generation, evidence_policy=provenance.evidence_policy)
        if admitted != provenance or request.name != admitted.operation: raise OperationBoundaryError("invalid-executor-result")
        catalog, ledger = context.operation_schemas, context.evidence_ledger
        guard = context._operation_boundary_guard
        if (type(guard) is not tuple or len(guard) != 2 or guard[0] is not catalog
                or guard[1] is not ledger or type(catalog) is not _PROXY_TYPE
                or set(catalog) != set(_SOURCE_SCHEMAS)
                or any(catalog.get(name) is not schema for name, schema in _SOURCE_SCHEMAS.items())):
            raise OperationBoundaryError("invalid-executor-result")
        binding = context.runtime_target.binding if context.runtime_target is not None else None
        if type(ledger) is not EvidenceLedger or not ledger._valid() or (ledger.root, ledger.policy) != ((binding.evidence_root, binding.evidence_policy.value) if binding else (None, "sanitized")) or ledger.policy != admitted.evidence_policy: raise OperationBoundaryError("invalid-executor-result")
        if type(raw) is not OperationResult or type(raw.verdict) is not OperationVerdict or type(raw.artifacts) is not tuple: raise OperationBoundaryError("invalid-executor-result")
        schema, state = catalog[admitted.operation], [0]
        value = None if raw.value is None else _rebuild(schema[1], raw.value, 1, state)
        if raw.verdict is OperationVerdict.SUCCESS:
            if raw.error is not None: raise OperationBoundaryError("invalid-executor-result")
            error = None
        else:
            if type(raw.error) is not OperationError or type(raw.error.retryable) is not bool: raise OperationBoundaryError("invalid-executor-result")
            details = _rebuild(schema[2], raw.error.details, 1, state)
            code, message = _ERRORS[raw.verdict]; error = OperationError(code, message, raw.error.retryable, details)
        if len(raw.artifacts) > 64: raise _TooLarge()
        artifacts, artifact_ids = [], set()
        for artifact in raw.artifacts:
            if not schema[3] or type(artifact) is not ArtifactReference: raise OperationBoundaryError("invalid-executor-result")
            artifact_id, media_type, sha256, sensitivity = artifact.artifact_id, artifact.media_type, artifact.sha256, artifact.sensitivity
            if type(artifact_id) is not str or _ARTIFACT.fullmatch(artifact_id) is None or type(media_type) is not str or _MEDIA.fullmatch(media_type) is None or type(sha256) is not str or (sha256 and _SHA.fullmatch(sha256) is None) or type(sensitivity) is not str or sensitivity not in {"public", "internal"} or artifact_id in artifact_ids: raise OperationBoundaryError("invalid-executor-result")
            artifact_ids.add(artifact_id)
            _charge(state, 1, 5); artifacts.append((artifact_id, media_type, sha256, sensitivity))
        if type(receipts) is not tuple or len(receipts) > 64: raise OperationBoundaryError("invalid-evidence-receipt")
        full_local = admitted.evidence_policy == "full_local"
        scoped = type(scope) is EvidenceScope and getattr(scope, "_ledger", None) is ledger
        if (full_local and not scoped) or (scope is not None and not scoped):
            raise OperationBoundaryError("invalid-evidence-receipt")
        if scoped and scope._operation not in (None, admitted.operation):
            raise OperationBoundaryError("invalid-evidence-receipt")
        if any(type(item) is not EvidenceReceipt or type(getattr(item, "artifact_id", None)) is not str for item in receipts): raise OperationBoundaryError("invalid-evidence-receipt")
        receipt_map = {item.artifact_id: item for item in receipts}
        if len(receipt_map) != len(receipts) or (not scoped and receipts): raise OperationBoundaryError("invalid-evidence-receipt")
        if scoped:
            if (scope._operation == "capture_screenshot" and raw.verdict is OperationVerdict.SUCCESS
                    and len(artifacts) != 1):
                raise OperationBoundaryError("invalid-evidence-receipt")
            if (raw.verdict is OperationVerdict.SUCCESS and set(receipt_map) != artifact_ids
                    or not artifact_ids.issubset(receipt_map)):
                raise OperationBoundaryError("invalid-evidence-receipt")
            paths = {a: ledger._path(receipt_map.get(a), a, scope, h) for a, m, h, s in artifacts}
            if scope._operation == "capture_screenshot" and any(
                    m != "image/png" or s != "internal" for a, m, h, s in artifacts):
                raise OperationBoundaryError("invalid-evidence-receipt")
            if scope._operation == "capture_screenshot" and len(artifacts) == 1:
                record = ledger._records[(scope._token, artifacts[0][0])]
                if type(value) is dict and "size_bytes" in value and value["size_bytes"] != record.identity[2]:
                    raise OperationBoundaryError("invalid-evidence-receipt")
        else:
            paths = {}
        artifacts = [ArtifactReference(a, m, h, paths[a] if full_local else "", s) for a, m, h, s in artifacts]
        result = OperationResult(OperationRequest(kind, admitted.operation), raw.verdict, value, error, tuple(artifacts), admitted)
        encoded = json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
        return _failure(kind, admitted, "result-too-large") if len(encoded) > 65_536 else result
    except _TooLarge: return _failure(kind, admitted, "result-too-large")
    except OperationBoundaryError as error: code = "invalid-evidence-receipt" if error.code == "invalid-evidence-receipt" else "invalid-executor-result"
    except Exception: code = "invalid-executor-result"
    return _failure(kind, admitted, code)
