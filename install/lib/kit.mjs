#!/usr/bin/env node
// Prevaro Add-ons for Claude setup helper. Cross-platform (Windows / macOS / Linux), Node 22+.
// Used by install.ps1 / install.sh / uninstall.*. No network access except `git fetch` of pinned commits.
//
// Commands:
//   install-skills <manifest.json> <claudeDir> <ledger.json> <phase>
//   install-local-skills <repoDir> <manifest.json> <claudeDir> <ledger.json>
//   remove-skills  <claudeDir> <ledger.json>
//   copy-agents    <srcDir> <claudeDir> <ledger.json>
//   remove-agents  <claudeDir> <ledger.json>
//   merge-settings <settings.json> <fragment.json> <ledger.json>
//   merge-claudemd <target CLAUDE.md> <source CLAUDE.md>
//   backup         <claudeDir> <backupDir> <ledger.json>
//   restore        <claudeDir> <ledger.json>
//   allowed-models <models.json> <prefix,prefix,...>
//   ledger-add     <ledger.json> <section> <value>
//   ledger-get     <ledger.json> <section>

import { execFileSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync, copyFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const MARKER = ".kit-source.json";
const MD_START = "<!-- PREVARO:START (managed by Prevaro Add-ons for Claude; edit outside this block) -->";
const MD_END = "<!-- PREVARO:END -->";
const FORBIDDEN = /(?!)/; // never matches: no protected paths in the public kit

function guard(p) {
  if (FORBIDDEN.test(p)) throw new Error(`refusing to touch protected path: ${p}`);
  return p;
}
const readJson = (p, dflt) => (existsSync(p) ? JSON.parse(readFileSync(p, "utf8").replace(/^﻿/, "")) : dflt);
const writeJson = (p, v) => writeFileSync(guard(p), JSON.stringify(v, null, 2) + "\n", "utf8");

function ledgerLoad(p) {
  return readJson(p, { createdAt: new Date().toISOString(), skills: [], agents: [], mcp: [], plugins: [], npm: [], env: [], marketplaces: [], backup: null, settingsAdded: {} });
}
function ledgerPush(p, section, value) {
  const l = ledgerLoad(p);
  if (!Array.isArray(l[section])) l[section] = [];
  if (!l[section].includes(value)) l[section].push(value);
  writeJson(p, l);
}

function git(args, cwd) {
  try {
    return execFileSync("git", args, { cwd, stdio: ["ignore", "pipe", "pipe"], encoding: "utf8" }).trim();
  } catch (e) {
    // Surface git's own message (last stderr lines), not just "Command failed".
    const detail = String(e.stderr || e.message || e).trim().split("\n").slice(-3).join(" | ");
    throw new Error(`git ${args.filter((a) => !a.startsWith("-c")).slice(0, 3).join(" ")}: ${detail}`);
  }
}

// Fetch exactly one commit of a repo into a fresh temp dir and verify the SHA.
// Partial clone (blobs on demand) + sparse checkout: only the requested folders are downloaded and
// written to disk, so large repos (e.g. hyperframes, ~9k files) never need a full checkout.
function fetchPinned(repo, commit, paths) {
  const dir = mkdtempSync(join(tmpdir(), "kit-src-"));
  git(["init", "-q"], dir);
  git(["remote", "add", "origin", repo], dir);
  git(["config", "core.sparseCheckout", "true"], dir);
  git(["config", "core.longpaths", "true"], dir);
  git(["config", "core.autocrlf", "false"], dir);
  writeFileSync(join(dir, ".git", "info", "sparse-checkout"), paths.map((p) => `/${p.replace(/^\/+|\/+$/g, "")}/\n`).join(""), "utf8");
  git(["-c", "protocol.version=2", "fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit], dir);
  git(["-c", "advice.detachedHead=false", "checkout", "-q", "FETCH_HEAD"], dir);
  const head = git(["rev-parse", "HEAD"], dir);
  if (head !== commit) throw new Error(`commit mismatch for ${repo}: got ${head}, want ${commit}`);
  return dir;
}

function installSkills(manifestPath, claudeDir, ledgerPath, phase) {
  const m = readJson(manifestPath);
  const skills = m.skills.filter((s) => String(s.phase) === String(phase));
  const cache = new Map();
  const results = [];
  for (const s of skills) {
    const dest = guard(join(claudeDir, "skills", s.name));
    try {
      if (existsSync(dest) && !existsSync(join(dest, MARKER))) {
        results.push({ name: s.name, status: "SKIPPED", reason: "a skill with this name already exists and was not installed by Prevaro Add-ons for Claude" });
        continue;
      }
      const key = `${s.repo}@${s.commit}`;
      if (!cache.has(key)) {
        const paths = skills.filter((x) => x.repo === s.repo && x.commit === s.commit).map((x) => x.path);
        cache.set(key, fetchPinned(s.repo, s.commit, paths));
      }
      const src = join(cache.get(key), s.path);
      if (!existsSync(join(src, "SKILL.md"))) throw new Error(`SKILL.md not found at ${s.path}`);
      rmSync(dest, { recursive: true, force: true });
      mkdirSync(join(claudeDir, "skills"), { recursive: true });
      cpSync(src, dest, { recursive: true, filter: (p) => !p.split(/[\\/]/).includes(".git") });
      writeJson(join(dest, MARKER), { repo: s.repo, commit: s.commit, tag: s.tag ?? null, path: s.path, installedAt: new Date().toISOString() });
      ledgerPush(ledgerPath, "skills", s.name);
      results.push({ name: s.name, status: "OK", commit: s.commit });
    } catch (e) {
      results.push({ name: s.name, status: "FAILED", reason: String(e.message || e).replace(/\s+/g, " ").slice(0, 300) });
    }
  }
  for (const d of cache.values()) rmSync(d, { recursive: true, force: true });
  console.log(JSON.stringify(results));
}

// Local skills that live in this repo (manifest.localSkills). Keeps an existing .venv so re-runs are fast.
function installLocalSkills(repoDir, manifestPath, claudeDir, ledgerPath) {
  const m = readJson(manifestPath);
  let commit = "working-tree";
  try { commit = git(["rev-parse", "HEAD"], repoDir); } catch {}
  const results = [];
  for (const s of m.localSkills ?? []) {
    const dest = guard(join(claudeDir, "skills", s.name));
    try {
      if (existsSync(dest) && !existsSync(join(dest, MARKER))) {
        results.push({ name: s.name, status: "SKIPPED", reason: "a skill with this name already exists and was not installed by Prevaro Add-ons for Claude" });
        continue;
      }
      const src = join(repoDir, s.path);
      if (!existsSync(join(src, "SKILL.md"))) throw new Error(`SKILL.md not found at ${s.path}`);
      if (existsSync(dest)) for (const f of readdirSync(dest)) if (f !== ".venv") rmSync(join(dest, f), { recursive: true, force: true });
      mkdirSync(dest, { recursive: true });
      cpSync(src, dest, { recursive: true, filter: (p) => !p.split(/[\\/]/).some((x) => x === "__pycache__" || x === ".venv") });
      writeJson(join(dest, MARKER), { repo: "prevaro-addons (local)", commit, path: s.path, installedAt: new Date().toISOString() });
      ledgerPush(ledgerPath, "skills", s.name);
      results.push({ name: s.name, status: "OK", commit });
    } catch (e) {
      results.push({ name: s.name, status: "FAILED", reason: String(e.message || e).replace(/\s+/g, " ").slice(0, 300) });
    }
  }
  console.log(JSON.stringify(results));
}

function removeSkills(claudeDir, ledgerPath) {
  const l = ledgerLoad(ledgerPath);
  for (const name of l.skills) {
    const dest = guard(join(claudeDir, "skills", name));
    if (existsSync(join(dest, MARKER))) {
      rmSync(dest, { recursive: true, force: true });
      console.log(`removed skill ${name}`);
    } else console.log(`kept skill ${name} (no kit marker)`);
  }
}

function copyAgents(srcDir, claudeDir, ledgerPath) {
  const dst = guard(join(claudeDir, "agents"));
  mkdirSync(dst, { recursive: true });
  const out = [];
  for (const f of readdirSync(srcDir).filter((f) => f.endsWith(".md"))) {
    const target = join(dst, f);
    const incoming = readFileSync(join(srcDir, f), "utf8");
    if (existsSync(target)) {
      const cur = readFileSync(target, "utf8");
      if (cur === incoming) { ledgerPush(ledgerPath, "agents", f); out.push({ name: f, status: "OK", note: "already identical" }); continue; }
      if (!cur.includes("# source: https://github.com/msitarzewski/agency-agents")) {
        out.push({ name: f, status: "SKIPPED", reason: "an agent with this file name exists and is not ours" });
        continue;
      }
    }
    copyFileSync(join(srcDir, f), target);
    ledgerPush(ledgerPath, "agents", f);
    out.push({ name: f, status: "OK" });
  }
  console.log(JSON.stringify(out));
}

function removeAgents(claudeDir, ledgerPath) {
  const l = ledgerLoad(ledgerPath);
  for (const f of l.agents) {
    const p = guard(join(claudeDir, "agents", f));
    if (existsSync(p) && readFileSync(p, "utf8").includes("# source: https://github.com/msitarzewski/agency-agents")) {
      rmSync(p);
      console.log(`removed agent ${f}`);
    }
  }
}

// Additive merge: env keys are set; permission rule lists are unioned; other top-level keys only if absent.
function mergeSettings(settingsPath, fragmentPath, ledgerPath) {
  const cur = readJson(settingsPath, {});
  const frag = readJson(fragmentPath);
  const added = { env: [], deny: [], keys: [] };
  for (const [k, v] of Object.entries(frag)) {
    if (k.startsWith("_")) continue;
    if (k === "env") {
      cur.env ??= {};
      for (const [ek, ev] of Object.entries(v)) { if (cur.env[ek] !== ev) { cur.env[ek] = ev; added.env.push(ek); } }
    } else if (k === "permissions") {
      cur.permissions ??= {};
      for (const [pk, pv] of Object.entries(v)) {
        if (Array.isArray(pv)) {
          cur.permissions[pk] ??= [];
          for (const rule of pv) if (!cur.permissions[pk].includes(rule)) { cur.permissions[pk].push(rule); if (pk === "deny") added.deny.push(rule); }
        }
      }
    } else if (!(k in cur)) { cur[k] = v; added.keys.push(k); }
  }
  mkdirSync(join(settingsPath, ".."), { recursive: true });
  writeJson(settingsPath, cur);
  const l = ledgerLoad(ledgerPath); l.settingsAdded = added; writeJson(ledgerPath, l);
  console.log(JSON.stringify(added));
}

function mergeClaudeMd(target, source) {
  const block = `${MD_START}\n${readFileSync(source, "utf8").trim()}\n${MD_END}\n`;
  let cur = existsSync(target) ? readFileSync(guard(target), "utf8") : "";
  const s = cur.indexOf(MD_START), e = cur.indexOf(MD_END);
  if (s !== -1 && e !== -1) cur = cur.slice(0, s) + block + cur.slice(e + MD_END.length + 1);
  else cur = cur ? `${cur.trimEnd()}\n\n${block}` : block;
  writeFileSync(guard(target), cur, "utf8");
  console.log(JSON.stringify({ lines: cur.split("\n").length }));
}

function backup(claudeDir, backupDir, ledgerPath) {
  guard(backupDir);
  mkdirSync(backupDir, { recursive: true });
  const home = join(claudeDir, "..");
  const items = [
    [join(claudeDir, "settings.json"), "settings.json"],
    [join(claudeDir, "CLAUDE.md"), "CLAUDE.md"],
    [join(home, ".claude.json"), "dot-claude.json"],
  ];
  const record = { dir: backupDir, files: {} };
  for (const [src, name] of items) {
    if (existsSync(src)) { copyFileSync(src, join(backupDir, name)); record.files[name] = { from: src, existed: true }; }
    else record.files[name] = { from: src, existed: false };
  }
  const l = ledgerLoad(ledgerPath);
  if (!l.backup) l.backup = record; // keep the FIRST backup: it is the pre-kit state
  l.backups = [...(l.backups ?? []), record];
  writeJson(ledgerPath, l);
  console.log(JSON.stringify(record));
}

// Restore settings.json and CLAUDE.md to the pre-kit state. ~/.claude.json is NOT overwritten
// (it holds unrelated state); MCP entries are removed with `claude mcp remove` instead.
function restore(claudeDir, ledgerPath) {
  const l = ledgerLoad(ledgerPath);
  if (!l.backup) { console.log("no backup recorded"); return; }
  for (const name of ["settings.json", "CLAUDE.md"]) {
    const rec = l.backup.files[name];
    const target = guard(join(claudeDir, name));
    if (rec?.existed) { copyFileSync(join(l.backup.dir, name), target); console.log(`restored ${name}`); }
    else if (existsSync(target)) { rmSync(target); console.log(`removed ${name} (did not exist before)`); }
  }
}

function allowedModels(modelsJsonPath, prefixes) {
  // CLI output may start with log lines (e.g. "Loaded env from ..."): parse from the first JSON bracket.
  const text = readFileSync(modelsJsonPath, "utf8").replace(/^\uFEFF/, "");
  const start = text.search(/[\[{]/);
  const raw = start === -1 ? [] : JSON.parse(text.slice(start));
  const want = prefixes.split(",").map((p) => p.trim()).filter(Boolean);
  const ids = new Set();
  const walk = (v) => {
    if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === "object") {
      for (const k of ["id", "model", "fullId", "qualifiedId"]) if (typeof v[k] === "string") ids.add(v[k]);
      Object.values(v).forEach(walk);
    }
  };
  walk(raw);
  const out = [...ids].filter((id) => want.some((p) => id.startsWith(p + "/"))).sort();
  console.log(JSON.stringify(out));
}

const [cmd, ...a] = process.argv.slice(2);
try {
  a.forEach((arg) => guard(String(arg)));
  switch (cmd) {
    case "install-skills": installSkills(a[0], a[1], a[2], a[3]); break;
    case "install-local-skills": installLocalSkills(a[0], a[1], a[2], a[3]); break;
    case "remove-skills": removeSkills(a[0], a[1]); break;
    case "copy-agents": copyAgents(a[0], a[1], a[2]); break;
    case "remove-agents": removeAgents(a[0], a[1]); break;
    case "merge-settings": mergeSettings(a[0], a[1], a[2]); break;
    case "merge-claudemd": mergeClaudeMd(a[0], a[1]); break;
    case "backup": backup(a[0], a[1], a[2]); break;
    case "restore": restore(a[0], a[1]); break;
    case "allowed-models": allowedModels(a[0], a[1]); break;
    case "ledger-add": ledgerPush(a[0], a[1], a[2]); break;
    case "ledger-get": console.log(JSON.stringify(ledgerLoad(a[0])[a[1]] ?? null)); break;
    default:
      console.error(`unknown command: ${cmd}`);
      process.exit(2);
  }
} catch (e) {
  console.error(`kit.mjs ${cmd}: ${e.message}`);
  process.exit(1);
}
