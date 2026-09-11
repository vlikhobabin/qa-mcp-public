"""Card 97 #5 — first-class assert + WaitForCondition (assert_form_value / wait_for_form_value).

The read primitive (_read_field_value) needs a live /TESTCLIENT, so it is monkeypatched here; these tests
cover the pure comparison + the poll/timeout orchestration. Live read-back is verified by the probe
tools/protocol-research/assert_wait_verify.py."""
import pytest

import qa_mcp.mcp_server as srv


def test_match_value_modes():
    assert srv._match_value("abc", "abc", "equals")
    assert not srv._match_value("abc", "ab", "equals")
    assert srv._match_value("hello world", "world", "contains")
    assert not srv._match_value("hello", "world", "contains")
    assert srv._match_value("PF_TABLE[3]=PF_ROW_001", r"PF_TABLE\[\d+\]", "regex")
    assert not srv._match_value("PF_TABLE[3]=x", r"PF_SEL\[\d+\]", "regex")
    assert not srv._match_value(None, "anything", "equals")  # 0x88 no-value stub never matches
    with pytest.raises(ValueError):
        srv._match_value("a", "a", "bogus")


def test_parse_1c_number():
    from decimal import Decimal
    assert srv._parse_1c_number("120,50") == Decimal("120.5")      # RU comma decimal
    assert srv._parse_1c_number("120.50") == Decimal("120.5")      # dot decimal
    assert srv._parse_1c_number("1 234,50") == Decimal("1234.5")   # plain-space thousands
    assert srv._parse_1c_number("1 234,50") == Decimal("1234.5")  # NBSP thousands
    assert srv._parse_1c_number("-5,5") == Decimal("-5.5")         # negative
    assert srv._parse_1c_number("0") == Decimal("0")
    assert srv._parse_1c_number(None) is None
    assert srv._parse_1c_number("abc") is None
    assert srv._parse_1c_number("") is None
    assert srv._parse_1c_number("-") is None


def test_match_value_numeric_mode():
    # card 97 #3: a number rides the wire as localized display text "120,50" — numeric compare is format-robust
    assert srv._match_value("120,50", "120.5", "numeric")
    assert srv._match_value("120,50", "120.50", "numeric")
    assert srv._match_value("120,50", "120,5", "numeric")
    assert srv._match_value("1 234,50", "1234.5", "numeric")
    assert not srv._match_value("120,50", "121", "numeric")
    assert not srv._match_value("abc", "1", "numeric")  # non-numeric actual never matches
    assert not srv._match_value(None, "1", "numeric")   # no-value stub never matches


def test_assert_form_value_numeric(monkeypatch):
    monkeypatch.setattr(srv, "_read_field_value", lambda field, **k: "120,50")
    ok = srv.assert_form_value("PF_EDIT_NUMBER", "120.5", mode="numeric")
    assert ok["passed"] and ok["actual"] == "120,50" and ok["mode"] == "numeric"


# --- Card 97 #2-read: cross-region full-path retarget (read a field in another Group) -----------------------
_S, _F = "44e53dad-5631-419a-a34a-09de536dc612", "2582c122-d42a-4ef2-9b35-fd3f5ed63948"


def _value_read_query_frame() -> bytes:
    # mirror the genuine value-read query: a length-prefixed element path for the editable-region leaf
    path = (f"SecondaryFrame[{_S}].ManagedForm[{_F}]"
            ".Group[PF_GROUP_MAIN].Group[PF_GROUP_EDITS].EditField[PF_EDIT_STRING]")
    return b"\x9a" + bytes([len(path)]) + path.encode("latin1") + b"\x20\x20\x20"


def test_cross_region_retarget_drops_subgroup():
    # PF_GROUP_MAIN markers sit one group above the captured PF_GROUP_EDITS region: swap the WHOLE path
    out = srv._retarget_read_to_groups(_value_read_query_frame(), "PF_EDIT_STRING", "PF_LAST_ACTION", ["PF_GROUP_MAIN"])
    new = f"SecondaryFrame[{_S}].ManagedForm[{_F}].Group[PF_GROUP_MAIN].EditField[PF_LAST_ACTION]"
    assert (bytes([len(new)]) + new.encode("latin1")) in out  # length-prefix recomputed for the new path
    assert b"EditField[PF_EDIT_STRING]" not in out            # captured leaf swapped out
    assert b"Group[PF_GROUP_EDITS]" not in out                # the editable-region container dropped


def test_cross_region_retarget_other_subgroup():
    # a field in a different SUBGROUP keeps PF_GROUP_MAIN and swaps the subgroup
    out = srv._retarget_read_to_groups(
        _value_read_query_frame(), "PF_EDIT_STRING", "PF_V4_SUPPORTED_SCENARIOS",
        ["PF_GROUP_MAIN", "PF_GROUP_DIALOG_RECOVERY_V4"])
    new = (f"SecondaryFrame[{_S}].ManagedForm[{_F}]"
           ".Group[PF_GROUP_MAIN].Group[PF_GROUP_DIALOG_RECOVERY_V4].EditField[PF_V4_SUPPORTED_SCENARIOS]")
    assert (bytes([len(new)]) + new.encode("latin1")) in out


def test_cross_region_retarget_noop_without_captured_leaf():
    # a frame that does not carry the captured leaf is returned unchanged
    frame = b"\x9a\x10NOTHING_TO_DO_HERE"
    assert srv._retarget_read_to_groups(frame, "PF_EDIT_STRING", "PF_LAST_ACTION", ["PF_GROUP_MAIN"]) == frame


def test_assert_form_value_pass_and_fail(monkeypatch):
    monkeypatch.setattr(srv, "_read_field_value", lambda field, **k: "protocol-fixture.v1")
    ok = srv.assert_form_value("PF_FIXTURE_VERSION", "protocol-fixture.v1")
    assert ok["passed"] and ok["actual"] == "protocol-fixture.v1" and ok["mode"] == "equals"
    bad = srv.assert_form_value("PF_FIXTURE_VERSION", "WRONG")
    assert not bad["passed"] and bad["actual"] == "protocol-fixture.v1"


def test_assert_form_value_none_fails(monkeypatch):
    monkeypatch.setattr(srv, "_read_field_value", lambda field, **k: None)
    r = srv.assert_form_value("MISSING", "x")
    assert r["passed"] is False and r["actual"] is None


def test_wait_satisfies_after_a_few_polls(monkeypatch):
    seq = iter([None, "PENDING", "PENDING", "DONE"])
    monkeypatch.setattr(srv, "_read_field_value", lambda field, **k: next(seq))
    r = srv.wait_for_form_value("F", "DONE", timeout_sec=5.0, interval_sec=0.001)
    assert r["satisfied"] is True and r["polls"] == 4 and r["actual"] == "DONE"


def test_wait_times_out_and_reports_last_value(monkeypatch):
    monkeypatch.setattr(srv, "_read_field_value", lambda field, **k: "never")
    r = srv.wait_for_form_value("F", "TARGET", timeout_sec=0.05, interval_sec=0.01)
    assert r["satisfied"] is False and r["polls"] >= 1 and r["actual"] == "never"


def test_wait_satisfies_on_first_poll(monkeypatch):
    monkeypatch.setattr(srv, "_read_field_value", lambda field, **k: "READY")
    r = srv.wait_for_form_value("F", "READY", timeout_sec=5.0, interval_sec=0.5)
    assert r["satisfied"] is True and r["polls"] == 1


def test_wait_rejects_bad_intervals():
    result = srv.wait_for_form_value("F", "X", interval_sec=0)
    assert result["ok"] is False
    assert result["error"] == "invalid-arguments"
    assert result["tool"] == "wait_for_form_value"
