# خوادم MCP (نطاق المستخدم)
الإصدارات من `manifest.json`. يسجّلها `install.ps1`. على Windows تُشغَّل عبر `cmd /c npx`.

| الاسم | الأمر | المفتاح | المرحلة |
|---|---|---|---|
| playwright | `claude mcp add playwright --scope user -- cmd /c npx -y @playwright/mcp@0.0.83` | لا | 1 |
| firecrawl | `claude mcp add firecrawl --scope user -- cmd /c npx -y firecrawl-mcp@3.35.0` | `FIRECRAWL_API_KEY` (بيئة المستخدم) | 6 |
| cad | `claude mcp add cad --scope user -e PLAYWRIGHT_BROWSER_CHANNEL=msedge -- node <setup>\mcp\cad-mcp-server\node_modules\@mlightcad\cad-mcp-server\dist\cli.js` (يثبّته `npm ci --ignore-scripts` من `mcp/cad-mcp-server/package-lock.json`) | لا | 10 |
| perplexity | `claude mcp add perplexity --scope user -- cmd /c npx -y @perplexity-ai/mcp-server@1.3.0` | `PERPLEXITY_API_KEY` (بيئة المستخدم) | 6 |

- التحقق: `claude mcp list`
- الإزالة: `claude mcp remove <name> --scope user`
- لا تمرر المفاتيح بـ `-e` لأنها تُكتب نصاً صريحاً في `~/.claude.json`.
