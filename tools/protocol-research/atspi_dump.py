#!/usr/bin/env python3
"""Card 98 — AT-SPI introspection probe. Walks the accessibility-bus tree and reports which apps register and,
for any 1C app, dumps the accessible element tree (role / name / value / interfaces incl. EditableText/Action).
Answers: does the 1C thin client expose its form elements natively via AT-SPI (vs only via the TestClient
protocol)? Run inside the SAME D-Bus session as the launched 1C client + at-spi-bus-launcher.

    DBUS_SESSION_BUS_ADDRESS=... python3 atspi_dump.py
"""
from __future__ import annotations

import sys

import pyatspi  # type: ignore


def ifaces(node) -> list[str]:
    try:
        return list(node.get_interfaces())
    except Exception:
        try:
            return pyatspi.listInterfaces(node)
        except Exception:
            return []


def text_value(node) -> str:
    try:
        ii = ifaces(node)
        if any("Text" in x for x in ii):
            t = node.queryText()
            return t.getText(0, t.characterCount)
    except Exception:
        pass
    return ""


def dump(node, depth: int, maxdepth: int, counter: list[int]) -> None:
    counter[0] += 1
    try:
        role = node.getRoleName()
    except Exception:
        role = "?"
    try:
        name = node.name
    except Exception:
        name = "?"
    ii = ifaces(node)
    short = [x.replace("Accessible", "") for x in ii]
    editable = any("EditableText" in x for x in ii)
    action = any("Action" in x for x in ii)
    val = text_value(node)
    flags = ("  <EDITABLE>" if editable else "") + ("  <ACTION>" if action else "")
    print(f"{'  ' * depth}[{role}] name={name!r} val={val!r} ifaces={short}{flags}")
    if depth >= maxdepth:
        return
    try:
        for ch in node:
            if ch is not None:
                dump(ch, depth + 1, maxdepth, counter)
    except Exception as e:  # noqa: BLE001
        print(f"{'  ' * (depth + 1)}<children error: {e}>")


def main() -> int:
    maxdepth = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    desktop = pyatspi.Registry.getDesktop(0)
    n = desktop.childCount
    print(f"=== AT-SPI desktop: {n} application(s) registered ===")
    apps = []
    for i in range(n):
        try:
            app = desktop.getChildAtIndex(i)
            nm = app.name
            print(f"  app[{i}] name={nm!r} role={app.getRoleName()} children={app.childCount}")
            apps.append(app)
        except Exception as e:  # noqa: BLE001
            print(f"  app[{i}] <error: {e}>")
    # dump any 1C app (and, if none obviously 1C, dump every app shallowly)
    onec = [a for a in apps if any(k in (a.name or "") for k in ("1С", "1C", "1cv8")) or "1c" in (a.name or "").lower()]
    targets = onec if onec else apps
    for app in targets:
        print(f"\n=== TREE: app name={app.name!r} ===")
        counter = [0]
        dump(app, 0, maxdepth, counter)
        print(f"  ({counter[0]} nodes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
