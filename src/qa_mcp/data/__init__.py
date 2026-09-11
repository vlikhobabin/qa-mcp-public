"""Card 105 (E-XV) — data-layer access for cross-verifying UI actions against the database.

qa-mcp drives the UI over the native TestClient protocol AND can assert the RESULT against the data layer
(standard 1C OData) in the SAME scenario — a capability Vanessa Automation (UI-only) does not have. Read-only.
"""
from __future__ import annotations

from .odata import (
    ODataClient,
    assert_data_count_value,
    assert_data_value,
    match_value,
    role_data_matrix,
)

__all__ = ["ODataClient", "assert_data_value", "assert_data_count_value", "match_value", "role_data_matrix"]
