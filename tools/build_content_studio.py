#!/usr/bin/env python3
"""Package the Content Studio plugin: content-studio/plugin/ -> content-studio/content-studio-<version>.plugin

The plugin folder is the source and is installable as it is (marketplace entry in .claude-plugin/marketplace.json).
This script checks it and writes the single-file package for Claude Desktop, with fixed timestamps so the same
source always gives the same file.

Checks before packing:
  * plugin.json and .mcp.json are valid, the name is kebab-case, and the marketplace lists the same version;
  * every skill folder has a SKILL.md whose `name` matches the folder;
  * the bundled gemini-visual-generation skill is identical to gemini-media/skill/ (one source of truth);
  * no secrets, caches or company-specific words are packed.
Usage: python3 tools/build_content_studio.py
"""
import json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content-studio" / "plugin"
FIXED_TIME = (2026, 11, 13, 0, 0, 0)
FORBIDDEN_NAMES = re.compile(r"(^|/)(\.env[^/]*|.*\.pem|.*\.key|__pycache__|.*\.pyc|\.DS_Store)(/|$)")
# This plugin is generic: nothing from the company it was first built for may leak into it.
FORBIDDEN_WORDS = ("praesidium", "بريسيديوم", "psd-")


def fail(msg):
    raise SystemExit("ERROR: " + msg)


def main():
    manifest = json.loads((SRC / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    name, version = manifest.get("name", ""), manifest.get("version", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        fail("plugin name must be kebab-case")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail("plugin version must be MAJOR.MINOR.PATCH")
    servers = json.loads((SRC / ".mcp.json").read_text(encoding="utf-8")).get("mcpServers", {})
    for sname, s in servers.items():
        if s.get("type") != "http" or not str(s.get("url", "")).startswith("https://"):
            fail(f"connector {sname}: only remote https servers are bundled")
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entry = next((p for p in market["plugins"] if p["name"] == name), None)
    if not entry or entry.get("version") != version or entry.get("source") != "./content-studio/plugin":
        fail("marketplace.json must list this plugin with the same version and source ./content-studio/plugin")

    skills = sorted(p.name for p in (SRC / "skills").iterdir() if p.is_dir())
    for s in skills:
        md = SRC / "skills" / s / "SKILL.md"
        if not md.is_file():
            fail(f"skills/{s} has no SKILL.md")
        m = re.search(r"^name:\s*(\S+)\s*$", md.read_text(encoding="utf-8").split("\n---", 1)[0], re.M)
        if not m or m.group(1) != s:
            fail(f"skills/{s}/SKILL.md: name must be '{s}'")
    ours = (SRC / "skills" / "gemini-visual-generation" / "SKILL.md").read_bytes()
    theirs = (ROOT / "gemini-media" / "skill" / "gemini-visual-generation" / "SKILL.md").read_bytes()
    if ours != theirs:
        fail("skills/gemini-visual-generation differs from gemini-media/skill; copy the latter over it")

    files = {}
    for f in sorted(SRC.rglob("*")):
        rel = f.relative_to(SRC).as_posix()
        if not f.is_file() or "__pycache__" in f.parts or f.suffix == ".pyc" or f.name == ".DS_Store":
            continue
        if FORBIDDEN_NAMES.search(rel):
            fail(f"refusing to pack {rel}")
        data = f.read_bytes()
        if f.suffix in (".md", ".json", ".py"):
            text = data.decode("utf-8").lower()
            hit = next((w for w in FORBIDDEN_WORDS if w in text), None)
            if hit:
                fail(f"{rel} contains '{hit}': this plugin must stay generic")
        files[rel] = data

    for old in (ROOT / "content-studio").glob("*.plugin"):
        old.unlink()
    out = ROOT / "content-studio" / f"{name}-{version}.plugin"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, data in files.items():
            info = zipfile.ZipInfo(rel, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB  {len(files)} files  {len(skills)} skills")
    print("skills: " + ", ".join(skills))
    print("connectors: " + ", ".join(sorted(servers)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
