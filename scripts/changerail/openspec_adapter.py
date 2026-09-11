"""Pinned project-local OpenSpec 1.3.1 command boundary.

The adapter invokes only the dependency installed below ``tools/openspec``.
It never searches PATH for OpenSpec, invokes npx, installs a package, or falls
back to a user-global schema/configuration directory.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.changerail.contracts import DeliveryError


@dataclass(frozen=True)
class Task:
    """One task returned by the stock OpenSpec apply instructions."""

    id: str
    description: str
    done: bool


@dataclass(frozen=True)
class ApplyContext:
    """Normalized stock apply state."""

    state: str
    tasks: tuple[Task, ...]
    context_files: tuple[Path, ...]
    instruction: str

    @property
    def tasks_complete(self) -> bool:
        return (
            bool(self.tasks)
            and self.state == "all_done"
            and all(task.done for task in self.tasks)
        )


class OpenSpecAdapter:
    """Read and validate stock OpenSpec artifacts through the pinned CLI."""

    VERSION = "1.3.1"
    CHANGE_ID = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")

    def __init__(self, root: Path, *, timeout: float = 40.0) -> None:
        self.root = root.resolve(strict=True)
        dependency = self.root / "tools/openspec"
        self.package = (dependency / "node_modules/@fission-ai/openspec").resolve()
        node = shutil.which("node")
        if node is None:
            raise DeliveryError("Node.js executable missing from PATH")
        self.node = Path(node).resolve(strict=True)
        self.cli = self.package / "bin/openspec.js"
        self.timeout = timeout
        manifest = self.package / "package.json"
        if not self.package.is_relative_to(dependency.resolve()):
            raise DeliveryError("OpenSpec package must remain project-local")
        if not self.node.is_file() or not manifest.is_file() or not self.cli.is_file():
            raise DeliveryError(
                "local OpenSpec dependency missing; run "
                "./tools/openspec/bootstrap.sh --offline"
            )
        try:
            metadata = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise DeliveryError("invalid local OpenSpec manifest") from exc
        if (
            metadata.get("name") != "@fission-ai/openspec"
            or metadata.get("version") != self.VERSION
        ):
            raise DeliveryError("only project-local OpenSpec 1.3.1 is supported")
        version = self._invoke("--version")
        if version.returncode or version.stdout.strip() != self.VERSION:
            raise DeliveryError("installed OpenSpec CLI does not match version 1.3.1")

    def _change_id(self, change_id: str) -> str:
        if not self.CHANGE_ID.fullmatch(change_id) or change_id == "archive":
            raise DeliveryError(f"invalid OpenSpec change ID: {change_id}")
        return change_id

    def change_root(self, change_id: str) -> Path:
        root = self.root / "openspec/changes" / self._change_id(change_id)
        if (
            root.is_symlink()
            or not root.is_dir()
            or not root.resolve().is_relative_to(self.root / "openspec/changes")
        ):
            raise DeliveryError(f"active OpenSpec change is absent: {change_id}")
        return root.resolve()

    def _invoke(self, *args: str) -> subprocess.CompletedProcess[str]:
        if (self.root / "openspec/schemas").exists():
            raise DeliveryError("project OpenSpec schema overrides are unsupported")
        with tempfile.TemporaryDirectory(prefix="chrl-openspec-") as isolated:
            env = {
                "PATH": "/usr/bin:/bin",
                "LANG": "C.UTF-8",
                "TZ": "UTC",
                "XDG_DATA_HOME": isolated,
                "XDG_CONFIG_HOME": isolated,
                "OPENSPEC_TELEMETRY": "0",
                "DO_NOT_TRACK": "1",
                "CI": "true",
                "OPENSPEC_NO_UPDATE_CHECK": "1",
                "OPENSPEC_NO_COMPLETIONS": "1",
                "OPENSPEC_NO_AUTO_CONFIG": "1",
                "NO_UPDATE_NOTIFIER": "1",
                "npm_config_update_notifier": "false",
            }
            try:
                return subprocess.run(
                    [str(self.node), str(self.cli), *args],
                    cwd=self.root,
                    env=env,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=self.timeout,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise DeliveryError(f"local OpenSpec command failed: {args}") from exc

    def _json(self, *args: str) -> dict[str, Any]:
        result = self._invoke(*args, "--json")
        if result.returncode:
            raise DeliveryError(
                f"OpenSpec exited {result.returncode}: {result.stderr.strip()}"
            )
        try:
            value = json.loads(result.stdout)
        except ValueError as exc:
            raise DeliveryError("OpenSpec returned invalid JSON") from exc
        if not isinstance(value, dict):
            raise DeliveryError("OpenSpec JSON result must be an object")
        return value

    def inspect_complete_plan(self, change_id: str) -> None:
        root = self.change_root(change_id)
        data = self._json("status", "--change", change_id, "--schema", "spec-driven")
        if (
            data.get("changeName") != change_id
            or data.get("schemaName") != "spec-driven"
        ):
            raise DeliveryError("OpenSpec status returned a foreign change")
        if data.get("isComplete") is not True:
            raise DeliveryError(
                "OpenSpec proposal/specs/design/tasks plan is incomplete"
            )
        required = (root / "proposal.md", root / "design.md", root / "tasks.md")
        if not all(path.is_file() for path in required) or not any(
            (root / "specs").glob("*/spec.md")
        ):
            raise DeliveryError("OpenSpec stock artifact set is incomplete")

    def apply_context(self, change_id: str) -> ApplyContext:
        root = self.change_root(change_id)
        data = self._json(
            "instructions", "apply", "--change", change_id, "--schema", "spec-driven"
        )
        if (
            data.get("changeName") != change_id
            or data.get("schemaName") != "spec-driven"
        ):
            raise DeliveryError("OpenSpec apply returned a foreign change")
        rows = data.get("tasks")
        if not isinstance(rows, list):
            raise DeliveryError("OpenSpec apply tasks are malformed")
        tasks: list[Task] = []
        for row in rows:
            if (
                not isinstance(row, dict)
                or not isinstance(row.get("id"), str)
                or not isinstance(row.get("description"), str)
                or type(row.get("done")) is not bool
            ):
                raise DeliveryError("OpenSpec apply task is malformed")
            tasks.append(Task(row["id"], row["description"], row["done"]))
        if not tasks or len({task.id for task in tasks}) != len(tasks):
            raise DeliveryError("OpenSpec requires nonempty uniquely identified tasks")
        state = data.get("state")
        if state not in {"ready", "all_done"}:
            raise DeliveryError(f"OpenSpec apply is not executable: {state}")
        files: list[Path] = []
        context_files = data.get("contextFiles")
        if not isinstance(context_files, dict):
            raise DeliveryError("OpenSpec contextFiles are malformed")
        for values in context_files.values():
            if not isinstance(values, list):
                raise DeliveryError("OpenSpec context file list is malformed")
            for value in values:
                path = Path(value)
                if (
                    not path.is_absolute()
                    or not path.is_file()
                    or not path.resolve().is_relative_to(root)
                ):
                    raise DeliveryError("OpenSpec context file escapes its change")
                files.append(path.resolve())
        instruction = data.get("instruction")
        if not isinstance(instruction, str) or not instruction.strip():
            raise DeliveryError("OpenSpec apply instruction is absent")
        return ApplyContext(state, tuple(tasks), tuple(files), instruction)

    def validate_change(self, change_id: str) -> None:
        self.change_root(change_id)
        result = self._invoke("validate", change_id, "--strict", "--no-interactive")
        if result.returncode:
            raise DeliveryError(
                "strict OpenSpec change validation failed: " + result.stderr.strip()
            )

    def validate_specs(self) -> None:
        result = self._invoke("validate", "--specs", "--strict", "--no-interactive")
        if result.returncode:
            raise DeliveryError(
                "strict canonical OpenSpec validation failed: " + result.stderr.strip()
            )

    def workflow(self, name: str) -> str:
        """Read stock methodology from the pinned package, not global skills."""
        if name not in {"apply", "sync", "verify"}:
            raise DeliveryError("unknown stock OpenSpec workflow")
        loader = self.root / "tools/openspec/workflow-instructions.mjs"
        result = subprocess.run(
            [str(self.node), str(loader), name],
            cwd=self.root,
            env={"PATH": "/usr/bin:/bin", "OPENSPEC_TELEMETRY": "0", "CI": "true"},
            text=True,
            capture_output=True,
            timeout=self.timeout,
            check=False,
        )
        if result.returncode or not result.stdout.strip():
            raise DeliveryError(
                "cannot read pinned stock workflow: " + result.stderr.strip()
            )
        return result.stdout

    def archive(self, change_id: str) -> Path:
        """Move already semantically synchronized artifacts using stock archive."""

        self.inspect_complete_plan(change_id)
        if not self.apply_context(change_id).tasks_complete:
            raise DeliveryError("OpenSpec archive requires all tasks complete")
        self.validate_change(change_id)
        self.validate_specs()
        date = datetime.now(timezone.utc).date().isoformat()
        destination = self.root / "openspec/changes/archive" / f"{date}-{change_id}"
        if destination.exists():
            raise DeliveryError(f"OpenSpec archive destination exists: {destination}")
        result = self._invoke("archive", change_id, "--yes", "--skip-specs")
        source = self.root / "openspec/changes" / change_id
        if result.returncode or source.exists() or not destination.is_dir():
            raise DeliveryError(
                "OpenSpec archive/sync did not complete: "
                + (result.stderr.strip() or result.stdout.strip())
            )
        self.validate_specs()
        return destination.resolve()

    def artifact_identity(
        self, root: Path, *, normalize_tasks: bool = True
    ) -> dict[str, str]:
        if root.is_symlink() or any(path.is_symlink() for path in root.rglob("*")):
            raise DeliveryError("OpenSpec artifact tree contains a symlink")
        files = sorted(path for path in root.rglob("*") if path.is_file())
        artifacts: dict[str, str] = {}
        for path in files:
            raw = path.read_bytes()
            if normalize_tasks and path == root / "tasks.md":
                text = raw.decode("utf-8")
                raw = re.sub(
                    r"^([-*][ \t]*\[)[ xX](\][ \t]*\S[^\r\n]*)$",
                    r"\1 \2",
                    text,
                    flags=re.MULTILINE,
                ).encode("utf-8")
            artifacts[path.relative_to(root).as_posix()] = hashlib.sha256(
                raw
            ).hexdigest()
        return artifacts

    def identity(self, change_id: str) -> dict[str, Any]:
        root = self.change_root(change_id)
        return {
            "schema": "changerail.openspec-plan.v1",
            "change_id": change_id,
            "openspec_version": self.VERSION,
            "package_lock_sha256": hashlib.sha256(
                (self.root / "tools/openspec/package-lock.json").read_bytes()
            ).hexdigest(),
            "artifacts": self.artifact_identity(root),
        }
