from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools" / "protocol-research"
sys.path.insert(0, str(TOOLS_DIR))

from promote_member import promote  # noqa: E402


def test_promote_adds_new_member(tmp_path: Path) -> None:
    map_path = tmp_path / "mutation-evidence-map.json"
    map_path.write_text(json.dumps({"schema": "x", "members": []}), encoding="utf-8")
    data = promote(map_path, "TestedFormTable.AddRow", "candidate", "docs/ev/", "added a row")
    member = data["members"][0]
    assert member == {
        "api": "TestedFormTable.AddRow",
        "bucket": "candidate",
        "evidence_path": "docs/ev/",
        "note": "added a row",
    }
    # persisted
    assert json.loads(map_path.read_text(encoding="utf-8"))["members"][0]["api"] == "TestedFormTable.AddRow"


def test_promote_updates_existing_member(tmp_path: Path) -> None:
    map_path = tmp_path / "m.json"
    map_path.write_text(
        json.dumps({"members": [{"api": "TestedFormButton.Click", "bucket": "candidate"}]}),
        encoding="utf-8",
    )
    data = promote(map_path, "TestedFormButton.Click", "accepted_reviewed", "docs/ev/", "")
    assert len(data["members"]) == 1
    assert data["members"][0]["bucket"] == "accepted_reviewed"
    assert data["members"][0]["evidence_path"] == "docs/ev/"
