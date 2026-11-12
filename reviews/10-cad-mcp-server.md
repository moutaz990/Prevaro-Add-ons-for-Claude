# مراجعة: mlightcad/cad-viewer — packages/cad-mcp-server
## المصدر والإصدار
| | القيمة |
|---|---|
| المستودع | github.com/mlightcad/cad-viewer، MIT. HEAD عند المراجعة `833c202` (2026-11-11) |
| الحزمة | `@mlightcad/cad-mcp-server`. حقل repository يطابق المستودع |
| الإصدار المثبّت | **1.7.8**، الإصدار المستقر الوحيد (2026-11-02). أول نشر للحزمة كان 2026-10-25. فروع 1.8.0 كلها preview |
| استثناء قاعدة 14 يوماً | 1.7.8 عمره 10 أيام. البديل الأقدم preview فقط، فاخترنا المستقر (DECISIONS D35) |
| التحقق من tarball | sha512 يطابق سجل npm |
| شجرة الاعتماديات | `mcp/cad-mcp-server/package-lock.json` يثبّت 122 حزمة. **لا يوجد أي install script** في الشجرة كلها. التثبيت بـ `npm ci --ignore-scripts` |
| overrides | 9 حزم طرف ثالث كان عمرها أقل من 14 يوماً ثُبّتت على إصدار أقدم متوافق: playwright/playwright-core 1.64.1، hono 4.13.14، @hono/node-server 2.1.5، jose 6.2.13، express-rate-limit 8.7.1، ip-address 10.7.5، encodeurl 2.0.1، tslib 2.8.1. حزم `@mlightcad/*` بقيت على إصدارات 1.7.8 المتسقة |
| رخصة محرك DWG | `@mlightcad/libredwg-converter` و `libredwg-web` بترخيص **GPL-3.0** (LibreDWG مترجم إلى WASM). الاستخدام الداخلي لا يفرض شيئاً. **توزيعه ضمن منتج لعملاء يفرض شروط GPL.** البائع يعرض محلّلاً تجارياً بديلاً (PROPRIETARY-PARSER.md)، لم نطلبه |

## ماذا يشغّل
- عملية Node عبر stdio تكشف أداتين فقط: `open_drawing` و`execute_cad_script`.
- عند أول طلب يشغّل **Chromium headless** عبر Playwright. على Windows نوجّهه لـ **Edge المثبت** (`PLAYWRIGHT_BROWSER_CHANNEL=msedge`)، وعلى macOS لـ Chrome أو Edge إن وُجد، وإلا يُنزّل Chromium الخاص بـ Playwright 1.64.1. يُغلق بعد 30 ث خمول.
- خادم HTTP داخلي على **127.0.0.1 بمنفذ عشوائي** يخدم صفحة العارض والملف المفتوح فقط، ومحمي من `..`.
- `execute_cad_script` ينفّذ JavaScript يكتبه النموذج داخل صفحة المتصفح، عبر واجهة `cad.*` مع مدقق يرفض الواجهات غير المعروفة. لا وصول لـ Node أو للنظام إلا عبر `cad.file.saveDxf`.
- **الكتابة على القرص:** `saveDxf(path)` يكتب ملف `.dxf` في **أي مسار** يحدده السكربت (`path.resolve`)، ويضيف `.dxf` إن غاب. → المهارة تقيّده بمسار بجانب المخطط وباسم `.from-dwg.dxf`. وكل استدعاء أداة MCP يمر بأذونات Claude Code.

## الشبكة
| الاتصال | متى | القرار |
|---|---|---|
| `open_drawing` بمسار `http(s)://` | إن طُلب رابط | ممنوع في المهارة وCLAUDE.md: ملفات محلية فقط |
| `cdn.jsdelivr.net/gh/mlightcad/cad-data/fonts/` | تحميل خطوط CAD (SHX/TTF) عند عرض النصوص | مقبول: يُرسل اسم الخط فقط، لا محتوى المخطط. بلا إنترنت تُعرض النصوص بخط بديل |
| Playwright CDN | تنزيل Chromium على macOS عند غياب Chrome و Edge | وقت التثبيت فقط |

- **إعدادات النماذج الخارجية:** فحصنا الخادم وصفحة العارض (4.4MB) بحثاً عن openai وanthropic وgemini وdeepseek وapiKey وAuthorization وtelemetry وanalytics وsentry وposthog: **لا شيء**.
- حزم الوكيل داخل التطبيق (`cad-llm-plugin`، `cad-agent-plugin`) **ليست ضمن** الخادم، فلا يوجد ما نعطّله. لا telemetry.

## نتائج الاختبار الفعلي (Linux، Chromium 1.64.1، SwiftShader)
| الاختبار | النتيجة |
|---|---|
| `tools/list` | `open_drawing`، `execute_cad_script` ✓ |
| فتح DXF التجريبي | ✓ |
| فتح DWG حقيقي (عينتان عامتان من mlightcad/cad-data: baseline-sample.dwg، patient-chairs.dwg) | ✓ |
| تصدير DXF + مقارنة العدّ | ✓ عدد الكتل في المستوى الأعلى مطابق للمحرك في العينتين |
| **فقد في تصدير DXF (1.7.8)** | ⚠️ على المخطط التجريبي: **MINSERT فُقد**، فاختفت 6 سماعات (المحرك يراه block بلا اسم). **قيم attributes فُقدت.** **أسماء dynamic blocks** بقيت `*U1`. وملف التصدير فيه قسم OBJECTS لا يقرؤه ezdxf |
| الحماية المضافة | السكربت `export-with-check.js` يكتب عدّ المحرك داخل الـ DXF المصدَّر. `takeoff.py` يقارنه، وعند أي فرق يطبع **EXPORT CHECK FAILED** ويعنون Excel بـ «DO NOT USE». ويقرأ الملف دون OBJECTS عند الحاجة، مع تنبيه |
| PDF | **غير متاح في 1.7.8.** `savePdf` موجود في 1.8.0-preview فقط [يُتحقق عند صدور 1.8.0 مستقراً] |
| الدقة مقابل AutoCAD | **[يُتحقق]:** لم نقارن بإخراج AutoCAD لنفس DWG. الفحص يضمن أن التصدير لم يفقد ما رآه المحرك، لا أن المحرك قرأ كل شيء |

## القرار
مقبول **للفتح والاستعلام والقياس وتحويل DWG للحصر المبدئي**، بالضوابط التالية:
- إصدار مثبّت بـ lockfile و `--ignore-scripts`.
- ملفات محلية فقط، والمتصفح Edge على Windows.
- فحص تطابق إلزامي بعد التصدير، ومنع تام داخل `claude-omni`.
- كميات عروض الأسعار تُؤكَّد من تصدير AutoCAD (أو ODA، انظر reviews/11).
