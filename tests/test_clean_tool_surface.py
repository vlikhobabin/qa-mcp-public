"""Gate: the runtime-exposed MCP tool descriptions must be product-facing.

FastMCP returns each tool's function docstring as the `description` field of `tools/list`, which every
connecting agent sees with no reverse-engineering. This test pins the contract that no shipped tool
description leaks an internal research reference (a `card <n>` trace, a `vanessa`/`vanessa-mcp` mention, or
an `evidence/` path). It scans the live registered tool surface, so it also catches any future tool that
reintroduces such a token.
"""

from __future__ import annotations

import asyncio
import re

from qa_mcp.mcp_server import mcp

# Internal R&D tokens that must not appear in any runtime-exposed tool description.
_RND_TOKEN = re.compile(r"card\s+\d|vanessa|evidence", re.IGNORECASE)


def _tool_descriptions() -> list[tuple[str, str]]:
    """(name, description) for every registered tool, straight from the FastMCP tool manager."""
    return [(t.name, t.description or "") for t in asyncio.run(mcp.list_tools())]


def test_every_tool_is_registered_with_a_description() -> None:
    tools = _tool_descriptions()
    # Sanity: the full tool surface is present and each tool actually carries a description.
    assert len(tools) >= 60, f"expected the full tool surface, got {len(tools)} tools"
    missing = [name for name, desc in tools if not desc.strip()]
    assert not missing, f"tools with an empty description: {missing}"


def test_tool_descriptions_carry_no_internal_rnd_references() -> None:
    violations: dict[str, list[str]] = {}
    for name, desc in _tool_descriptions():
        hits = _RND_TOKEN.findall(desc)
        if hits:
            violations[name] = hits
    assert not violations, (
        "tool descriptions still leak internal R&D references "
        f"({sum(len(v) for v in violations.values())} hits across {len(violations)} tools):\n"
        + "\n".join(f"  {name}: {hits}" for name, hits in sorted(violations.items()))
    )
