# Third-party notices

The [MIT License](LICENSE) in this repository covers the work written for it: the installers, the
tools, the documentation, the reviews, and the Gemini Images & Video extension.

It does **not** relicense other people's work. The material below keeps its own license.

## Included in this repository

| Where | What | From | License |
|---|---|---|---|
| `claude-home/agents/*.md` | 9 subagent definitions. The source and commit are in the header of each file; only the front matter was changed | [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) @ `8ae6164` | MIT (text below) |
| `chat-skills/frontend-design.zip`, `theme-factory.zip`, `canvas-design.zip`, `mcp-builder.zip` | Skills, with a shortened description | [anthropics/skills](https://github.com/anthropics/skills) @ `2c5958e` | Apache-2.0. Each ZIP contains its `LICENSE.txt` and a `NOTICE.txt` |
| `chat-skills/hairline-create.zip`, `hairline-adopt.zip` | Skills, with a shortened description | [lucasmarkes/hairline](https://github.com/lucasmarkes/hairline) @ `37d2e78` | MIT. Each ZIP contains its `LICENSE.txt` and a `NOTICE.txt` |
| `chat-skills/canvas-design.zip` → `canvas-fonts/` | Fonts shipped with that skill | Various font authors | SIL Open Font License; the license file sits next to each font |
| `gemini-media/source/src/gemini.ts`, `pricing.ts` | Small adapted parts | [crabkun/nano-banana-mcp](https://github.com/crabkun/nano-banana-mcp), [u2n4/gemini-media-mcp](https://github.com/u2n4/gemini-media-mcp) | MIT. Details and both license texts in `gemini-media/source/NOTICE.md` |
| `gemini-media/gemini-media-*.mcpb` | Three npm packages bundled into the extension | `@modelcontextprotocol/server`, `@modelcontextprotocol/core`, `zod` | Apache-2.0, Apache-2.0, MIT |
| `gemini-media/gemini-media-install-guide-ar-en.pdf` | Embedded font | Noto Sans Arabic | SIL Open Font License 1.1 |

## Installed on your computer by the installer, not stored here

The Claude Code pack downloads these at install time, at the versions pinned in `manifest.json`.
Each one is used under its own license, and the review for each is in `reviews/`. Two deserve attention:

- **Remotion** is free for individuals and for companies of up to 3 employees; larger companies need a Company License.
- **The DWG engine of the `cad` server** (`@mlightcad/libredwg-converter`, `libredwg-web`) is licensed under **GPL-3.0**.

## License text: msitarzewski/agency-agents

```
MIT License

Copyright (c) 2025 AgentLand Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
