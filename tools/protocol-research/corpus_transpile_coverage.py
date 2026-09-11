#!/usr/bin/env python3
"""Card 103 (E-FW step-library) — measure the Gherkin transpiler's coverage over a REAL Vanessa feature corpus.

Offline, no lab boot: globs project `.feature` files, runs the qa-mcp transpiler over each, and reports
per-file + aggregate coverage (mapped vs unmapped steps) plus a frequency-ranked list of the UNMAPPED step
phrasings — the concrete vocabulary gap to close. This doubles as the change-5 "corpus transpile gate".

Usage:
    python tools/protocol-research/corpus_transpile_coverage.py [GLOB ...] [--min FRACTION]

Defaults to the lab Vanessa corpora under /opt/1c-dev + the in-repo qa-vanessa-style sample.
With --min, exits non-zero when coverage is below FRACTION (e.g. --min 0.95) — usable as a CI gate alongside
the in-repo gate in tests/test_corpus_gate.py.
"""
from __future__ import annotations

import glob
import re
import sys
from collections import Counter
from pathlib import Path

from qa_mcp.scenario.gherkin import transpile_feature

LAB_ROOT = Path("/opt/1c-dev")
PUBLIC_LAB_GLOB = "/opt/1c-dev/demo10413/tests/vanessa/**/*.feature"
IN_REPO_GLOB = "tools/protocol-research/qa-vanessa-style.feature"


def default_globs() -> list[str]:
    patterns = [IN_REPO_GLOB]
    if not LAB_ROOT.is_dir():
        return patterns
    public = glob.glob(PUBLIC_LAB_GLOB, recursive=True)
    if len(public) != 4:
        raise RuntimeError(f"public lab corpus count {len(public)} != 4")
    candidates = []
    for child in sorted(LAB_ROOT.iterdir()):
        pattern = str(child / "tests/vanessa/**/*.feature")
        if child.name != "demo10413" and len(glob.glob(pattern, recursive=True)) == 6:
            candidates.append(pattern)
    if len(candidates) != 1:
        raise RuntimeError(f"private lab corpus candidates {len(candidates)} != 1")
    return [PUBLIC_LAB_GLOB, candidates[0], IN_REPO_GLOB]

# Normalize an unmapped step to a phrasing key: lowercase, strip quoted literals to <…>, collapse spaces.
_QUOTED = re.compile(r"['\"][^'\"]*['\"]")
_SPACE = re.compile(r"\s+")


def norm(step: str) -> str:
    s = _QUOTED.sub("<…>", step.strip().lower())
    return _SPACE.sub(" ", s)


def display_path(path: str) -> str:
    lab_prefix = str(LAB_ROOT) + "/"
    if path.startswith(lab_prefix):
        relative = path[len(lab_prefix):]
        head, _, tail = relative.partition("/")
        label = head if head == "demo10413" else "<private-corpus>"
        return f"…/{label}/{tail}"
    return path.replace("tools/protocol-research/", "repo:")


def main(argv: list[str]) -> int:
    args = argv[1:]
    min_cov: float | None = None
    if "--min" in args:
        i = args.index("--min")
        min_cov = float(args[i + 1])
        args = args[:i] + args[i + 2:]
    try:
        patterns = args or default_globs()
    except RuntimeError as exc:
        print(f"corpus discovery failed: {exc}")
        return 1
    files: list[str] = []
    for pat in patterns:
        matched = sorted(glob.glob(pat, recursive=True))
        if not matched:
            print("configured corpus matched no files:", pat)
            return 1
        files.extend(matched)
    if not files:
        print("no .feature files matched:", patterns)
        return 1

    total_mapped = total_unmapped = 0
    unmapped_counter: Counter[str] = Counter()
    unmapped_examples: dict[str, str] = {}

    print(f"{'file':<70} {'scen':>4} {'mapped':>7} {'unmap':>6} {'cov%':>5}")
    print("-" * 96)
    for path in files:
        try:
            text = open(path, encoding="utf-8-sig").read()
        except Exception as exc:  # noqa: BLE001
            print(f"{path}: READ ERROR {exc}")
            continue
        results = transpile_feature(text)
        f_mapped = sum(len(r.scenario.steps) for r in results)
        f_unmapped = sum(len(r.unmapped) for r in results)
        for r in results:
            for u in r.unmapped:
                key = norm(u)
                unmapped_counter[key] += 1
                unmapped_examples.setdefault(key, u.strip())
        total_mapped += f_mapped
        total_unmapped += f_unmapped
        denom = f_mapped + f_unmapped or 1
        cov = 100 * f_mapped / denom
        short = display_path(path)
        print(f"{short:<70} {len(results):>4} {f_mapped:>7} {f_unmapped:>6} {cov:>4.0f}")

    denom = total_mapped + total_unmapped or 1
    print("-" * 96)
    print(f"{'TOTAL':<70} {'':>4} {total_mapped:>7} {total_unmapped:>6} {100*total_mapped/denom:>4.0f}")
    print(f"\nfiles={len(files)}  steps={denom}  mapped={total_mapped}  unmapped={total_unmapped}  "
          f"coverage={100*total_mapped/denom:.1f}%")

    print(f"\n=== UNMAPPED step phrasings (normalized, freq-ranked) — {len(unmapped_counter)} distinct ===")
    for key, n in unmapped_counter.most_common():
        print(f"{n:>4}  {key}")
        print(f"      e.g.  {unmapped_examples[key]}")

    if min_cov is not None:
        coverage = total_mapped / denom
        if coverage < min_cov:
            print(f"\nFAIL: coverage {coverage:.1%} < required {min_cov:.0%}")
            return 2
        print(f"\nOK: coverage {coverage:.1%} >= required {min_cov:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
