#!/usr/bin/env python3
"""Build Claude-chat-ready skill ZIPs from the pinned sources in manifest.json.

For each skill in chat-skills/chat-skills.json:
  * fetch only that folder at the pinned commit (git sparse + partial checkout),
  * rewrite the SKILL.md frontmatter to `name` + a <=200-char `description` (chat upload limits),
  * add the upstream LICENSE and a NOTICE (source, commit, changes),
  * write chat-skills/<name>.zip with the skill folder at the ZIP root (deterministic timestamps).
Usage: python3 tools/build_chat_skills.py
"""
import json, re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "chat-skills"
FIXED_TIME = (2026, 11, 12, 0, 0, 0)

def git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)

def fetch(repo, commit, paths, dest):
    git(["init", "-q"], dest); git(["remote", "add", "origin", repo], dest)
    git(["config", "core.sparseCheckout", "true"], dest)
    (dest / ".git" / "info" / "sparse-checkout").write_text("".join(f"/{p.strip('/')}/\n" for p in paths))
    git(["fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit], dest)
    git(["-c", "advice.detachedHead=false", "checkout", "-q", "FETCH_HEAD"], dest)

def main():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    pinned = {s["name"]: s for s in manifest["skills"]}
    spec = json.loads((OUT / "chat-skills.json").read_text())
    for item in spec["skills"]:
        name, desc = item["name"], item["description"]
        assert len(name) <= 64 and re.fullmatch(r"[a-z0-9-]+", name), name
        assert len(desc) <= 200, f"{name}: description is {len(desc)} chars"
        src = pinned[name]
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            fetch(src["repo"], src["commit"], [src["path"]], tmp)
            if item["license_file"].startswith("../"):
                # License sits at the repo root: read it from the commit (blob fetched on demand).
                lic_text = subprocess.run(["git", "show", "FETCH_HEAD:LICENSE"], cwd=tmp, check=True,
                                          capture_output=True, text=True).stdout
            else:
                lic_text = (tmp / src["path"] / item["license_file"]).read_text()
            stage = tmp / "stage" / name
            shutil.copytree(tmp / src["path"], stage, ignore=shutil.ignore_patterns(".git"))
            skill_md = stage / "SKILL.md"
            text = skill_md.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            body = text[m.end():]
            skill_md.write_text(f"---\nname: {name}\ndescription: {json.dumps(desc)}\n---\n{body}", encoding="utf-8")
            (stage / "LICENSE.txt").write_text(lic_text, encoding="utf-8")
            (stage / "NOTICE.txt").write_text(
                f"Source: {src['repo']} ({src['path']}) at commit {src['commit']}\nLicense: {item['license']} (see LICENSE.txt)\n"
                "Changes for Claude chat upload: SKILL.md frontmatter reduced to `name` and a shortened `description` (<= 200 chars).\n"
                "Instructions, scripts and assets are unchanged.\nPackaged by Prevaro Add-ons for Claude.\n", encoding="utf-8")
            zpath = OUT / f"{name}.zip"
            with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
                for f in sorted(stage.rglob("*")):
                    if f.is_file():
                        info = zipfile.ZipInfo(f"{name}/{f.relative_to(stage).as_posix()}", FIXED_TIME)
                        info.compress_type = zipfile.ZIP_DEFLATED
                        info.external_attr = 0o644 << 16
                        z.writestr(info, f.read_bytes())
            print(f"{name:16} {zpath.stat().st_size // 1024:>6} KB  {src['commit'][:7]}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
