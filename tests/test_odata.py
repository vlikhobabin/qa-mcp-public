"""Card 105 (E-XV) — read-only OData client + data-layer assertion (offline, injected fetcher)."""
from __future__ import annotations

import base64
import urllib.parse

import pytest

from qa_mcp.data import ODataClient, assert_data_value, match_value


class _FakeFetcher:
    """Records the last URL/headers and returns a canned payload."""
    def __init__(self, payload):
        self.payload = payload
        self.url = None
        self.headers = None

    def __call__(self, url, headers):
        self.url = url
        self.headers = headers
        return self.payload


def test_build_url_filter_select_and_auth() -> None:
    fake = _FakeFetcher({"value": [{"Code": "000000001", "Description": "Обувь"}]})
    client = ODataClient("http://127.0.0.1:8316/vc/odata/standard.odata", "Администратор", "",
                         fetcher=fake)
    rows = client.query("Catalog_Товары", filter="Description eq 'Обувь'", select=["Code", "Description"])
    assert rows == [{"Code": "000000001", "Description": "Обувь"}]
    # the Cyrillic entity-set name is percent-encoded into the path (see test_url_is_ascii_safe)
    assert "/" + urllib.parse.quote("Catalog_Товары") + "?" in fake.url
    assert "Description" in fake.url                     # the $filter value is carried
    assert "24select=Code" in fake.url                   # $select=Code,Description (url-encoded)
    assert "24format=json" in fake.url                   # $format=json
    # basic auth header for «Администратор:» (empty password)
    assert fake.headers["Authorization"] == "Basic " + base64.b64encode("Администратор:".encode()).decode()


def test_url_is_ascii_safe_for_cyrillic_entity_set() -> None:
    # Live regression (2026-06-21): an unencoded Cyrillic path raised UnicodeEncodeError in urllib before
    # the request was even sent. The built URL must be pure ASCII (percent-encoded), so .encode('ascii') is safe.
    url = ODataClient("http://127.0.0.1:8316/vc/odata/standard.odata").build_url(
        "Catalog_Банки", filter="Code eq '000000005'")
    url.encode("ascii")  # must not raise
    assert "Catalog_Банки" not in url                    # raw Cyrillic must be gone
    assert urllib.parse.quote("Catalog_Банки") in url    # percent-encoded form present


def test_filter_spaces_encode_as_percent20_not_plus() -> None:
    # Live regression (2026-06-21): 1C OData's $filter parser treats '+' literally, not as a space, so a
    # quote_plus-encoded space yields HTTP 500 «Operation not allowed in clause "ГДЕ"». Spaces must be %20.
    url = ODataClient("http://h/odata").build_url("Catalog_X", filter="Code eq '5'")
    query = url.split("?", 1)[1]
    assert "+" not in query                              # no quote_plus spaces anywhere in the query
    assert "Code%20eq%20" in url                         # the $filter spaces are %20


def test_query_by_key_wraps_single_entity() -> None:
    fake = _FakeFetcher({"Ref_Key": "abc", "Description": "Обувь"})  # single entity (no "value")
    client = ODataClient("http://h/odata", fetcher=fake)
    rows = client.query("Catalog_Товары", key="9f8e7d6c-1111-2222-3333-444455556666")
    assert rows == [{"Ref_Key": "abc", "Description": "Обувь"}]
    assert "(guid'9f8e7d6c-1111-2222-3333-444455556666')" in fake.url


def test_unconfigured_base_url_raises() -> None:
    with pytest.raises(ValueError):
        ODataClient("", fetcher=_FakeFetcher({})).query("Catalog_X", filter="true")


def test_match_value_modes() -> None:
    assert match_value("Обувь", "Обувь", "equals")
    assert not match_value("Обувь", "Обув", "equals")
    assert match_value("Обувь склад", "склад", "contains")
    assert match_value("000000001", r"^0+1$", "regex")
    assert match_value("120,50", "120.5", "numeric")
    assert match_value("120.500", "120,5", "numeric")
    assert match_value(None, "", "equals")  # None -> "" equals empty
    with pytest.raises(ValueError, match="unknown match mode"):
        match_value("same", "same", "__bogus__")


def test_assert_data_value_match_mismatch_and_missing() -> None:
    hit = _FakeFetcher({"value": [{"Code": "000000001"}]})
    client = ODataClient("http://h/odata", fetcher=hit)
    ok = assert_data_value(client, "Catalog_Товары", "Code", "000000001",
                           filter="Description eq 'Обувь'")
    assert ok["ok"] is True and ok["actual"] == "000000001" and ok["record_count"] == 1

    bad = assert_data_value(client, "Catalog_Товары", "Code", "999")
    assert bad["ok"] is False and bad["actual"] == "000000001"

    miss = assert_data_value(ODataClient("http://h/odata", fetcher=_FakeFetcher({"value": []})),
                             "Catalog_Товары", "Code", "x", filter="false")
    assert miss["ok"] is False and miss["actual"] is None and miss["reason"] == "no matching record"
