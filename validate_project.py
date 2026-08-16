#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
OGG_MAGIC = b"OggS"
errors: list[str] = []

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    suffix = path.suffix.lower()
    try:
        header = path.open("rb").read(16)
    except OSError as exc:
        errors.append(f"unreadable: {path}: {exc}")
        continue
    if suffix == ".png" and not header.startswith(PNG_MAGIC):
        errors.append(f"invalid PNG signature: {path}")
    if suffix == ".ogg" and not header.startswith(OGG_MAGIC):
        errors.append(f"invalid Ogg signature: {path}")

required = [
    ROOT / "project.godot",
    ROOT / "core/game.tscn",
    ROOT / "core/game.gd",
    ROOT / "assets/horror_packs/brand/Lord Brand Horror RP/sounds/mob/jump_scare2.ogg",
    ROOT / "assets/horror_packs/brand/Insanity Shader RP/textures/environment/clouds.png",
    ROOT / "assets/horror_packs/brand/eRetro Vision RP/pack_icon.png",
]
for path in required:
    if not path.exists():
        errors.append(f"missing required file: {path.relative_to(ROOT)}")

project = ROOT / "project.godot"
if project.exists():
    text = project.read_text(encoding="utf-8", errors="replace")
    for required_line in ["run/main_scene=\"res://core/game.tscn\"", "[preset.0]", "name=\"Android\"", "platform=\"Android\""]:
        if required_line not in text:
            errors.append(f"project.godot missing: {required_line}")

scene = ROOT / "core/game.tscn"
if scene.exists():
    text = scene.read_text(encoding="utf-8", errors="replace")
    for required_line in ["[gd_scene", "[ext_resource type=\"Script\" path=\"res://core/game.gd\"", "[node name=\"Game\" type=\"Node2D\"]"]:
        if required_line not in text:
            errors.append(f"core/game.tscn missing: {required_line}")

# Decode the specifically reported Ogg file as an extra check.
reported_ogg = ROOT / "assets/horror_packs/brand/Lord Brand Horror RP/sounds/mob/jump_scare2.ogg"
if reported_ogg.exists():
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=format_name", "-of", "default=nw=1:nk=1", str(reported_ogg)], capture_output=True, text=True)
    if result.returncode != 0 or "ogg" not in result.stdout.lower():
        errors.append(f"ffprobe cannot decode reported Ogg: {reported_ogg}: {result.stderr.strip()}")

if errors:
    print("INTEGRITY_FAILED")
    print("\n".join(errors))
    sys.exit(1)
print("INTEGRITY_OK")
print(f"Scanned {sum(1 for p in ROOT.rglob('*') if p.is_file())} files")
