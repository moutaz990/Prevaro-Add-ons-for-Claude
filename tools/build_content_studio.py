#!/usr/bin/env python3
"""Package the Content Studio plugin and its connector add-ons as single-file .plugin packages.

  content-studio/plugin/                 -> content-studio/content-studio-<version>.plugin
  content-studio/connectors/<service>/   -> content-studio/connect-<service>-<version>.plugin

Each folder is the source and is installable as it is (entries in .claude-plugin/marketplace.json). This script
checks them and writes the packages with fixed timestamps, so the same source always gives the same file.

Checks before packing:
  * every plugin.json is valid, the name is kebab-case, and the marketplace lists the same version and source;
  * the core plugin bundles no connector; every skill folder has a SKILL.md whose `name` matches the folder;
  * the bundled gemini-visual-generation skill is identical to gemini-media/skill/ (one source of truth);
  * a connector add-on holds exactly one remote https server, no code, and only the expected host;
    a key, when used, comes from the plugin's own `userConfig` option marked sensitive, never from a file;
  * no secrets, caches or company-specific words are packed.
Usage: python3 tools/build_content_studio.py
"""
import json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "content-studio"
FIXED_TIME = (2026, 11, 14, 0, 0, 0)
FORBIDDEN_NAMES = re.compile(r"(^|/)(\.env[^/]*|.*\.pem|.*\.key|__pycache__|.*\.pyc|\.DS_Store)(/|$)")
# These plugins are generic: nothing from the company they were first built for may leak into them.
FORBIDDEN_WORDS = ("praesidium", "بريسيديوم", "psd-")
CONNECTORS = {  # service -> the only host its add-on may talk to
    "typefully": "https://mcp.typefully.com/mcp",
    "buffer": "https://mcp.buffer.com/mcp",
    "metricool": "https://ai.metricool.com/mcp",
}
KEY_HEADER = "Bearer ${user_config.api_key}"


def fail(msg):
    raise SystemExit("ERROR: " + msg)


def read_manifest(src):
    manifest = json.loads((src / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    name, version = manifest.get("name", ""), manifest.get("version", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        fail(f"{src}: plugin name must be kebab-case")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"{name}: version must be MAJOR.MINOR.PATCH")
    return manifest


def collect(src):
    files = {}
    for f in sorted(src.rglob("*")):
        rel = f.relative_to(src).as_posix()
        if not f.is_file() or "__pycache__" in f.parts or f.suffix == ".pyc" or f.name == ".DS_Store":
            continue
        if FORBIDDEN_NAMES.search(rel):
            fail(f"refusing to pack {src.name}/{rel}")
        data = f.read_bytes()
        if f.suffix in (".md", ".json", ".py"):
            text = data.decode("utf-8").lower()
            hit = next((w for w in FORBIDDEN_WORDS if w in text), None)
            if hit:
                fail(f"{src.name}/{rel} contains '{hit}': these plugins must stay generic")
        files[rel] = data
    return files


def pack(name, version, files):
    out = BASE / f"{name}-{version}.plugin"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, data in files.items():
            info = zipfile.ZipInfo(rel, FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    return out


def main():
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    listed = {p["name"]: p for p in market["plugins"]}

    def check_listing(manifest, source):
        entry = listed.get(manifest["name"])
        if not entry or entry.get("version") != manifest["version"] or entry.get("source") != source:
            fail(f"marketplace.json must list {manifest['name']} with version {manifest['version']} and source {source}")

    for old in BASE.glob("*.plugin"):
        old.unlink()

    # --- the core plugin: skills only
    src = BASE / "plugin"
    manifest = read_manifest(src)
    check_listing(manifest, "./content-studio/plugin")
    if (src / ".mcp.json").exists():
        fail("the core plugin must bundle no connector; connectors are separate add-ons")
    skills = sorted(p.name for p in (src / "skills").iterdir() if p.is_dir())
    for s in skills:
        md = src / "skills" / s / "SKILL.md"
        if not md.is_file():
            fail(f"skills/{s} has no SKILL.md")
        m = re.search(r"^name:\s*(\S+)\s*$", md.read_text(encoding="utf-8").split("\n---", 1)[0], re.M)
        if not m or m.group(1) != s:
            fail(f"skills/{s}/SKILL.md: name must be '{s}'")
    ours = (src / "skills" / "gemini-visual-generation" / "SKILL.md").read_bytes()
    theirs = (ROOT / "gemini-media" / "skill" / "gemini-visual-generation" / "SKILL.md").read_bytes()
    if ours != theirs:
        fail("skills/gemini-visual-generation differs from gemini-media/skill; copy the latter over it")
    files = collect(src)
    out = pack(manifest["name"], manifest["version"], files)
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB  {len(files)} files  {len(skills)} skills")

    # --- the connector add-ons: one remote server each, no code
    for service, url in CONNECTORS.items():
        src = BASE / "connectors" / service
        manifest = read_manifest(src)
        if manifest["name"] != f"connect-{service}":
            fail(f"connectors/{service}: plugin name must be connect-{service}")
        check_listing(manifest, f"./content-studio/connectors/{service}")
        files = collect(src)
        extra = sorted(set(files) - {".claude-plugin/plugin.json", ".mcp.json", "README.md"})
        if extra:
            fail(f"connect-{service} may hold only plugin.json, .mcp.json and README.md; found {extra}")
        servers = json.loads(files[".mcp.json"]).get("mcpServers", {})
        if list(servers) != [service]:
            fail(f"connect-{service}: .mcp.json must define exactly one server named '{service}'")
        s = servers[service]
        if s.get("type") != "http" or s.get("url") != url or set(s) - {"type", "url", "headers"}:
            fail(f"connect-{service}: the server must be the remote https server {url} and nothing else")
        headers, options = s.get("headers", {}), manifest.get("userConfig", {})
        if headers:
            if headers != {"Authorization": KEY_HEADER}:
                fail(f"connect-{service}: the only header allowed is Authorization: {KEY_HEADER}")
            key = options.get("api_key", {})
            if set(options) != {"api_key"} or not key.get("sensitive") or not key.get("required"):
                fail(f"connect-{service}: userConfig must be one option, api_key, marked required and sensitive")
        elif options:
            fail(f"connect-{service}: no header is sent, so no userConfig option is expected")
        out = pack(manifest["name"], manifest["version"], files)
        how = "API key" if headers else "sign-in"
        print(f"{out.relative_to(ROOT)}  {out.stat().st_size} bytes  {url}  ({how})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
