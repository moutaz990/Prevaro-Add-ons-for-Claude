#!/usr/bin/env python3
"""Package the plugin suites of this repository as single-file .plugin packages.

A suite is a folder with one core plugin (skills only) and small connector add-ons:
  <suite>/plugin/                 -> <suite>/<name>-<version>.plugin
  <suite>/connectors/<service>/   -> <suite>/connect-<service>-<version>.plugin

Each folder is the source and is installable as it is (entries in .claude-plugin/marketplace.json). This script
checks them and writes the packages with fixed timestamps, so the same source always gives the same file.

Checks before packing:
  * every plugin.json is valid, the name is kebab-case, and the marketplace lists the same version and source;
  * a core plugin bundles no connector; every skill folder has a SKILL.md whose `name` matches the folder;
  * a skill copied from elsewhere in the repository is identical to its source (one source of truth);
  * a connector add-on holds exactly one remote https server and no code. Three kinds are allowed:
      key      the vendor's fixed address, plus the user's own API key from a sensitive `userConfig` option
      signin   the vendor's fixed address and nothing else; the user signs in on the vendor's page
      user-url the address itself is the user's own (created in the vendor's console), from a sensitive option
  * no secrets, caches or company-specific words are packed.
Usage: python3 tools/build_plugins.py [suite ...]     (default: all suites)
"""
import json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_NAMES = re.compile(r"(^|/)(\.env[^/]*|.*\.pem|.*\.key|__pycache__|.*\.pyc|\.DS_Store)(/|$)")
# These plugins are generic: nothing from the company they were first built for may leak into them.
FORBIDDEN_WORDS = ("praesidium", "بريسيديوم", "psd-")
KEY_HEADER = "Bearer ${user_config.api_key}"
USER_URL = "${user_config.mcp_url}"

SUITES = {
    "content-studio": {
        "time": (2026, 11, 14, 0, 0, 0),
        "synced_skills": {"gemini-visual-generation": "gemini-media/skill/gemini-visual-generation"},
        "connectors": {
            "typefully": ("key", "https://mcp.typefully.com/mcp"),
            "buffer": ("key", "https://mcp.buffer.com/mcp"),
            "metricool": ("signin", "https://ai.metricool.com/mcp"),
        },
    },
    "meeting-assistant": {
        "time": (2026, 11, 19, 0, 0, 0),
        "synced_skills": {},
        "connectors": {
            "fathom": ("signin", "https://api.fathom.ai/mcp"),
            "fireflies": ("key", "https://api.fireflies.ai/mcp"),
            "zoho-mail": ("user-url", None),
        },
    },
}


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


def pack(base, name, version, files, time):
    out = base / f"{name}-{version}.plugin"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, data in files.items():
            info = zipfile.ZipInfo(rel, time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    return out


def sensitive_option(options, key, where):
    opt = options.get(key, {})
    if set(options) != {key} or not opt.get("sensitive") or not opt.get("required"):
        fail(f"{where}: userConfig must be one option, {key}, marked required and sensitive")


def check_connector(service, kind, url, manifest, files):
    where = f"connect-{service}"
    extra = sorted(set(files) - {".claude-plugin/plugin.json", ".mcp.json", "README.md"})
    if extra:
        fail(f"{where} may hold only plugin.json, .mcp.json and README.md; found {extra}")
    servers = json.loads(files[".mcp.json"]).get("mcpServers", {})
    if list(servers) != [service]:
        fail(f"{where}: .mcp.json must define exactly one server named '{service}'")
    s, options = servers[service], manifest.get("userConfig", {})
    if s.get("type") != "http" or set(s) - {"type", "url", "headers"}:
        fail(f"{where}: the server must be a remote http server and nothing else")
    headers = s.get("headers", {})
    if kind == "user-url":
        if s.get("url") != USER_URL or headers:
            fail(f"{where}: the address must be exactly {USER_URL}, with no headers")
        sensitive_option(options, "mcp_url", where)
        return "the user's own address"
    if s.get("url") != url:
        fail(f"{where}: the server must be {url}")
    if kind == "key":
        if headers != {"Authorization": KEY_HEADER}:
            fail(f"{where}: the only header allowed is Authorization: {KEY_HEADER}")
        sensitive_option(options, "api_key", where)
        return f"{url}  (API key)"
    if headers or options:
        fail(f"{where}: a sign-in connector sends no header and has no userConfig option")
    return f"{url}  (sign-in)"


def build(suite, spec, listed):
    base = ROOT / suite

    def check_listing(manifest, source):
        entry = listed.get(manifest["name"])
        if not entry or entry.get("version") != manifest["version"] or entry.get("source") != source:
            fail(f"marketplace.json must list {manifest['name']} with version {manifest['version']} and source {source}")

    for old in base.glob("*.plugin"):
        old.unlink()

    # --- the core plugin: skills only
    src = base / "plugin"
    manifest = read_manifest(src)
    if manifest["name"] != suite:
        fail(f"{suite}/plugin: plugin name must be {suite}")
    check_listing(manifest, f"./{suite}/plugin")
    if (src / ".mcp.json").exists():
        fail(f"{suite}: the core plugin must bundle no connector; connectors are separate add-ons")
    skills = sorted(p.name for p in (src / "skills").iterdir() if p.is_dir())
    for s in skills:
        md = src / "skills" / s / "SKILL.md"
        if not md.is_file():
            fail(f"{suite}: skills/{s} has no SKILL.md")
        m = re.search(r"^name:\s*(\S+)\s*$", md.read_text(encoding="utf-8").split("\n---", 1)[0], re.M)
        if not m or m.group(1) != s:
            fail(f"{suite}: skills/{s}/SKILL.md: name must be '{s}'")
    for skill, origin in spec["synced_skills"].items():
        if (src / "skills" / skill / "SKILL.md").read_bytes() != (ROOT / origin / "SKILL.md").read_bytes():
            fail(f"{suite}: skills/{skill} differs from {origin}; copy the latter over it")
    files = collect(src)
    out = pack(base, manifest["name"], manifest["version"], files, spec["time"])
    print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB  {len(files)} files  {len(skills)} skills")

    # --- the connector add-ons: one remote server each, no code
    for service, (kind, url) in spec["connectors"].items():
        src = base / "connectors" / service
        manifest = read_manifest(src)
        if manifest["name"] != f"connect-{service}":
            fail(f"{suite}/connectors/{service}: plugin name must be connect-{service}")
        check_listing(manifest, f"./{suite}/connectors/{service}")
        files = collect(src)
        how = check_connector(service, kind, url, manifest, files)
        out = pack(base, manifest["name"], manifest["version"], files, spec["time"])
        print(f"{out.relative_to(ROOT)}  {out.stat().st_size} bytes  {how}")


def main(argv=None):
    wanted = (argv if argv is not None else sys.argv[1:]) or list(SUITES)
    unknown = [s for s in wanted if s not in SUITES]
    if unknown:
        fail("unknown suite: " + ", ".join(unknown) + ". Known: " + ", ".join(SUITES))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    listed = {p["name"]: p for p in market["plugins"]}
    for suite in wanted:
        build(suite, SUITES[suite], listed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
