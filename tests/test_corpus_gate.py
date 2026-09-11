"""Card 103 Wave 4 — the transpile coverage GATE.

Two gates:
1. HERMETIC (always runs) — the in-repo canonical corpus must transpile with ZERO unmapped lines and the
   expected scenario count (Scenario Outline expanded). This pins the Wave 1+2 step vocabulary + BDD mechanics
   as an executable spec, independent of the lab.
2. LAB (skips if /opt/1c-dev is absent) — the four public demo contracts plus one private six-file corpus must
   each be present and transpile at >= LAB_MIN coverage. The private directory name is never published: the lab
   discovers the structurally pinned six-file corpus, and fails loudly on a missing or ambiguous group.

Card 109 closed the last residual — «я открываю внешнюю обработку или отчет … (Расширение)» now transpiles
(executed by the open_external_processor tool), so both the hermetic and lab corpora are at 100% (LAB_MIN = 1.0).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from qa_mcp.scenario import transpile_feature

REPO = Path(__file__).resolve().parents[1]
CANONICAL = REPO / "tools/protocol-research/qa-vanessa-canonical-corpus.feature"

LAB_ROOT = Path("/opt/1c-dev")
PUBLIC_CORPUS = Path("demo10413/tests/vanessa")
EXPECTED_COUNTS = (4, 6)
LAB_MIN = 1.0  # real corpus now fully mapped (card 109 closed the external-epf residual)


def test_canonical_corpus_transpiles_fully() -> None:
    """The in-repo canonical corpus is the hermetic gate: 0 unmapped, every scenario has steps."""
    results = transpile_feature(CANONICAL.read_text(encoding="utf-8"))
    # 6 plain scenarios (incl. the card-109 external-epf) + 3 expanded Outline rows + 1 nested = 10
    assert len(results) == 10, [r.scenario.name for r in results]
    for r in results:
        assert r.unmapped == [], f"{r.scenario.name}: unmapped {r.unmapped}"
        assert r.scenario.steps, f"{r.scenario.name}: no steps"
    # Outline expanded with substitution
    outline_names = [r.scenario.name for r in results if r.scenario.name.startswith("договор виден")]
    assert outline_names == [
        "договор виден в форме Заказ",
        "договор виден в форме ПриходТовара",
        "договор виден в форме Оплата",
    ]


def _features(root: Path) -> list[Path]:
    return sorted(root.rglob("*.feature")) if root.is_dir() else []


def _lab_file_groups(lab_root: Path = LAB_ROOT) -> list[list[Path]]:
    if not lab_root.is_dir():
        return []
    public = _features(lab_root / PUBLIC_CORPUS)
    if len(public) != EXPECTED_COUNTS[0]:
        raise RuntimeError(f"public lab corpus count {len(public)} != {EXPECTED_COUNTS[0]}")
    candidates = [
        files for child in sorted(lab_root.iterdir())
        if child.name != PUBLIC_CORPUS.parts[0]
        and len(files := _features(child / "tests/vanessa")) == EXPECTED_COUNTS[1]
    ]
    if len(candidates) != 1:
        raise RuntimeError(f"private lab corpus candidates {len(candidates)} != 1")
    return [public, candidates[0]]


def test_lab_corpus_discovery_fails_loud_on_partial_union(tmp_path: Path) -> None:
    public = tmp_path / PUBLIC_CORPUS
    public.mkdir(parents=True)
    for index in range(EXPECTED_COUNTS[0]):
        (public / f"public-{index}.feature").write_text("# fixture", encoding="utf-8")
    with pytest.raises(RuntimeError, match="private lab corpus candidates 0"):
        _lab_file_groups(tmp_path)


def test_lab_corpus_discovery_preserves_four_plus_six_contract(tmp_path: Path) -> None:
    for relative, count in ((PUBLIC_CORPUS, 4), (Path("private-corpus/tests/vanessa"), 6)):
        directory = tmp_path / relative
        directory.mkdir(parents=True)
        for index in range(count):
            (directory / f"case-{index}.feature").write_text("# fixture", encoding="utf-8")
    assert [len(group) for group in _lab_file_groups(tmp_path)] == [4, 6]


def test_lab_corpus_coverage_above_threshold() -> None:
    """Regression gate on the real lab corpus (skips when the lab tree is not present)."""
    groups = _lab_file_groups()
    if not groups:
        pytest.skip("lab corpus (/opt/1c-dev) not present on this machine")
    files = [path for group in groups for path in group]
    mapped = unmapped = 0
    for path in files:
        for r in transpile_feature(Path(path).read_text(encoding="utf-8-sig")):
            mapped += len(r.scenario.steps)
            unmapped += len(r.unmapped)
    total = mapped + unmapped or 1
    coverage = mapped / total
    assert coverage >= LAB_MIN, f"lab corpus coverage {coverage:.1%} < {LAB_MIN:.0%} (mapped={mapped}, unmapped={unmapped})"
