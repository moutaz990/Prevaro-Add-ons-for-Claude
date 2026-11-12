// Self-test for the installed cad MCP server (run by the installers).
// Starts the server over stdio, opens a drawing, saves it again as DXF, and checks the file exists.
// Usage: node selftest.mjs <input.dxf|dwg> <output.dxf>
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const [input, output] = process.argv.slice(2).map((p) => resolve(p));
const cli = join(here, "node_modules", "@mlightcad", "cad-mcp-server", "dist", "cli.js");
const code = `const ms = cad.blocks.find(b => b.isModelSpace)
const n = cad.entities.where(e => e.type === 'BlockReference' && e.ownerId === ms.id).length
cad.file.saveDxf(${JSON.stringify(output)})
return { blockReferences: n }`;

const client = new Client({ name: "kit-selftest", version: "1" });
await client.connect(new StdioClientTransport({ command: process.execPath, args: [cli], env: { ...process.env }, stderr: "ignore" }));
try {
  const tools = (await client.listTools()).tools.map((t) => t.name);
  if (!tools.includes("open_drawing") || !tools.includes("execute_cad_script")) throw new Error(`unexpected tools: ${tools}`);
  const open = JSON.parse((await client.callTool({ name: "open_drawing", arguments: { path: input, mode: "write" } })).content[0].text);
  if (!open.ok) throw new Error(`open_drawing failed: ${open.error ?? JSON.stringify(open)}`);
  const run = JSON.parse((await client.callTool({ name: "execute_cad_script", arguments: { code } })).content[0].text);
  if (!run.success) throw new Error(`execute_cad_script failed: ${run.error ?? run.message}`);
  if (!existsSync(output)) throw new Error("exported DXF missing");
  console.log(JSON.stringify({ ok: true, tools, ...run.data }));
} finally {
  await client.close();
}
