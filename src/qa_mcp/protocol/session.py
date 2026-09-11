"""Read-only direct TCP session API for a running 1C `/TESTCLIENT`."""

from __future__ import annotations

import json
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .bootstrap import CaptureBootstrap
from .bootstrap_synth import SynthesizedBootstrap
from .element_ref import retarget_element_leaf
from .evidence import OperationDescriptor, get_readonly_operation_descriptor
from .frames import (
    adapt_manager_header_guid,
    extract_client_ack_guid,
    extract_managed_form_guid,
    extract_secondary_frame_guid,
    manager_frame_sequence,
    preview_hex,
    sha256_hex,
)
from .responses import (
    extract_active_form_fields,
    extract_active_window_fields,
    extract_edit_field_value,
    extract_element_details,
    extract_form_elements,
    response_summary,
    value_mode_present,
)
from .templates import BootstrapFrameRenderer, ProtocolTemplates, RenderedFrame
from .transport import connect_testclient, read_protocol_available


# The field that the default value-read frames (218..221) address in the read-only capture; card-86a
# addressing re-targets the element path leaf from this to the requested field.
_VALUE_READ_CAPTURED_FIELD = "PF_EDIT_STRING"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def timestamp_name() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def read_available(sock: socket.socket, first_timeout_sec: float, idle_timeout_sec: float) -> bytes:
    return read_protocol_available(sock, first_timeout_sec, idle_timeout_sec)


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as file_obj:
        for record in records:
            file_obj.write(json.dumps(record, ensure_ascii=False) + "\n")


@dataclass
class InitialUiContext:
    status: str
    capture_dir: Path
    templates_path: Path
    output_dir: Path
    descriptor: OperationDescriptor
    ack_guid: str | None
    frame4_sequence: int | None
    sent_byte_count: int
    received_byte_count: int
    frames: list[dict[str, Any]]
    events: list[dict[str, Any]] = field(default_factory=list)
    finished_at: str = field(default_factory=utc_now)

    def to_result(self) -> dict[str, Any]:
        return {
            "schema": "python-manager-probe.result.v1",
            "status": self.status,
            "query": self.descriptor.query,
            "case_id": self.descriptor.case_id,
            "evidence_status": self.descriptor.acceptance_status.value,
            "descriptor": self.descriptor.to_dict(),
            "capture_dir": str(self.capture_dir),
            "templates": str(self.templates_path),
            "output_dir": str(self.output_dir),
            "ack_guid": self.ack_guid,
            "frame4_sequence": self.frame4_sequence,
            "sent_byte_count": self.sent_byte_count,
            "received_byte_count": self.received_byte_count,
            "frames": self.frames,
            "finished_at": self.finished_at,
        }


@dataclass
class ActiveWindowContext:
    base_context: InitialUiContext
    active_window_ref: str | None
    active_window_markers: list[str]

    def to_result(self) -> dict[str, Any]:
        result = self.base_context.to_result()
        result["schema"] = "python-manager-active-window-context.result.v1"
        result["active_window_ref"] = self.active_window_ref
        result["active_window_markers"] = self.active_window_markers
        return result


@dataclass
class ActiveFormContext:
    base_context: InitialUiContext
    active_form_name: str | None
    active_form_caption: str | None
    managed_form_ref: str | None

    def to_result(self) -> dict[str, Any]:
        result = self.base_context.to_result()
        result["schema"] = "python-manager-active-form-context.result.v1"
        result["active_form_name"] = self.active_form_name
        result["active_form_caption"] = self.active_form_caption
        result["managed_form_ref"] = self.managed_form_ref
        return result


@dataclass
class FormSummaryContext:
    base_context: InitialUiContext
    active_form_name: str | None
    active_form_caption: str | None
    managed_form_ref: str | None
    elements: list[dict[str, Any]]

    def to_result(self) -> dict[str, Any]:
        result = self.base_context.to_result()
        result["schema"] = "python-manager-form-summary.result.v1"
        result["active_form_name"] = self.active_form_name
        result["active_form_caption"] = self.active_form_caption
        result["managed_form_ref"] = self.managed_form_ref
        result["elements"] = self.elements
        result["element_count"] = len(self.elements)
        return result


@dataclass
class FormElementDetailsContext:
    base_context: InitialUiContext
    active_form_name: str | None
    active_form_caption: str | None
    managed_form_ref: str | None
    elements: list[dict[str, Any]]
    element_details: list[dict[str, Any]]
    frame_mode: str

    def to_result(self) -> dict[str, Any]:
        result = self.base_context.to_result()
        result["schema"] = "python-manager-form-element-details.result.v1"
        result["active_form_name"] = self.active_form_name
        result["active_form_caption"] = self.active_form_caption
        result["managed_form_ref"] = self.managed_form_ref
        result["elements"] = self.elements
        result["element_count"] = len(self.elements)
        result["element_details"] = self.element_details
        result["element_detail_count"] = len(self.element_details)
        result["frame_mode"] = self.frame_mode
        return result


@dataclass
class FormValueContext:
    """Card 79 (Fork 1): the LIVE data value of a form field, read off the wire for effect
    verification on a READ. ``value`` is None when the response carried the 0x88 no-value stub
    (e.g. the form was not actually open)."""

    base_context: InitialUiContext
    field: str
    value: str | None
    value_mode_on: bool
    secondary_frame_ref: str | None

    def to_result(self) -> dict[str, Any]:
        result = self.base_context.to_result()
        result["schema"] = "python-manager-form-value.result.v1"
        result["field"] = self.field
        result["value"] = self.value
        result["value_mode_on"] = self.value_mode_on
        result["secondary_frame_ref"] = self.secondary_frame_ref
        return result


@dataclass
class _ExchangeState:
    """Mutable handshake/stream state shared across frames in one socket exchange."""

    ack_guid: str | None = None
    frame4_sequence: int | None = None
    managed_form_guid: str | None = None
    secondary_frame_guid: str | None = None
    sent_stream: bytearray = field(default_factory=bytearray)
    received_stream: bytearray = field(default_factory=bytearray)
    events: list[dict[str, Any]] = field(default_factory=list)
    frame_summaries: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SessionHandle:
    """An open, already-bootstrapped session: run multiple operation segments on one socket
    without re-bootstrapping (card 74 Phase 2)."""

    session: "TestClientSession"
    bootstrap: CaptureBootstrap
    templates: ProtocolTemplates
    synthesized: "SynthesizedBootstrap | None"
    state: _ExchangeState
    steps_dir: Path
    summary_from_frame: int = 8
    cursor: int = 11  # next contiguous operation frame (frames 1..10 are the bootstrap)

    def run_segment(
        self, frame_indices: list[int], query_id: str,
        frame_rewriter: "Callable[[int, bytes], bytes] | None" = None,
    ) -> InitialUiContext:
        return self.session._run_segment(self, frame_indices, query_id, frame_rewriter=frame_rewriter)

    def _advance_to(self, target_frame: int, query_id: str) -> InitialUiContext:
        """Send the contiguous operation frames from the cursor up to target_frame (order-
        dependent: the linear template requires increasing targets within one session)."""
        if target_frame < self.cursor:
            raise RuntimeError(
                f"single-session steps are order-dependent: cursor={self.cursor} already past "
                f"target frame {target_frame} for {query_id!r}"
            )
        frames = list(range(self.cursor, target_frame + 1))
        self.cursor = target_frame + 1
        return self.run_segment(frames, query_id)

    def active_window(self) -> "ActiveWindowContext":
        base = self._advance_to(11, "active-window-context")
        frame = next((f for f in reversed(base.frames) if f.get("semantic_guess")), None)
        return ActiveWindowContext(base_context=base, **extract_active_window_fields(frame or {}))

    def form_summary(self) -> "FormSummaryContext":
        base = self._advance_to(17, "form-summary")
        active_frame = next(
            (f for f in reversed(base.frames) if f.get("semantic_guess") == "active_form_descriptor"), None
        )
        element_frame = next(
            (f for f in reversed(base.frames) if f.get("semantic_guess") == "form_element_summary"), None
        )
        fields = extract_active_form_fields(active_frame or {})
        elements = extract_form_elements(element_frame or {})
        return FormSummaryContext(base_context=base, elements=elements, **fields)

    def read_form_value(
        self,
        *,
        field: str = "PF_EDIT_STRING",
        open_frames_through: int = 17,
        value_frames: list[int] | None = None,
    ) -> "FormValueContext":
        """Card 79 (Fork 1) — EFFECT verification on a READ. Open the fixture form (run the
        contiguous open sequence up to ``open_frames_through`` if this session has not reached it
        yet), then run the value-read segment and parse the field's LIVE value. The value-read
        frames carry the rebindable SecondaryFrame GUID, resolved from this session's open form
        (proven live: an unopened form returns the 0x88 no-value stub → ``value`` is None)."""
        if value_frames is None:
            value_frames = [218, 219, 220, 221]
        if self.cursor <= open_frames_through:
            self._advance_to(open_frames_through, "form-summary")
        # Card 86a: the captured value-read frames address PF_EDIT_STRING; to read ANOTHER field
        # capture-free, re-target the element-address path leaf to `field` (same enclosing group). The
        # rewrite runs AFTER GUID rebind, so it is GUID-neutral — only the leaf name + length prefix change.
        rewriter: "Callable[[int, bytes], bytes] | None" = None
        if field != _VALUE_READ_CAPTURED_FIELD:
            def rewriter(_idx: int, payload: bytes, _field: str = field) -> bytes:
                try:
                    out, _ = retarget_element_leaf(payload, _VALUE_READ_CAPTURED_FIELD, _field)
                    return out
                except ValueError:
                    return payload
        before = len(self.state.received_stream)
        base = self.run_segment(value_frames, query_id="form-value-read", frame_rewriter=rewriter)
        blob = bytes(self.state.received_stream[before:])
        return FormValueContext(
            base_context=base,
            field=field,
            value=extract_edit_field_value(blob, field),
            value_mode_on=value_mode_present(blob, field),
            secondary_frame_ref=self.state.secondary_frame_guid,
        )

    def run_action(self, command_payload: bytes, *, query_id: str = "action", rebinder: Any = None) -> dict[str, Any]:
        """Card 78 Phase A: send a captured ACTION command frame on the already-open socket
        (continuing THIS synthesized session) and read the client's response — no re-bootstrap,
        no Vanessa. ``command_payload`` is a captured action command template; if ``rebinder`` (any
        object with ``.apply(bytes) -> bytes``) is given, its captured->live GUID map is applied so
        the frame targets this live session. Returns a summary dict; ``accepted`` is True when the
        client responded (did not reject/close the connection)."""
        payload = rebinder.apply(command_payload) if rebinder is not None else command_payload
        response = self.session.send_and_read(payload)
        self.state.sent_stream.extend(payload)
        self.state.received_stream.extend(response)
        summary = {
            "query_id": query_id,
            "sent_bytes": len(payload),
            "recv_bytes": len(response),
            "adapted": payload != command_payload,
            "accepted": bool(response),
        }
        self.state.events.append({"ts": utc_now(), "event": "action", **summary})
        return summary


class TestClientSession:
    """Direct read-only TCP session against a running 1C `/TESTCLIENT` listener."""

    __test__ = False

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 15381,
        connect_timeout_sec: float = 10.0,
        read_timeout_sec: float = 5.0,
        idle_timeout_sec: float = 0.25,
    ) -> None:
        self.host = host
        self.port = port
        self.connect_timeout_sec = connect_timeout_sec
        self.read_timeout_sec = read_timeout_sec
        self.idle_timeout_sec = idle_timeout_sec
        self._socket: socket.socket | None = None

    def __enter__(self) -> "TestClientSession":
        self.connect()
        return self

    def __exit__(self, _exc_type: object, _exc: object, _tb: object) -> None:
        self.close()

    def connect(self) -> None:
        if self._socket is not None:
            return
        sock = connect_testclient((self.host, self.port), timeout=self.connect_timeout_sec)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._socket = sock

    def close(self) -> None:
        if self._socket is None:
            return
        try:
            self._socket.close()
        finally:
            self._socket = None

    @property
    def socket(self) -> socket.socket:
        if self._socket is None:
            raise RuntimeError("TestClientSession is not connected")
        return self._socket

    def read_initial(self) -> bytes:
        return read_available(self.socket, self.read_timeout_sec, self.idle_timeout_sec)

    def send_and_read(self, payload: bytes) -> bytes:
        self.socket.sendall(payload)
        return read_available(self.socket, self.read_timeout_sec, self.idle_timeout_sec)

    def render_initial_ui_frame(
        self,
        frame_index: int,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        ack_guid: str | None,
        frame4_sequence: int | None,
        managed_form_guid: str | None = None,
        synthesized: "SynthesizedBootstrap | None" = None,
        secondary_frame_guid: str | None = None,
    ) -> tuple[RenderedFrame, int | None]:
        captured = bootstrap.captured_frame(frame_index)

        if frame_index in (1, 2, 3):
            if synthesized is not None:
                # Card 62: render frames 1..3 from the in-repo static template + fresh
                # dynamic fields — no captured bytes consumed for these frames.
                return (
                    RenderedFrame(
                        payload=synthesized.frame(frame_index),
                        replacements=[],
                        source="synthesized_bootstrap_1to3",
                    ),
                    frame4_sequence,
                )
            return RenderedFrame(payload=captured, replacements=[], source="captured"), frame4_sequence
        # Card 73: when synthesizing, frames 4..7 are rendered from the in-repo static
        # template (synthesized.template_frame) instead of the captured frame, with a single
        # message-counter sequence threaded from the synthesized base.
        base_4to7 = synthesized.template_frame if synthesized is not None else None
        if frame_index == 4:
            if ack_guid is None:
                raise RuntimeError("ACK GUID is not available before manager frame 4")
            if synthesized is not None:
                return (
                    RenderedFrame(
                        payload=synthesized.render_frame4(ack_guid),
                        replacements=[],
                        source="synthesized_bootstrap_4to7",
                    ),
                    synthesized.frame4_sequence,
                )
            payload, original_guid = adapt_manager_header_guid(captured, ack_guid)
            sequence = manager_frame_sequence(captured)
            return (
                RenderedFrame(
                    payload=payload,
                    source="captured_text_template",
                    replacements=[
                        {
                            "name": "ack_guid",
                            "offset": 3,
                            "length": len(original_guid),
                            "original": original_guid,
                            "replacement": ack_guid,
                        }
                    ],
                ),
                sequence,
            )
        if frame_index == 5:
            if ack_guid is None or frame4_sequence is None:
                raise RuntimeError("Handshake state is incomplete before manager frame 5")
            block = base_4to7(5) if base_4to7 is not None else captured
            rendered = BootstrapFrameRenderer.render_frame5(block, ack_guid, frame4_sequence)
            if synthesized is not None:
                rendered = RenderedFrame(payload=rendered.payload, replacements=rendered.replacements, source="synthesized_bootstrap_4to7")
            return rendered, frame4_sequence
        if frame_index in (6, 7):
            if ack_guid is None or frame4_sequence is None:
                raise RuntimeError("Handshake state is incomplete before manager frame 6/7")
            block = base_4to7(frame_index) if base_4to7 is not None else captured
            rendered = BootstrapFrameRenderer.render_single_block_frame(block, ack_guid, frame4_sequence, frame_index)
            if synthesized is not None:
                rendered = RenderedFrame(payload=rendered.payload, replacements=rendered.replacements, source="synthesized_bootstrap_4to7")
            return rendered, frame4_sequence
        if frame_index >= 8:
            if ack_guid is None or frame4_sequence is None:
                raise RuntimeError("Handshake state is incomplete before manager template frames")
            return (
                templates.render(
                    frame_index, ack_guid, frame4_sequence, managed_form_guid, secondary_frame_guid
                ),
                frame4_sequence,
            )
        raise RuntimeError(f"Unexpected initial UI frame index: {frame_index}")

    def exchange_template_frames(
        self,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        output_dir: Path,
        last_frame: int,
        query_id: str,
        summary_from_frame: int = 8,
        frame_indices: list[int] | None = None,
        synthesized: "SynthesizedBootstrap | None" = None,
    ) -> InitialUiContext:
        if last_frame < 10:
            raise ValueError("last_frame must be at least 10 for the initial UI context")
        if frame_indices is None:
            frame_indices = list(range(1, last_frame + 1))
        if not frame_indices:
            raise ValueError("frame_indices must not be empty")

        descriptor = get_readonly_operation_descriptor(query_id)
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        steps_dir = output_dir / "steps"
        steps_dir.mkdir(parents=True, exist_ok=True)

        events: list[dict[str, Any]] = []
        sent_stream = bytearray()
        received_stream = bytearray()
        frame_summaries: list[dict[str, Any]] = []
        ack_guid: str | None = None
        frame4_sequence: int | None = None
        managed_form_guid: str | None = None

        events.append({"ts": utc_now(), "event": "connected"})
        initial = self.read_initial()
        received_stream.extend(initial)
        (steps_dir / "initial_read.bin").write_bytes(initial)
        events.append(
            {
                "ts": utc_now(),
                "event": "initial_read",
                "byte_count": len(initial),
                "sha256": sha256_hex(initial) if initial else "",
                "head_hex": preview_hex(initial),
            }
        )

        state = _ExchangeState(
            ack_guid=ack_guid,
            frame4_sequence=frame4_sequence,
            managed_form_guid=managed_form_guid,
            sent_stream=sent_stream,
            received_stream=received_stream,
            events=events,
            frame_summaries=frame_summaries,
        )
        for frame_index in frame_indices:
            self._process_frame(
                frame_index=frame_index,
                state=state,
                bootstrap=bootstrap,
                templates=templates,
                synthesized=synthesized,
                summary_from_frame=summary_from_frame,
                steps_dir=steps_dir,
            )

        (output_dir / "sent_manager_to_client.bin").write_bytes(bytes(state.sent_stream))
        (output_dir / "received_client_to_manager.bin").write_bytes(bytes(state.received_stream))
        write_jsonl(output_dir / "probe_events.jsonl", state.events)

        return InitialUiContext(
            status="ok",
            capture_dir=bootstrap.capture_dir,
            templates_path=templates.path,
            output_dir=output_dir,
            descriptor=descriptor,
            ack_guid=state.ack_guid,
            frame4_sequence=state.frame4_sequence,
            sent_byte_count=len(state.sent_stream),
            received_byte_count=len(state.received_stream),
            frames=state.frame_summaries,
            events=state.events,
        )

    def _process_frame(
        self,
        frame_index: int,
        state: _ExchangeState,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        synthesized: "SynthesizedBootstrap | None",
        summary_from_frame: int,
        steps_dir: Path,
        frame_rewriter: "Callable[[int, bytes], bytes] | None" = None,
    ) -> None:
        rendered, state.frame4_sequence = self.render_initial_ui_frame(
            frame_index=frame_index,
            bootstrap=bootstrap,
            templates=templates,
            ack_guid=state.ack_guid,
            frame4_sequence=state.frame4_sequence,
            managed_form_guid=state.managed_form_guid,
            synthesized=synthesized,
            secondary_frame_guid=state.secondary_frame_guid,
        )
        payload = rendered.payload
        if frame_rewriter is not None:  # card 86a: re-target element address (path) before send
            payload = frame_rewriter(frame_index, payload)
        (steps_dir / f"sent_{frame_index:03d}_manager_to_client.bin").write_bytes(payload)
        self.socket.sendall(payload)
        state.sent_stream.extend(payload)
        state.events.append(
            {
                "ts": utc_now(),
                "event": "sent",
                "send_index": frame_index,
                "source": rendered.source,
                "byte_count": len(payload),
                "sha256": sha256_hex(payload),
                "head_hex": preview_hex(payload),
                "replacements": rendered.replacements,
            }
        )

        response = read_available(self.socket, self.read_timeout_sec, self.idle_timeout_sec)
        state.received_stream.extend(response)
        (steps_dir / f"response_after_send_{frame_index:03d}_client_to_manager.bin").write_bytes(response)
        state.events.append(
            {
                "ts": utc_now(),
                "event": "response",
                "after_send_index": frame_index,
                "byte_count": len(response),
                "sha256": sha256_hex(response) if response else "",
                "head_hex": preview_hex(response),
            }
        )

        if frame_index == 3:
            state.ack_guid = extract_client_ack_guid(response)
            state.events.append(
                {"ts": utc_now(), "event": "observed_ack_guid", "after_send_index": frame_index, "ack_guid": state.ack_guid}
            )
        if summary_from_frame <= frame_index:
            state.frame_summaries.append(response_summary(frame_index, response, rendered.replacements))
            observed = extract_managed_form_guid(response)
            if observed and observed != state.managed_form_guid:
                state.managed_form_guid = observed
                state.events.append(
                    {"ts": utc_now(), "event": "observed_managed_form_guid", "after_send_index": frame_index, "guid": observed}
                )
            observed_sf = extract_secondary_frame_guid(response)
            if observed_sf and observed_sf != state.secondary_frame_guid:
                state.secondary_frame_guid = observed_sf
                state.events.append(
                    {"ts": utc_now(), "event": "observed_secondary_frame_guid", "after_send_index": frame_index, "guid": observed_sf}
                )

    def open_and_bootstrap(
        self,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        output_dir: Path,
        synthesized: "SynthesizedBootstrap | None" = None,
        bootstrap_last_frame: int = 10,
        summary_from_frame: int = 8,
    ) -> SessionHandle:
        """Card 74 Phase 2: run the handshake/initial-UI frames (1..bootstrap_last_frame) ONCE,
        then leave the socket open so multiple operation segments can run via the returned
        SessionHandle without re-bootstrapping."""
        output_dir = output_dir.resolve()
        steps_dir = output_dir / "steps"
        steps_dir.mkdir(parents=True, exist_ok=True)

        state = _ExchangeState()
        initial = self.read_initial()
        state.received_stream.extend(initial)
        (steps_dir / "initial_read.bin").write_bytes(initial)
        state.events.append({"ts": utc_now(), "event": "initial_read", "byte_count": len(initial)})
        for frame_index in range(1, bootstrap_last_frame + 1):
            self._process_frame(
                frame_index=frame_index,
                state=state,
                bootstrap=bootstrap,
                templates=templates,
                synthesized=synthesized,
                summary_from_frame=summary_from_frame,
                steps_dir=steps_dir,
            )
        return SessionHandle(
            session=self,
            bootstrap=bootstrap,
            templates=templates,
            synthesized=synthesized,
            state=state,
            steps_dir=steps_dir,
            summary_from_frame=summary_from_frame,
        )

    def _run_segment(
        self, handle: SessionHandle, frame_indices: list[int], query_id: str,
        frame_rewriter: "Callable[[int, bytes], bytes] | None" = None,
    ) -> InitialUiContext:
        """Send one operation segment on the already-bootstrapped socket, continuing the
        handshake state (sequence cursor / managed-form GUID) from the handle. ``frame_rewriter``
        (card 86a) optionally rewrites each rendered payload before send — e.g. to re-target the
        element-address path to a different field, addressing it capture-free."""
        state = handle.state
        before = len(state.frame_summaries)
        for frame_index in frame_indices:
            self._process_frame(
                frame_index=frame_index,
                state=state,
                bootstrap=handle.bootstrap,
                templates=handle.templates,
                synthesized=handle.synthesized,
                summary_from_frame=handle.summary_from_frame,
                steps_dir=handle.steps_dir,
                frame_rewriter=frame_rewriter,
            )
        return InitialUiContext(
            status="ok",
            capture_dir=handle.bootstrap.capture_dir,
            templates_path=handle.templates.path,
            output_dir=handle.steps_dir.parent,
            descriptor=get_readonly_operation_descriptor(query_id),
            ack_guid=state.ack_guid,
            frame4_sequence=state.frame4_sequence,
            sent_byte_count=len(state.sent_stream),
            received_byte_count=len(state.received_stream),
            frames=state.frame_summaries[before:],
            events=state.events,
        )

    def get_initial_ui_context(
        self,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        output_dir: Path,
    ) -> InitialUiContext:
        return self.exchange_template_frames(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            last_frame=10,
            query_id="initial-ui",
            summary_from_frame=8,
        )

    def get_active_window_context(
        self,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        output_dir: Path,
        synthesized: "SynthesizedBootstrap | None" = None,
    ) -> ActiveWindowContext:
        base_context = self.exchange_template_frames(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            last_frame=11,
            query_id="active-window-context",
            summary_from_frame=8,
            synthesized=synthesized,
        )
        frame = next((item for item in reversed(base_context.frames) if item.get("semantic_guess")), None)
        fields = extract_active_window_fields(frame or {})
        return ActiveWindowContext(base_context=base_context, **fields)

    def get_active_form_context(
        self,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        output_dir: Path,
    ) -> ActiveFormContext:
        base_context = self.exchange_template_frames(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            last_frame=12,
            query_id="active-form-context",
            summary_from_frame=8,
        )
        frame12 = next((frame for frame in base_context.frames if frame.get("send_index") == 12), None)
        fields = extract_active_form_fields(frame12 or {})
        return ActiveFormContext(base_context=base_context, **fields)

    def get_form_summary(
        self,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        output_dir: Path,
        synthesized: "SynthesizedBootstrap | None" = None,
    ) -> FormSummaryContext:
        base_context = self.exchange_template_frames(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            last_frame=17,
            query_id="form-summary",
            summary_from_frame=8,
            synthesized=synthesized,
        )
        active_frame = next(
            (frame for frame in reversed(base_context.frames) if frame.get("semantic_guess") == "active_form_descriptor"),
            None,
        )
        element_frame = next(
            (frame for frame in reversed(base_context.frames) if frame.get("semantic_guess") == "form_element_summary"),
            None,
        )
        fields = extract_active_form_fields(active_frame or {})
        elements = extract_form_elements(element_frame or {})
        return FormSummaryContext(base_context=base_context, elements=elements, **fields)

    def get_form_element_details(
        self,
        bootstrap: CaptureBootstrap,
        templates: ProtocolTemplates,
        output_dir: Path,
        frame_mode: str = "short",
    ) -> FormElementDetailsContext:
        if frame_mode == "short":
            frame_indices = list(range(1, 18)) + list(range(101, 107))
        elif frame_mode == "full":
            frame_indices = list(range(1, 107))
        else:
            raise ValueError(f"Unsupported frame_mode: {frame_mode}")

        base_context = self.exchange_template_frames(
            bootstrap=bootstrap,
            templates=templates,
            output_dir=output_dir,
            last_frame=106,
            query_id="form-element-details",
            summary_from_frame=8,
            frame_indices=frame_indices,
        )
        active_frame = next(
            (frame for frame in reversed(base_context.frames) if frame.get("semantic_guess") == "active_form_descriptor"),
            None,
        )
        element_summary_frame = next(
            (
                frame
                for frame in reversed(base_context.frames)
                if frame.get("send_index") == 17 and frame.get("semantic_guess") == "form_element_summary"
            ),
            None,
        )
        fields = extract_active_form_fields(active_frame or {})
        elements = extract_form_elements(element_summary_frame or {})
        details = extract_element_details(
            [frame for frame in base_context.frames if int(frame.get("send_index", 0)) >= 101]
        )
        return FormElementDetailsContext(
            base_context=base_context,
            elements=elements,
            element_details=details,
            frame_mode=frame_mode,
            **fields,
        )
