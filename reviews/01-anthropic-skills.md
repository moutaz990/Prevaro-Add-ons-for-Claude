# مراجعة: anthropics/skills (المهارات الرسمية)
- **المصدر:** https://github.com/anthropics/skills @ `2c5958ecac7cee2b583967a2c4981d0f4a75c579` (2026-11-06). لكل مهارة ملف LICENSE.txt.
- **المهارات السبع:** frontend-design، webapp-testing، web-artifacts-builder، canvas-design (5.6MB خطوط)، theme-factory، brand-guidelines، mcp-builder.
- **hooks:** لا يوجد في أي منها.
- **سكربتات تُشغَّل فقط عند طلب المهارة:**
  - `web-artifacts-builder/scripts/init-artifact.sh`: ينشئ مشروع Vite ويثبّت pnpm و Tailwind و shadcn/radix من npm، داخل مجلد المشروع. لا يُشغَّل عند التثبيت.
  - `webapp-testing/scripts/with_server.py`: يشغّل خادماً محلياً للاختبار.
  - `mcp-builder/scripts/evaluation.py` و `connections.py`: أدوات تقييم لخادم MCP، وتستدعي Anthropic API عند تشغيلها يدوياً.
- **ملاحظة:** `brand-guidelines` تحمل هوية Anthropic كمثال؛ لا تُستخدم كهوية للشركة.
- **القرار:** مقبول.
