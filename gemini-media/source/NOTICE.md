# NOTICE — third-party material

Small parts of this extension are adapted from two MIT-licensed projects, after a security review of both.

## 1. crabkun/nano-banana-mcp
- Source: https://github.com/crabkun/nano-banana-mcp
- Commit: `1b0818d05dc2d101497b1e38358a155737b28a93` (2026-10-09)
- License: MIT
- Used in `src/gemini.ts`: classification of Google API errors, removal of the API key from error text, reading the image and token usage from an Interactions API response, base64 decoding, and the shape of the image request.
- Used in `src/pricing.ts`: the default per-token prices for the image model, after checking them against Google's pricing page.

## 2. u2n4/gemini-media-mcp
- Source: https://github.com/u2n4/gemini-media-mcp
- Commit: `e10cd49640565c652e60e2e3189865389a2dc86d` (2026-11-06)
- License: MIT
- No code was copied (it is Python). The logic was followed in `src/gemini.ts` and `src/server.ts`: the shape of the video request, the "job id, then poll" pattern, and waiting for the result file to become `ACTIVE` before downloading it.

Everything else was written for this extension.

## Bundled packages
The built `.mcpb` contains three npm packages, bundled into `server/index.mjs`:
`@modelcontextprotocol/server` 2.4.0 and `@modelcontextprotocol/core` 2.4.0 (Apache-2.0, the official MCP SDK) and `zod` 4.6.7 (MIT).

## License texts

### crabkun/nano-banana-mcp
```
MIT License

Copyright (c) 2026 crabkun

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

### u2n4/gemini-media-mcp
```
MIT License

Copyright (c) 2026 u2n4

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
