#!/usr/bin/env python3
"""Card 79: (re)build the merged 'open fixture form + value-read' manager template from the capture.

Reproducible build of `runtime/protocol-research/templates/tm-v1-open-plus-valueread/` (a gitignored
runtime artifact) from the `tm-v1-ro-batchQ3` capture, so any machine can regenerate it:

  - extract the fixture-form OPEN sequence (frames 8-17: MainFrame.CI -> CIButton click -> SecondaryFrame)
  - extract the value-READ frames (218-221)
  - inject a `secondary_frame_guid_ascii` dynamic field into every frame whose body hardcodes the captured
    SecondaryFrame GUID 73c822ff (session-specific -> must be rebound to the live open form)

Then the runner (`native_openform_probe` / `native_effect_probe`) opens the form and reads the live value.

Usage:  python build_tm_v1_open_template.py [--capture-dir tm-v1-ro-batchQ3]
Requires the capture present under runtime/protocol-research/captures/ (gitignored; sync separately)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from extract_manager_templates import (  # type: ignore
    MANAGER_TO_CLIENT,
    CLIENT_TO_MANAGER,
    build_template,
    read_capture_payloads,
    repo_root_from_script,
    resolve_capture_dir,
    utc_now,
)

# The fixture form's SecondaryFrame GUID as captured in tm-v1-ro-batchQ3. It is SESSION-SPECIFIC: the
# live form opens under a fresh GUID, so any frame that hardcodes this must rebind it (like ManagedForm).
CAPTURED_SECONDARY_FRAME_GUID = "73c822ff-e160-46d3-b7d5-d5e50a92c6f4"
OPEN_FRAMES = list(range(8, 18))        # MainFrame.CI -> CIButton "qa mcp protocol fixture v1" -> open
VALUE_READ_FRAMES = [218, 219, 220, 221]


def inject_secondary_frame_field(template: dict) -> bool:
    body = bytes.fromhex(template["body_hex"])
    needle = CAPTURED_SECONDARY_FRAME_GUID.encode("ascii")
    idx = body.find(needle)
    if idx < 0:
        return False
    if any(f.get("kind") == "secondary_frame_guid_ascii" for f in template["dynamic_fields"]):
        return False
    template["dynamic_fields"].append(
        {
            "name": "secondary_frame_guid",
            "kind": "secondary_frame_guid_ascii",
            "offset": idx,
            "length": len(needle),
            "source": "latest_client_response_secondary_frame_ref",
            "template_value": CAPTURED_SECONDARY_FRAME_GUID,
            "template_hex": body[idx : idx + len(needle)].hex(),
        }
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", default="tm-v1-ro-batchQ3")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    capture_dir = resolve_capture_dir(args.capture_dir, repo_root)
    payloads = read_capture_payloads(capture_dir)
    manager = payloads[MANAGER_TO_CLIENT]
    client = payloads[CLIENT_TO_MANAGER]

    templates = [build_template(capture_dir, fi, manager, client) for fi in OPEN_FRAMES + VALUE_READ_FRAMES]
    injected = sum(inject_secondary_frame_field(t) for t in templates)

    output_dir = (
        args.output_dir or repo_root / "runtime" / "protocol-research" / "templates" / "tm-v1-open-plus-valueread"
    ).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "protocol-manager-frame-templates.v1",
        "generated_at": utc_now(),
        "capture_dir": str(capture_dir),
        "note": "card 79: open fixture form (8-17) + value-read (218-221), SecondaryFrame GUID rebindable",
        "frames": OPEN_FRAMES + VALUE_READ_FRAMES,
        "templates": templates,
    }
    out_path = output_dir / "manager_frame_templates.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")
    print(f"frames: {OPEN_FRAMES + VALUE_READ_FRAMES}")
    print(f"secondary_frame_guid_ascii injected into {injected} frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
