from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "public_readiness.py"
POLICY = ROOT / "config" / "publication-policy.json"
PROVENANCE = ROOT / "docs" / "public" / "asset-provenance.json"
HANDSHAKE_TRAFFIC = (
    ROOT
    / "docs"
    / "protocol-research"
    / "evidence"
    / "card115-8-5-handshake-decode-2026-06-25"
    / "8-5-handshake-traffic.jsonl"
)

SPEC = importlib.util.spec_from_file_location("public_readiness", TOOL)
assert SPEC and SPEC.loader
PUBLIC_READINESS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PUBLIC_READINESS)


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def scan_fixture(
    tmp_path: Path,
    files: dict[str, bytes],
    policy: dict | None = None,
) -> list[dict]:
    paths = []
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        paths.append(Path(name))
    return PUBLIC_READINESS.scan_tree(
        tmp_path,
        paths,
        policy=policy or {"scanner_fixture_allowlist": {}},
    )


def categories(findings: list[dict]) -> set[str]:
    return {finding["category"] for finding in findings}


def test_scanner_rejects_lowercase_credentials_and_test_tree_disclosures(
    tmp_path: Path,
) -> None:
    lowercase_credential = b"pass" + b"word=" + b"unsafe-lowercase-value"
    test_credential = b"PASS" + b"WORD=" + b"unsafe-test-tree-value"
    private_endpoint = b"192.168." + b"44.91"
    findings = scan_fixture(
        tmp_path,
        {
            "lowercase.env": lowercase_credential,
            "tests/leaked.env": test_credential,
            "tests/leaked.txt": private_endpoint,
        },
    )
    observed = {(item["category"], item["path"]) for item in findings}
    assert ("password_assignment", "lowercase.env") in observed
    assert ("password_assignment", "tests/leaked.env") in observed
    assert ("private_lab_endpoint", "tests/leaked.txt") in observed


def test_scanner_rejects_prefixed_mixed_case_credentials(tmp_path: Path) -> None:
    findings = scan_fixture(
        tmp_path,
        {
            "lower.env": b"qa_mcp_odata_pass" + b"word=unsafe-prefixed-value",
            "upper.env": b"TEST_CLIENT_PASS" + b"WORD=unsafe-uppercase-value",
            "mixed.env": b"Bridge_Pass" + b"Wd=unsafe-mixed-value",
        },
    )
    assert {
        item["path"] for item in findings
        if item["category"] == "password_assignment"
    } == {"lower.env", "upper.env", "mixed.env"}


def test_scanner_rejects_prefixed_structured_credentials(tmp_path: Path) -> None:
    findings = scan_fixture(
        tmp_path,
        {
            "credential.json": (
                b'{"QA_MCP_PASS' + b'WORD":"unsafe-json-value"}'
            ),
            "credential.yaml": (
                b"qa_mcp_pass" + b"word: unsafe-yaml-value\n"
            ),
        },
    )
    assert {
        item["path"] for item in findings
        if item["category"] == "password_assignment"
    } == {"credential.json", "credential.yaml"}


def test_scanner_rejects_camel_case_prefixed_credentials(tmp_path: Path) -> None:
    findings = scan_fixture(
        tmp_path,
        {
            "credential.json": (
                b'{"databasePass' + b'word":"unsafe-json-value"}'
            ),
            "credential.yaml": (
                b"servicePass" + b"wd: unsafe-yaml-value\n"
            ),
            "credential.env": (
                b"DatabaseP" + b"wd=unsafe-environment-value\n"
            ),
        },
    )
    assert {
        item["path"] for item in findings
        if item["category"] == "password_assignment"
    } == {"credential.json", "credential.yaml", "credential.env"}


def test_scanner_rejects_short_nonempty_password_assignments(
    tmp_path: Path,
) -> None:
    findings = scan_fixture(
        tmp_path,
        {
            "password.json": (
                b'{"databasePass' + b'word":"x"}'
            ),
            "passwd.json": (
                b'{"QA_MCP_PASS' + b'WD":"xy"}'
            ),
            "pwd.json": b'{"p' + b'Wd":"xyz"}',
            "password.yaml": b"servicePass" + b"word: a\n",
            "passwd.yaml": b"qa_mcp_pass" + b"wd: bb\n",
            "pwd.yaml": b"P" + b"WD: ccc\n",
            "password.env": b"QA_PASS" + b"WORD=1\n",
            "passwd.env": b"bridgePass" + b"wd=22\n",
            "pwd.env": b"p" + b"Wd=333\n",
        },
    )

    assert {
        item["path"] for item in findings
        if item["category"] == "password_assignment"
    } == {
        "password.json", "passwd.json", "pwd.json",
        "password.yaml", "passwd.yaml", "pwd.yaml",
        "password.env", "passwd.env", "pwd.env",
    }
    assert all(
        set(item) == {"category", "path", "source", "match_count"}
        for item in findings
    )


def test_scanner_allowlists_only_exact_public_fixture_values(tmp_path: Path) -> None:
    docker_subnet = b"192.168." + b"65.0"
    public_password_fixture = b'"pass' + b'word":         "supersecret'
    policy = {
        "scanner_fixture_allowlist": {
            "private_lab_endpoint": {
                "host-agent/install-windows-host-agent.ps1": {
                    "raw": {
                        base64.b64encode(docker_subnet).decode("ascii"): 3,
                    },
                },
            },
            "password_assignment": {
                "host-agent/windows-display-agent/main_test.go": {
                    "raw": {
                        base64.b64encode(public_password_fixture).decode("ascii"): 1,
                    },
                },
            },
        },
    }
    endpoint_policy = {
        "scanner_fixture_allowlist": {
            "private_lab_endpoint": policy["scanner_fixture_allowlist"][
                "private_lab_endpoint"
            ],
        },
    }
    findings = scan_fixture(
        tmp_path,
        {
            "host-agent/install-windows-host-agent.ps1": (
                b" ".join([docker_subnet] * 3)
            ),
            "host-agent/windows-display-agent/main_test.go": (
                public_password_fixture
            ),
        },
        policy,
    )
    assert findings == []

    added_private_endpoint = b"10.23." + b"91.7"
    added_credential = b"pass" + b"word=" + b"new-unallowlisted-secret"
    findings = scan_fixture(
        tmp_path,
        {
            "host-agent/install-windows-host-agent.ps1": (
                b" ".join([docker_subnet] * 3)
                + b" "
                + added_private_endpoint
            ),
            "host-agent/windows-display-agent/main_test.go": (
                public_password_fixture + b"\n" + added_credential
            ),
        },
        policy,
    )
    assert {
        (item["category"], item["path"])
        for item in findings
    } == {
        ("private_lab_endpoint", "host-agent/install-windows-host-agent.ps1"),
        ("password_assignment", "host-agent/windows-display-agent/main_test.go"),
    }

    repeated_fixture = scan_fixture(
        tmp_path,
        {
            "host-agent/install-windows-host-agent.ps1": (
                b" ".join([docker_subnet] * 4)
            ),
        },
        endpoint_policy,
    )
    assert repeated_fixture == [{
        "category": "private_lab_endpoint",
        "path": "host-agent/install-windows-host-agent.ps1",
        "source": "raw",
        "match_count": 1,
    }]

    missing_fixture = scan_fixture(
        tmp_path,
        {
            "host-agent/install-windows-host-agent.ps1": (
                b" ".join([docker_subnet] * 2)
            ),
        },
        endpoint_policy,
    )
    assert missing_fixture == [{
        "category": "private_lab_endpoint",
        "path": "host-agent/install-windows-host-agent.ps1",
        "source": "raw",
        "match_count": 1,
    }]


def test_scanner_reconciles_missing_allowlisted_path_globally(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    allowed_path = "fixture/allowlisted.txt"
    allowed_value = b"192.168." + b"65.0"
    monkeypatch.setattr(
        PUBLIC_READINESS,
        "load_policy",
        lambda: {
            "scanner_fixture_allowlist": {
                "private_lab_endpoint": {
                    allowed_path: {
                        "raw": {
                            base64.b64encode(allowed_value).decode("ascii"): 1,
                        },
                    },
                },
            },
        },
    )

    findings = PUBLIC_READINESS.scan_tree(tmp_path, [Path(allowed_path)])

    assert findings == [{
        "category": "private_lab_endpoint",
        "path": allowed_path,
        "source": "raw",
        "match_count": 1,
    }]


def test_scanner_reconciles_raw_allowance_after_symlink_substitution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    allowed_path = "fixture/allowlisted.txt"
    allowed_value = b"192.168." + b"65.0"
    monkeypatch.setattr(
        PUBLIC_READINESS,
        "load_policy",
        lambda: {
            "scanner_fixture_allowlist": {
                "private_lab_endpoint": {
                    allowed_path: {
                        "raw": {
                            base64.b64encode(allowed_value).decode("ascii"): 1,
                        },
                    },
                },
            },
        },
    )
    link = tmp_path / allowed_path
    link.parent.mkdir(parents=True)
    link.symlink_to("benign-public-target")

    findings = PUBLIC_READINESS.scan_tree(tmp_path, [Path(allowed_path)])

    assert findings == [{
        "category": "private_lab_endpoint",
        "path": allowed_path,
        "source": "raw",
        "match_count": 1,
    }]


def test_scanner_fails_closed_on_structured_payload_errors(tmp_path: Path) -> None:
    token = ("gh" + "p_" + "C" * 24).encode()
    valid = json.dumps({"PAYLOAD_B64": base64.b64encode(token).decode()}).encode()
    findings = scan_fixture(
        tmp_path,
        {
            "mixed.jsonl": b"{malformed}\n" + valid,
            "invalid.json": b'{"payload_b64":"not valid base64"}',
        },
    )
    assert categories(findings) >= {
        "service_token",
        "structured_payload_parse_error",
        "structured_payload_decode_error",
    }
    assert all(set(item) == {"category", "path", "source", "match_count"}
               for item in findings)


def test_scanner_rejects_wrong_typed_declared_base64(tmp_path: Path) -> None:
    findings = scan_fixture(
        tmp_path,
        {
            "wrong-type.jsonl": (
                b'{"payload_b64":123}\n'
                b'{"nested":{"value_b64":{"not":"a string"}}}\n'
            ),
        },
    )
    assert findings == [{
        "category": "structured_payload_type_error",
        "path": "wrong-type.jsonl",
        "source": "raw",
        "match_count": 2,
    }]


def test_scanner_rejects_inline_payload_integrity_mismatch(tmp_path: Path) -> None:
    payload = b"current-public-payload"
    row = {
        "payload_b64": base64.b64encode(payload).decode("ascii"),
        "byte_count": len(payload) + 1,
        "sha256": hashlib.sha256(b"stale-private-payload").hexdigest(),
    }
    findings = scan_fixture(
        tmp_path,
        {"traffic.jsonl": (json.dumps(row) + "\n").encode()},
    )
    assert {
        (item["category"], item["path"], item["source"], item["match_count"])
        for item in findings
    } == {
        ("structured_payload_byte_count_error", "traffic.jsonl", "raw", 1),
        ("structured_payload_sha256_error", "traffic.jsonl", "raw", 1),
    }


def test_curated_handshake_inline_payload_declarations_are_current() -> None:
    rows = [
        json.loads(line)
        for line in HANDSHAKE_TRAFFIC.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 29
    for row in rows:
        payload = base64.b64decode(row["payload_b64"], validate=True)
        assert row["byte_count"] == len(payload)
        assert row["sha256"] == hashlib.sha256(payload).hexdigest()


def test_scanner_checks_symlink_targets_and_exact_email_values(tmp_path: Path) -> None:
    link = tmp_path / "public-link"
    link.symlink_to("/home/" + "li" + "hv/private")
    findings = PUBLIC_READINESS.scan_tree(
        tmp_path,
        [Path("public-link")],
        policy={"scanner_fixture_allowlist": {}},
    )
    assert findings == [{
        "category": "named_lab_account",
        "path": "public-link",
        "source": "symlink_target",
        "match_count": 1,
    }]

    email = b"another@" + b"docs.example.com"
    findings = scan_fixture(tmp_path, {"tests/unlisted-email.txt": email})
    assert findings == [{
        "category": "personal_email",
        "path": "tests/unlisted-email.txt",
        "source": "raw",
        "match_count": 1,
    }]


def test_provenance_fails_closed_on_scan_or_i2_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args = type("Args", (), {"write": False})()
    i2_called = False

    monkeypatch.setattr(PUBLIC_READINESS, "policy_findings", lambda *_: [])
    monkeypatch.setattr(PUBLIC_READINESS, "scan_tree", lambda *_: [{
        "category": "service_token", "path": "leak.txt",
        "source": "raw", "match_count": 1,
    }])

    def record_i2(_: Path) -> dict:
        nonlocal i2_called
        i2_called = True
        return {}

    monkeypatch.setattr(PUBLIC_READINESS, "run_i2", record_i2)
    assert PUBLIC_READINESS.provenance(args) == {
        "schema": "qa-mcp.provenance-check.v1",
        "ok": False,
        "entry_count": 0,
        "gate_findings": 1,
    }
    assert i2_called is False

    monkeypatch.setattr(PUBLIC_READINESS, "scan_tree", lambda *_: [])
    monkeypatch.setattr(
        PUBLIC_READINESS,
        "run_i2",
        lambda *_: (_ for _ in ()).throw(RuntimeError("I2 gate failed")),
    )
    with pytest.raises(RuntimeError, match="I2 gate failed"):
        PUBLIC_READINESS.provenance(args)


def test_scanner_covers_all_file_types_and_high_confidence_secrets(tmp_path: Path) -> None:
    token = ("gh" + "p_" + "A" * 24).encode()
    private_key = b"-----BEGIN " + b"PRIVATE KEY-----\nfixture\n"
    findings = scan_fixture(tmp_path, {
        "payload.xml": b"<token>" + token + b"</token>",
        "identity.example": private_key,
        "credentials.env": b"PASSWORD=" + b"not-a-real-but-unsafe-value\n",
    })
    assert {"service_token", "private_key", "password_assignment"} <= categories(findings)


def test_scanner_covers_named_machine_and_all_rfc1918_ranges(tmp_path: Path) -> None:
    machine = b"DESKTOP-" + b"PRIVATE01"
    findings = scan_fixture(tmp_path, {
        "host.txt": machine + b" 10.23.4.5 172.20.4.8 192.168.44.7",
    })
    assert categories(findings) >= {"named_lab_machine", "private_lab_endpoint"}
    endpoint = next(item for item in findings if item["category"] == "private_lab_endpoint")
    assert endpoint["match_count"] == 3


def test_scanner_decodes_structured_base64_payloads_without_leaking_values(tmp_path: Path) -> None:
    token = ("gh" + "p_" + "B" * 24).encode()
    customer_and_machine = (
        "БИТ" + "." + "ФИНАНС " + "DESKTOP-" + "PRIVATE02"
    ).encode("utf-16le")
    rows = [
        {"payload_b64": base64.b64encode(token).decode("ascii")},
        {"payload_b64": base64.b64encode(customer_and_machine).decode("ascii")},
    ]
    content = "\n".join(json.dumps(row) for row in rows).encode()
    findings = scan_fixture(tmp_path, {"traffic.jsonl": content})
    assert {"service_token", "customer_identity", "named_lab_machine"} <= categories(findings)
    serialized = json.dumps(findings, ensure_ascii=False)
    assert token.decode() not in serialized
    assert "PRIVATE02" not in serialized


def test_scanner_checks_paths_and_rejects_unsupported_binary(tmp_path: Path) -> None:
    findings = scan_fixture(tmp_path, {
        "private/" + "DESKTOP-" + "PRIVATE03.xml": b"safe",
        "artifact.epf": b"opaque",
    })
    assert {"named_lab_machine", "unsupported_binary"} <= categories(findings)


def test_exact_apache2_policy_and_legal_files() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert policy["license_spdx"] == "Apache-2.0"
    assert metadata["project"]["license"] == "Apache-2.0"
    assert "Apache License\n                           Version 2.0" in (
        ROOT / "LICENSE"
    ).read_text(encoding="utf-8")
    assert "not affiliated" in (ROOT / "NOTICE").read_text(encoding="utf-8")
    assert policy["history"]["mode"] == "audited-source-snapshot"
    assert policy["history"]["include_ancestors"] is False


def test_public_audit_and_selected_history_are_safe() -> None:
    completed = run_tool("audit", "--history", "--json")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["current_tree_findings"] == []
    assert result["history"]["mode"] == "audited-source-snapshot"
    assert result["history"]["included_ancestor_count"] == 0
    assert result["i2"]["fail_closed_count"] == 23


def test_provenance_manifest_is_exhaustive_and_current() -> None:
    completed = run_tool("provenance", "--check", "--json")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    manifest = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["entry_count"] == len(manifest["entries"])
    assert result["entry_count"] >= 640
    assert len({entry["path"] for entry in manifest["entries"]}) == result["entry_count"]
    assert {entry["decision"] for entry in manifest["entries"]} == {"redistribute"}
    assert {entry["license_spdx"] for entry in manifest["entries"]} == {"Apache-2.0"}
    assert not any(entry["path"].lower().endswith(".cfe") for entry in manifest["entries"])


def test_standard_public_documents_and_active_links() -> None:
    required = {
        "README.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "GOVERNANCE.md",
        "SUPPORT.md",
        "CODE_OF_CONDUCT.md",
        "docs/publication-policy.md",
    }
    assert not [path for path in required if not (ROOT / path).is_file()]
    completed = run_tool("docs", "--json")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(completed.stdout) == {
        "broken_links": [],
        "checked_documents": 12,
        "ok": True,
        "schema": "qa-mcp.public-docs-audit.v1",
    }


def test_isolated_snapshot_build_is_public_and_clean() -> None:
    completed = run_tool("snapshot", "--json")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["build"]["wheel_count"] == 1
    assert result["build"]["sdist_count"] == 1
    assert result["excluded"]["git_metadata"] is True
    assert result["excluded"]["ignored_runtime"] is True
    # The three local workflow discovery links remain after native migration of
    # the workflow skills. Snapshot excludes every link; executable sources and
    # skills are ordinary repository files, checked separately below.
    assert result["excluded"]["symlink_count"] == 3
    assert result["excluded"]["external_symlink_count"] == 2
    assert result["install"] == {"import_smoke": True, "locked_sync": True}
    assert result["tests"] == {
        "audit": True,
        "docs": True,
        "focused_public_readiness": True,
        "i2_mutations": 23,
        "provenance": True,
    }
    assert result["license_spdx"] == "Apache-2.0"


def test_snapshot_preserves_local_workflow_and_frozen_history(tmp_path: Path) -> None:
    destination = tmp_path / "source"
    destination.mkdir()
    PUBLIC_READINESS.copy_snapshot(destination)
    for relative in (
        "bin/chrl", "bin/chrl-dist", "bin/chrl-run", "bin/openspec",
        "scripts/changerail/local_delivery.py", "scripts/changerail/native_workflow.py",
        "tools/changerail/skills/chrl-native-deliver/SKILL.md",
        "tools/changerail/skills/chrl-review/SKILL.md",
    ):
        source, exported = ROOT / relative, destination / relative
        assert exported.is_file() and not exported.is_symlink(), relative
        assert exported.read_bytes() == source.read_bytes(), relative
    manifest = json.loads(
        (destination / ".changerail/history.json").read_text()
    )
    for relative, expected in manifest["files"].items():
        exported = destination / relative
        assert exported.is_file(), relative
        assert hashlib.sha256(exported.read_bytes()).hexdigest() == expected, relative
    assert not (destination / ".runtime").exists()
    assert not any(path.is_symlink() for path in destination.rglob("*"))
