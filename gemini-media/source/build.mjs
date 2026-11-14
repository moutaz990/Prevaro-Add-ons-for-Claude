#!/usr/bin/env node
// Builds the Claude Desktop extension from this folder:
//   1. bundles the server and its dependencies into ONE file (no node_modules inside the bundle),
//   2. validates manifest.json with Anthropic's official packer,
//   3. writes ../gemini-media-<version>.mcpb
import { build } from "esbuild";
import { execFileSync } from "node:child_process";
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const stage = join(here, "build");
const manifest = JSON.parse(readFileSync(join(here, "manifest.json"), "utf8"));
const mcpb = join(here, "node_modules", ".bin", process.platform === "win32" ? "mcpb.cmd" : "mcpb");

rmSync(stage, { recursive: true, force: true });
mkdirSync(join(stage, "server"), { recursive: true });

await build({
  entryPoints: [join(here, "src", "server.ts")],
  outfile: join(stage, "server", "index.mjs"),
  bundle: true,
  platform: "node",
  format: "esm",
  target: "node18",
  legalComments: "none",
  logLevel: "warning",
});
cpSync(join(here, "manifest.json"), join(stage, "manifest.json"));
cpSync(join(here, "icon.png"), join(stage, "icon.png")); // drawn by tools/build_assets.py
writeFileSync(join(stage, "README.txt"), "Gemini Images & Video - Claude Desktop extension. Open this .mcpb file with Claude Desktop to install it.\n");

const run = (args) => execFileSync(mcpb, args, { stdio: "inherit", shell: process.platform === "win32" });
run(["validate", join(stage, "manifest.json")]);
const out = join(here, "..", `gemini-media-${manifest.version}.mcpb`);
run(["pack", stage, out]);
console.log(`\nBuilt ${out}`);
