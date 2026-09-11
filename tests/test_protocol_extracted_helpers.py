import pytest

from qa_mcp.protocol import foreground
from qa_mcp.protocol import introspection


def test_open_bare_create_form_for_write_normalizes_link_and_sets_meta() -> None:
    calls = {}
    resource = object()

    def fake_foreground(open_link, **kwargs):
        calls["open_link"] = open_link
        calls["kwargs"] = kwargs
        return resource

    result, meta = foreground.open_bare_create_form_for_write(
        "e1cib/data/Справочник.Товары?ref=01234567-89ab-cdef-0123-456789abcdef",
        host="client",
        port=15432,
        foreground_form_by_link=fake_foreground,
    )

    assert result is resource
    assert calls["open_link"] == "e1cib/data/Справочник.Товары?ref=0123456789abcdefcdef89ab01234567"
    assert calls["kwargs"]["host"] == "client"
    assert calls["kwargs"]["port"] == 15432
    assert calls["kwargs"]["allow_partial"] is True
    assert meta["foreground_method"] == "create_listreplay"
    assert meta["partial_foreground_replay"] is True
    assert meta["normalized_open_link"] == calls["open_link"]


def test_open_bare_create_form_for_write_structures_failures() -> None:
    def failing_foreground(*_args, **_kwargs):
        raise RuntimeError("boom")

    result, meta = foreground.open_bare_create_form_for_write(
        "e1cib/data/Справочник.Товары",
        host="client",
        port=15432,
        foreground_form_by_link=failing_foreground,
    )

    assert result is None
    assert meta["error"] == "create-foreground-failed"
    assert "RuntimeError: boom" in meta["reason"]


def test_introspection_link_helpers() -> None:
    assert introspection._normalize_data_ref_link(
        "e1cib/data/Справочник.Товары?ref=01234567-89ab-cdef-0123-456789abcdef"
    ) == "e1cib/data/Справочник.Товары?ref=0123456789abcdefcdef89ab01234567"
    assert introspection._normalize_data_ref_link("e1cib/data/Справочник.Товары?ref=not-a-ref") \
        == "e1cib/data/Справочник.Товары?ref=not-a-ref"
    assert introspection._is_bare_create_data_link("e1cib/data/Справочник.Товары")
    assert not introspection._is_bare_create_data_link("e1cib/data/Справочник.Товары?ref=abc")
    assert not introspection._is_bare_create_data_link("e1cib/list/Справочник.Товары")


def test_splice_window_activate_command_builds_secondary_frame_path() -> None:
    secondary_frame = "11111111-2222-3333-4444-555555555555"
    rendered = b"header" + b"\xcb\x23\x95" + b"value-read-body"

    command = introspection._splice_window_activate_command(rendered, secondary_frame)

    assert command.startswith(b"header\xcb\x23\x95")
    assert f"SecondaryFrame[{secondary_frame}]".encode("latin1") in command
    assert command.endswith(b"\x88\x82\x81   fS\xb2\xa6")


def test_splice_window_activate_command_requires_header() -> None:
    with pytest.raises(ValueError, match="no cb-23-95"):
        introspection._splice_window_activate_command(b"no marker", "11111111-2222-3333-4444-555555555555")
