"""Card 98 #2 — OS window enumeration (windows.py): pure argv shapes + geometry parse + list_windows with
an injected runner (offline). The live xdotool path is exercised by the change-2 lab verify."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.protocol import windows as W  # noqa: E402


def test_argv_shapes() -> None:
    assert W._search_argv()[1:] == ["search", "--onlyvisible", "--name", ""]
    assert W._name_argv("0x42")[1:] == ["getwindowname", "0x42"]
    assert W._geometry_argv("0x42")[1:] == ["getwindowgeometry", "--shell", "0x42"]


def test_parse_geometry() -> None:
    out = "WINDOW=4194305\nX=10\nY=20\nWIDTH=800\nHEIGHT=600\nSCREEN=0\n"
    assert W.parse_geometry(out) == {"x": 10, "y": 20, "width": 800, "height": 600}


def test_parse_geometry_partial_and_garbage() -> None:
    assert W.parse_geometry("X=5\nWIDTH=not-an-int\nGARBAGE\n") == {"x": 5}
    assert W.parse_geometry("") == {}


def test_list_windows_with_injected_runner() -> None:
    def fake(argv: list[str]) -> str:
        action = argv[1]
        if action == "search":
            return "0x111\n0x222\n"
        if action == "getwindowname":
            return "Демо — 1С:Предприятие" if argv[2] == "0x111" else "Справочник Валюты"
        if action == "getwindowgeometry":
            return "X=0\nY=0\nWIDTH=1280\nHEIGHT=1024\n"
        return ""

    wins = W.list_windows(":99", runner=fake)
    assert [w["id"] for w in wins] == ["0x111", "0x222"]
    assert wins[0]["title"] == "Демо — 1С:Предприятие"          # Cyrillic title round-trips
    assert wins[1]["title"] == "Справочник Валюты"
    assert wins[0]["geometry"] == {"x": 0, "y": 0, "width": 1280, "height": 1024}


def test_list_windows_geometry_off() -> None:
    def fake(argv: list[str]) -> str:
        return "0x1\n" if argv[1] == "search" else "Main"

    wins = W.list_windows(":99", runner=fake, geometry=False)
    assert wins == [{"id": "0x1", "title": "Main"}]


def test_list_windows_empty() -> None:
    assert W.list_windows(":99", runner=lambda argv: "") == []
