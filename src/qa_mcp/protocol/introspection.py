"""Protocol-owned foreground-neutral introspection helpers.

The MCP server keeps tool argument plumbing and result shaping; this module owns
the TestClient wire sweeps used by descriptor, value, table-cell and window-list
reads.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import Settings
from . import CaptureBootstrap, ProtocolTemplates, TestClientSession, resolve_capture_dir
from .bootstrap_synth import synthesize_bootstrap
from .session import timestamp_name

_VALUE_READ_OPEN_FRAMES = list(range(11, 18))
_VALUE_READ_FRAMES = [218, 219, 220, 221]
_VALUE_READ_CAPTURED_FIELD = "PF_EDIT_STRING"
_SPLICE_PLACEHOLDER_GUID = "00000000-0000-0000-0000-000000000000"
_FIELD_QUERY_PATH_RE = re.compile(rb"((?:Group\[[A-Za-z0-9_]+\]\.)+)EditField\[([A-Za-z0-9_]+)\]")
_DESCRIPTOR_FORM_PATH_RE = re.compile(r"SecondaryFrame\[([0-9a-f-]{36})\]\.ManagedForm\[([0-9a-f-]{36})\]")
_WINDOW_COMMAND_HEADER_MARKER = b"\xcb\x23\x95"
_WINDOW_COMMAND_NONCE = bytes.fromhex("754ee15d6fb6f64f9a9c819ed06cd42bd50625da112c78cb47a6971efaef2b6913")
_WINDOW_COMMAND_TAIL = b"\x88\x82\x81   fS\xb2\xa6"
_NAVIGATION_BOOTSTRAP_CAPTURE = "tm-v1-ro-batchQ3"
_NAVIGATION_BOOTSTRAP_TEMPLATE_FRAMES = (8, 9, 10)


class NavigationAssetError(RuntimeError):
    """Sanitized preflight failure for template-backed live navigation."""

    def __init__(self, asset_class: str, reason_code: str) -> None:
        super().__init__(f"{asset_class}: {reason_code}")
        self.asset_class = asset_class
        self.reason_code = reason_code


@dataclass(frozen=True)
class NavigationAssets:
    bootstrap: CaptureBootstrap
    templates: ProtocolTemplates
    synthesized: Any


def _repo_root() -> Path:
    home = Settings.from_env().home
    if home:
        return Path(home)
    return Path(__file__).resolve().parents[3]


def _load_templates(repo_root: Path, manager_templates: str) -> ProtocolTemplates:
    path = Path(manager_templates)
    return ProtocolTemplates.load(path if path.is_absolute() else (repo_root / path).resolve())


def prepare_open_list_navigation_assets(
    *,
    manager_templates: str,
    repo_root: Path | None = None,
) -> NavigationAssets:
    """Load and structurally validate every asset before a live navigation connection opens."""
    root = repo_root or _repo_root()
    try:
        bootstrap_dir = resolve_capture_dir(_NAVIGATION_BOOTSTRAP_CAPTURE, root)
        bootstrap = CaptureBootstrap.load(bootstrap_dir)
    except Exception as exc:  # noqa: BLE001 - collapse asset details into a public-safe capability reason
        reason = "asset-missing" if isinstance(exc, FileNotFoundError) else "asset-invalid"
        raise NavigationAssetError("bootstrap-capture", reason) from exc

    try:
        templates = _load_templates(root, manager_templates)
    except Exception as exc:  # noqa: BLE001 - do not expose machine-local template paths
        reason = "asset-missing" if isinstance(exc, FileNotFoundError) else "asset-invalid"
        raise NavigationAssetError("navigation-templates", reason) from exc

    placeholder = _SPLICE_PLACEHOLDER_GUID
    try:
        for frame_index in _NAVIGATION_BOOTSTRAP_TEMPLATE_FRAMES:
            templates.render(
                frame_index,
                placeholder,
                0,
                managed_form_guid=placeholder,
                secondary_frame_guid=placeholder,
            )
    except Exception as exc:  # noqa: BLE001 - every bootstrap template must be valid before protocol I/O
        raise NavigationAssetError("navigation-templates", "required-bootstrap-frame-unavailable") from exc

    try:
        rendered = templates.render(
            _VALUE_READ_FRAMES[0],
            placeholder,
            0,
            managed_form_guid=placeholder,
            secondary_frame_guid=placeholder,
        ).payload
        if _WINDOW_COMMAND_HEADER_MARKER not in rendered:
            raise RuntimeError("required splice marker is absent")
    except Exception as exc:  # noqa: BLE001 - structural template preflight is fail-closed
        raise NavigationAssetError("navigation-templates", "required-splice-frame-unavailable") from exc

    try:
        synthesized = synthesize_bootstrap()
    except Exception as exc:  # noqa: BLE001 - synthesized bootstrap assets are also preflighted
        reason = "asset-missing" if isinstance(exc, FileNotFoundError) else "asset-invalid"
        raise NavigationAssetError("synthesized-bootstrap", reason) from exc
    return NavigationAssets(bootstrap=bootstrap, templates=templates, synthesized=synthesized)


def open_list_from_navigation_assets(
    assets: NavigationAssets,
    nav_link: str,
    *,
    host: str,
    port: int,
    repo_root: Path | None = None,
) -> tuple[str, str, str] | None:
    """Open and resolve one list through already-preflighted bundled navigation assets."""
    root = repo_root or _repo_root()
    output_dir = root / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
    with TestClientSession(host=host, port=port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=assets.bootstrap,
            templates=assets.templates,
            output_dir=output_dir,
            synthesized=assets.synthesized,
        )
        return _open_form_by_link(handle, nav_link, splice_templates=assets.templates)


def _splice_header_no_form(handle: Any, templates: Any = None) -> bytes:
    """Build a value-read splice header without depending on an already-open form."""
    from .native_write import WINDOW_LIST_HEADER_MARKER

    rendered = (templates or handle.templates).render(
        _VALUE_READ_FRAMES[0],
        handle.state.ack_guid,
        handle.state.frame4_sequence,
        managed_form_guid=_SPLICE_PLACEHOLDER_GUID,
        secondary_frame_guid=_SPLICE_PLACEHOLDER_GUID,
    ).payload
    j = rendered.rfind(WINDOW_LIST_HEADER_MARKER)
    if j < 0:
        raise ValueError("no cb-23-95 marker in the rendered value-read frame")
    return rendered[: j + len(WINDOW_LIST_HEADER_MARKER)]


def _retarget_read_to_groups(
    payload: bytes,
    captured_leaf: str,
    field: str,
    groups: list[str],
    form_ref: tuple[str, str] | None = None,
) -> bytes:
    """Retarget a captured value-read query to a field's full group path."""
    from .element_ref import (
        ElementRef,
        extract_element_paths,
        parse_element_path,
        path_is_latin1,
        retarget_element_path,
        retarget_element_path_reencode,
    )

    out = payload
    for path in extract_element_paths(payload):
        try:
            ref = parse_element_path(path)
        except ValueError:
            continue
        if ref.kind == "EditField" and ref.name == captured_leaf:
            sframe, mform = form_ref if form_ref is not None else (ref.secondary_frame, ref.managed_form)
            new_path = ElementRef(sframe, mform, list(groups), "EditField", field).path()
            try:
                if path_is_latin1(new_path):
                    out, _ = retarget_element_path(out, path, new_path)
                else:
                    out, _ = retarget_element_path_reencode(out, path, new_path)
            except ValueError:
                pass
    return out


def _read_field_value(
    field: str,
    *,
    host: str,
    port: int,
    capture_dir: str,
    manager_templates: str,
    groups: list[str] | None = None,
) -> str | None:
    """Read a single live form field through the value-read protocol frames."""
    from .element_ref import retarget_element_leaf
    from .responses import extract_edit_field_value

    repo_root = _repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(capture_dir, repo_root))
    templates = _load_templates(repo_root, manager_templates)
    synthesized = synthesize_bootstrap()
    output_dir = repo_root / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()

    rewriter = None
    if groups is not None:

        def rewriter(_idx: int, payload: bytes, _field: str = field, _groups: tuple = tuple(groups)) -> bytes:
            return _retarget_read_to_groups(payload, _VALUE_READ_CAPTURED_FIELD, _field, list(_groups))

    elif field != _VALUE_READ_CAPTURED_FIELD:

        def rewriter(_idx: int, payload: bytes, _field: str = field) -> bytes:
            try:
                out, _ = retarget_element_leaf(payload, _VALUE_READ_CAPTURED_FIELD, _field)
                return out
            except ValueError:
                return payload

    with TestClientSession(host=host, port=port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            synthesized=synthesized,
        )
        handle.run_segment(_VALUE_READ_OPEN_FRAMES, query_id="form-element-details")
        before = len(handle.state.received_stream)
        handle.run_segment(_VALUE_READ_FRAMES, query_id="form-value-read", frame_rewriter=rewriter)
        blob = bytes(handle.state.received_stream[before:])
    return extract_edit_field_value(blob, field)


def _enumerate_capture_fields(bootstrap: CaptureBootstrap) -> list[tuple[str, list[str]]]:
    """Enumerate captured value-read field paths, including UTF-16 element paths."""
    from .element_ref import extract_element_paths_utf16, parse_element_path

    specs: dict[str, list[str]] = {}
    for frame in bootstrap.manager_frames:
        for m in _FIELD_QUERY_PATH_RE.finditer(frame):
            name = m.group(2).decode("latin1")
            if name not in specs:
                specs[name] = [g.decode("latin1") for g in re.findall(rb"Group\[([A-Za-z0-9_]+)\]", m.group(1))]
        for path in extract_element_paths_utf16(frame):
            try:
                ref = parse_element_path(path)
            except ValueError:
                continue
            if ref.kind == "EditField" and ref.name not in specs:
                specs[ref.name] = list(ref.groups)
    return list(specs.items())


def _live_descriptor_blob(handle: Any, form_ref: tuple[str, str] | None = None) -> bytes:
    """Fetch the live get_form_analysis descriptor response for the current or supplied form."""
    from .native_write import splice_descriptor_query

    if form_ref is not None:
        s, f = form_ref
        header = _splice_header_no_form(handle)
    else:
        sent0 = len(handle.state.sent_stream)
        handle.run_segment(_VALUE_READ_FRAMES[:1], query_id="form-value-read")
        header = bytes(handle.state.sent_stream[sent0:])
        m = _DESCRIPTOR_FORM_PATH_RE.search(header.decode("latin1", "replace"))
        if m is None:
            return b""
        s, f = m.group(1), m.group(2)
    before = len(handle.state.received_stream)
    handle.run_action(splice_descriptor_query(header, s, f), query_id="form-descriptor")
    return bytes(handle.state.received_stream[before:])


def _enumerate_live_fields(handle: Any, form_ref: tuple[str, str] | None = None) -> list[tuple[str, list[str]]]:
    from .responses import extract_descriptor_fields

    return extract_descriptor_fields(_live_descriptor_blob(handle, form_ref))


def _normalize_data_ref_link(nav_link: str) -> str:
    """Normalize dashed e1cib data references to the hex token expected by 1C."""
    from .navigation import e1cib_ref_hex

    m = re.match(r"^(e1cib/data/[^?]+\?ref=)(.+)$", nav_link)
    if not m:
        return nav_link
    try:
        return m.group(1) + e1cib_ref_hex(m.group(2))
    except ValueError:
        return nav_link


def _is_bare_create_data_link(nav_link: str) -> bool:
    return bool(re.match(r"^e1cib/data/[^?]+$", nav_link.strip()))


def _splice_window_activate_command(rendered_value_read_frame: bytes, secondary_frame: str) -> bytes:
    """Build a same-session window activate command for a resolved managed form."""
    marker = rendered_value_read_frame.rfind(_WINDOW_COMMAND_HEADER_MARKER)
    if marker < 0:
        raise ValueError("no cb-23-95 header marker in the rendered value-read frame")
    header = rendered_value_read_frame[: marker + len(_WINDOW_COMMAND_HEADER_MARKER)]
    path = f"SecondaryFrame[{secondary_frame}]".encode("latin1")
    if len(path) > 255:
        raise ValueError("window command path is too long")
    return header + _WINDOW_COMMAND_NONCE + b"\x9a" + bytes([len(path)]) + path + _WINDOW_COMMAND_TAIL


def _open_form_by_link(handle: Any, nav_link: str, splice_templates: Any = None) -> tuple[str, str, str] | None:
    """Navigate to a form and resolve its SecondaryFrame/ManagedForm pair."""
    from .native_write import splice_navigate, splice_resolve_form_query, splice_window_list_queries
    from .responses import extract_testclient_windows

    nav_link = _normalize_data_ref_link(nav_link)

    def _windows() -> list[dict[str, str]]:
        before = len(handle.state.received_stream)
        for q in splice_window_list_queries(_splice_header_no_form(handle, splice_templates)):
            handle.run_action(q, query_id="window-list")
        return extract_testclient_windows(bytes(handle.state.received_stream[before:]))

    desktop = _windows()
    main = next((w for w in desktop if w["kind"] == "MainFrame"), None)
    main_frame = main["guid"] if main else None
    before_sfs = {w["guid"] for w in desktop if w["kind"] == "SecondaryFrame"}

    for nav_frame in splice_navigate(_splice_header_no_form(handle, splice_templates), nav_link, main_frame=main_frame):
        handle.run_action(nav_frame, query_id="navigate")
    form_name = nav_link.rsplit(".", 1)[-1] if "." in nav_link else nav_link
    settings = Settings.from_env()
    attempts = max(1, settings.descriptor_warmup_attempts)
    delay = max(0.0, settings.descriptor_warmup_delay_sec)
    for attempt in range(attempts):
        windows = _windows()
        sfs = [w for w in windows if w["kind"] == "SecondaryFrame"]
        target = next((w for w in sfs if form_name in w["caption"]), None)
        if target is None:
            new_sfs = [w for w in sfs if w["guid"] not in before_sfs]
            target = new_sfs[-1] if new_sfs else None
        if target is not None:
            before = len(handle.state.received_stream)
            handle.run_action(
                splice_resolve_form_query(_splice_header_no_form(handle, splice_templates), target["guid"]),
                query_id="resolve-form",
            )
            resp = bytes(handle.state.received_stream[before:])
            match = re.search(
                target["guid"].encode("latin1") + rb"\]\.ManagedForm\[([0-9a-f-]{36})\]",
                resp,
            )
            if match is not None:
                return target["caption"], target["guid"], match.group(1).decode()
        if attempt + 1 < attempts and delay > 0:
            time.sleep(delay)
    return None


def _sweep_form_field_values(
    handle: Any,
    specs: list[tuple[str, list[str]]],
    form_ref: tuple[str, str] | None,
) -> dict[str, str]:
    """Read a value for every supplied field/group path spec on the same session."""
    from .responses import extract_form_field_values

    fields: dict[str, str] = {}
    for name, groups in specs:

        def rewriter(_idx: int, payload: bytes, _f: str = name, _g: tuple = tuple(groups), _r=form_ref) -> bytes:
            return _retarget_read_to_groups(payload, _VALUE_READ_CAPTURED_FIELD, _f, list(_g), form_ref=_r)

        before = len(handle.state.received_stream)
        try:
            handle.run_segment(_VALUE_READ_FRAMES, query_id="form-value-read", frame_rewriter=rewriter)
        except Exception:  # noqa: BLE001 - per-field read failure is skipped
            continue
        vblob = bytes(handle.state.received_stream[before:])
        for found_name, value in extract_form_field_values(vblob).items():
            fields[found_name] = value
    return fields


def _resolve_open_form_by_caption(
    handle: Any,
    caption_match: str,
    *,
    splice_templates: Any = None,
) -> tuple[str, str, str] | None:
    """Resolve an already-open form by caption or newest SecondaryFrame."""
    from .native_write import splice_resolve_form_query, splice_window_list_queries
    from .responses import extract_testclient_windows

    before = len(handle.state.received_stream)
    for q in splice_window_list_queries(_splice_header_no_form(handle, splice_templates)):
        handle.run_action(q, query_id="window-list")
    windows = extract_testclient_windows(bytes(handle.state.received_stream[before:]))
    sfs = [w for w in windows if w["kind"] == "SecondaryFrame"]
    if caption_match:
        needle = caption_match.casefold()
        sfs = [w for w in sfs if needle in (w.get("caption") or "").casefold()]
    target = sfs[-1] if sfs else None
    if target is None:
        return None
    before = len(handle.state.received_stream)
    handle.run_action(
        splice_resolve_form_query(_splice_header_no_form(handle, splice_templates), target["guid"]),
        query_id="resolve-form",
    )
    resp = bytes(handle.state.received_stream[before:])
    m = re.search(target["guid"].encode("latin1") + rb"\]\.ManagedForm\[([0-9a-f-]{36})\]", resp)
    if m is None:
        return None
    return target["caption"], target["guid"], m.group(1).decode()


def _read_open_form_once(
    *,
    host: str,
    port: int,
    caption_match: str,
    capture_dir: str,
    manager_templates: str,
) -> dict[str, Any]:
    """Read values from an already-open form on a fresh manager connection."""
    from .responses import extract_descriptor_elements, extract_descriptor_fields

    repo_root = _repo_root()
    try:
        bootstrap = CaptureBootstrap.load(resolve_capture_dir(capture_dir, repo_root))
        templates = _load_templates(repo_root, manager_templates)
        synthesized = synthesize_bootstrap()
        output_dir = repo_root / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
        with TestClientSession(host=host, port=port) as session:
            handle = session.open_and_bootstrap(
                bootstrap=bootstrap,
                templates=templates,
                output_dir=output_dir,
                synthesized=synthesized,
            )
            resolved = _resolve_open_form_by_caption(handle, caption_match)
            if resolved is None:
                return {"opened": None, "fields": {}, "field_count": 0, "element_count": 0}
            opened, sf, mf = resolved
            handle.state.secondary_frame_guid = sf
            handle.state.managed_form_guid = mf
            form_ref = (sf, mf)
            blob = _live_descriptor_blob(handle, form_ref)
            element_count = len(extract_descriptor_elements(blob))
            specs = extract_descriptor_fields(blob)
            fields = _sweep_form_field_values(handle, specs, form_ref)
    except Exception as exc:  # noqa: BLE001 - read-back is best-effort verification
        return {
            "opened": None,
            "fields": {},
            "field_count": 0,
            "element_count": 0,
            "error": f"{type(exc).__name__}: {exc}",
        }
    return {"opened": opened, "fields": fields, "field_count": len(fields), "element_count": element_count}


def _read_open_form_field_values(
    *,
    host: str,
    port: int,
    caption_match: str = "",
    capture_dir: str,
    manager_templates: str,
    retries: int = 4,
    retry_delay: float = 3.0,
) -> dict[str, Any]:
    """Retry value-reading an already-open form across fresh manager connections."""
    attempts = max(1, retries)
    last: dict[str, Any] = {"opened": None, "fields": {}, "field_count": 0, "element_count": 0}
    for attempt in range(attempts):
        last = _read_open_form_once(
            host=host,
            port=port,
            caption_match=caption_match,
            capture_dir=capture_dir,
            manager_templates=manager_templates,
        )
        if last.get("field_count", 0) > 0:
            last["read_attempts"] = attempt + 1
            return last
        if attempt + 1 < attempts:
            time.sleep(retry_delay)
    last["read_attempts"] = attempts
    return last


def _read_form_descriptor(
    *,
    host: str,
    port: int,
    capture_dir: str,
    manager_templates: str,
    enumerate_live: bool = False,
    open_link: str | None = None,
) -> dict[str, Any]:
    """Read a form descriptor and its value-bearing fields through protocol sweeps."""
    from .responses import extract_descriptor_elements, extract_descriptor_fields

    repo_root = _repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(capture_dir, repo_root))
    templates = _load_templates(repo_root, manager_templates)
    synthesized = synthesize_bootstrap()
    output_dir = repo_root / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
    fields: dict[str, str] = {}
    opened: str | None = None
    form_ref: tuple[str, str] | None = None
    with TestClientSession(host=host, port=port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            synthesized=synthesized,
        )
        elements: list[Any] = []
        if open_link:
            resolved = _open_form_by_link(handle, open_link)
            if resolved is None:
                return {"opened": None, "elements": [], "element_count": 0, "fields": {}}
            opened, sf, mf = resolved
            form_ref = (sf, mf)
            handle.state.secondary_frame_guid = sf
            handle.state.managed_form_guid = mf
            blob = _live_descriptor_blob(handle, form_ref)
            elements = extract_descriptor_elements(blob)
            specs = extract_descriptor_fields(blob)
        else:
            handle.run_segment(_VALUE_READ_OPEN_FRAMES, query_id="form-element-details")
            specs = _enumerate_live_fields(handle, form_ref) if enumerate_live else _enumerate_capture_fields(bootstrap)
        fields.update(_sweep_form_field_values(handle, specs, form_ref))
    if open_link:
        return {
            "opened": opened,
            "elements": elements,
            "element_count": len(elements),
            "fields": fields,
            "field_count": len(fields),
        }
    return {"fields": fields, "field_count": len(fields), "queried": len(specs)}


def _table_groups(blob: bytes, table: str) -> list[str]:
    """Discover the group chain enclosing a table in a form descriptor."""
    try:
        at = table.encode("latin1")
    except UnicodeEncodeError:
        at = None
    if at is not None:
        m = re.search(rb"((?:Group\[[^\]]+\]\.)*)Table\[" + re.escape(at) + rb"\]", blob)
        if m:
            return [g.decode("latin1") for g in re.findall(rb"Group\[([^\]]+)\]", m.group(1))]
    tu = ("Table[" + table + "]").encode("utf-16-le")
    grp = rb"G\x00r\x00o\x00u\x00p\x00\[\x00(?:(?!\]\x00)..)+?\]\x00\.\x00"
    m = re.search(rb"((?:" + grp + rb")*)" + re.escape(tu), blob)
    if m:
        return [
            g.decode("utf-16-le", "replace")
            for g in re.findall(
                rb"G\x00r\x00o\x00u\x00p\x00\[\x00((?:(?!\]\x00)..)+?)\]\x00",
                m.group(1),
            )
        ]
    return []


def _read_table_cell(
    *,
    host: str,
    port: int,
    capture_dir: str,
    manager_templates: str,
    table: str,
    column: str,
    open_link: str | None = None,
) -> dict[str, Any]:
    """Read the current row's table/dynamic-list column value."""
    from .native_write import splice_table_cell_read
    from .responses import extract_table_cell_value

    repo_root = _repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(capture_dir, repo_root))
    templates = _load_templates(repo_root, manager_templates)
    synthesized = synthesize_bootstrap()
    output_dir = repo_root / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
    opened: str | None = None
    with TestClientSession(host=host, port=port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            synthesized=synthesized,
        )
        if open_link:
            resolved = _open_form_by_link(handle, open_link)
            if resolved is None:
                return {"table": table, "column": column, "value": None, "groups": [], "opened": None}
            opened, sf, mf = resolved
            handle.state.secondary_frame_guid, handle.state.managed_form_guid = sf, mf
        else:
            handle.run_segment(_VALUE_READ_OPEN_FRAMES, query_id="form-element-details")
            sf, mf = handle.state.secondary_frame_guid, handle.state.managed_form_guid
        blob = _live_descriptor_blob(handle, (sf, mf))
        groups = _table_groups(blob, table)
        before = len(handle.state.received_stream)
        handle.run_action(
            splice_table_cell_read(_splice_header_no_form(handle), sf, mf, groups, table, column),
            query_id="table-read",
        )
        resp = bytes(handle.state.received_stream[before:])
    return {
        "table": table,
        "column": column,
        "value": extract_table_cell_value(resp),
        "groups": groups,
        "opened": opened,
    }


def _read_testclient_windows(*, host: str, port: int, capture_dir: str, manager_templates: str) -> dict[str, Any]:
    """Replay the TestClient internal window-list query and decode its response."""
    from .native_write import splice_window_list_queries
    from .responses import extract_testclient_windows

    repo_root = _repo_root()
    bootstrap = CaptureBootstrap.load(resolve_capture_dir(capture_dir, repo_root))
    templates = _load_templates(repo_root, manager_templates)
    synthesized = synthesize_bootstrap()
    output_dir = repo_root / "runtime" / "protocol-research" / "native-mcp" / timestamp_name()
    with TestClientSession(host=host, port=port) as session:
        handle = session.open_and_bootstrap(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            synthesized=synthesized,
        )
        handle.run_segment(_VALUE_READ_OPEN_FRAMES, query_id="form-element-details")
        sent0 = len(handle.state.sent_stream)
        handle.run_segment(_VALUE_READ_FRAMES[:1], query_id="form-value-read")
        rendered = bytes(handle.state.sent_stream[sent0:])
        before = len(handle.state.received_stream)
        for query in splice_window_list_queries(rendered):
            handle.run_action(query, query_id="window-list")
        blob = bytes(handle.state.received_stream[before:])
    windows = extract_testclient_windows(blob)
    return {"windows": windows, "count": len(windows)}
