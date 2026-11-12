# دليل الفوائد والاستخدام — Prevaro Add-ons for Claude

**العربية** | [English](#english-guide)

## لماذا هذه الإضافة؟
Claude Code قوي وحده، لكنه يعمل بأسلوب عام. هذه الإضافة تعطيه:

1. **ذوقاً تصميمياً واضحاً.** مهارات تمنع شكل «القوالب المكررة» في المواقع، وتفرض فحص النتيجة في متصفح حقيقي.
2. **عيوناً.** يفتح الصفحة التي بناها، ويلتقط صورة للكمبيوتر والجوال، ويصحح ما يراه بنفسه.
3. **قدرة على الفيديو.** فيديو موشن قصير يُكتب بالكود ويخرج MP4، دون برنامج مونتاج.
4. **قراءة مخططات AutoCAD.** يفتح DWG و DXF على جهازك، ويعدّ الرموز ويقيس المسافات.
5. **فريقاً من المختصين.** 9 وكلاء، كل واحد بخبرة وقواعد عمل محددة.
6. **ذاكرة للجلسات الطويلة.** عند امتلاء المحادثة يكتب ملخصاً منظماً ويكمل في جلسة نظيفة.
7. **أماناً.** إصدارات ثابتة مراجَعة، وإزالة نظيفة بأمر واحد.

## المكوّنات وفوائدها
| المكوّن | الفائدة | مثال طلب |
|---|---|---|
| **design-taste-frontend** | مواقع شركات بمستوى احترافي: نظام تصميم واحد، صور حقيقية، حركة مدروسة، وفحص في متصفح حقيقي قبل التسليم | «صمّم موقعاً لشركة صيانة بصفحة رئيسية وخدمات وتواصل» |
| **frontend-design** (Anthropic) | واجهات مميزة وغير مكررة | «أعد تصميم هذه الصفحة بشكل أقل عمومية» |
| **web-artifacts-builder** | صفحات HTML تفاعلية متكاملة (React + Tailwind) في ملف واحد | «اصنع حاسبة تكلفة تفاعلية في صفحة واحدة» |
| **webapp-testing** + **Playwright MCP** | اختبار المواقع وأخذ لقطات وتعبئة النماذج تلقائياً | «افتح موقعي والتقط صورة جوال واذكر المشاكل» |
| **theme-factory** | ثيمات ألوان وخطوط جاهزة للعروض والصفحات | «طبّق ثيماً احترافياً على هذا العرض» |
| **brand-guidelines** | مثال لتطبيق هوية علامة على المخرجات (هوية Anthropic كمثال، استبدلها بهويتك) | — |
| **canvas-design** | ملصقات وتصاميم ثابتة PNG/PDF | «اصنع ملصقاً A3 لإعلان خدمة» |
| **hairline-create / adopt** | رسوم خطية أيزومترية تتفاعل مع المؤشر، أو تحويل SVG لرسم تفاعلي | `/hairline-adopt logo.svg` |
| **mcp-builder** | بناء خادم MCP لربط Claude بأي نظام أو API | «ابنِ MCP يقرأ من نظام المخزون» |
| **HyperFrames** (مهارتان + CLI) | فيديو من HTML: عناوين، شعارات متحركة، شرائح، ترجمة | «فيديو 10 ثوانٍ 1080p بالشعار ونص الخدمات» |
| **Remotion** (بلغن) | فيديو بـ React: قوالب قابلة للتكرار، رسوم بيانية متحركة | «قالب فيديو أسبوعي لأرقام المبيعات» |
| **cad** (MCP) | فتح DWG/DXF، عدّ الرموز، القياس، التعديل، التصدير إلى DXF | «افتح plan.dwg وعدّ الرموز حسب الاسم والطبقة» |
| **auto-handoff** (بلغن) | لا ضياع للسياق في الجلسات الطويلة، والملخص يبقى على جهازك | تلقائي |
| **Firecrawl / Perplexity** (اختياري) | سحب صفحات الويب وبحث موثّق | «اسحب مواصفات هذا المنتج من موقع المورد» |

## الوكلاء التسعة
| الوكيل | متى تستخدمه |
|---|---|
| `frontend-developer` | بناء واجهات React/Vue، أداء، وصولية |
| `backend-architect` | تصميم API، قواعد بيانات، أنظمة قابلة للتوسع |
| `code-reviewer` | مراجعة صحة وأمان وقابلية صيانة |
| `ai-generated-code-auditor` | فحص الكود المولّد بالذكاء الاصطناعي: مفاتيح مكشوفة، صلاحيات، حقن |
| `network-engineer` | Cisco/Juniper/Palo Alto: VLAN، جدران نارية، خطط تغيير مع rollback |
| `ui-designer` | أنظمة تصميم ومكونات |
| `ux-architect` | هيكلة تجربة المستخدم و CSS |
| `brand-guardian` | اتساق الهوية |
| `content-creator` | خطط ومحتوى تسويقي (مسودات) |

اطلب صراحة: «استخدم الوكيل network-engineer لـ ...»، أو اترك Claude يختار.

## هل يوفّر التوكنز؟
بصراحة: **الهدف الجودة والتنظيم، لا التوفير المباشر.**

| يوفّر | يزيد |
|---|---|
| منع قراءة `node_modules` والملفات الكبيرة. ملخص الجلسات الطويلة يصغّر السياق. المهارات لا تُحمّل كاملة إلا عند استخدامها | كل خادم MCP يضيف تعريفات أدواته. الوكيل الفرعي له استهلاكه الخاص |

للقياس اكتب `/context` داخل Claude قبل التثبيت وبعده.

## لا يحتاج تفعيلاً
- Claude يختار المهارة أو الوكيل حسب طلبك.
- أول استخدام لأي أداة MCP يطلب إذنك.

**أوامر مفيدة:**
| الأمر | ماذا يعرض أو يفعل |
|---|---|
| `/skills` | المهارات المتاحة |
| `/agents` | الوكلاء |
| `/mcp` | الخوادم المتصلة |
| `/context` | استهلاك المحادثة |
| `/compact` | ضغط المحادثة |
| `/rewind` | التراجع عن خطوة |
| `/resume` | فتح جلسة سابقة |
| `/reload-skills` | إعادة تحميل المهارات |

<a id="chat"></a>
## استخدام المهارات في Claude Chat
1. claude.ai: **Settings > Capabilities**، وفعّل «Code execution and file creation».
2. اضغط مجلد المهارة إلى ZIP:
   - Windows: المجلد في `%USERPROFILE%\.claude\skills\<الاسم>`، ثم زر يمين، ثم Send to، ثم Compressed folder.
   - الماك: المجلد في `~/.claude/skills/<الاسم>`، ثم زر يمين، ثم Compress.
3. **Customize > Skills > + > Upload a skill**.

- **المزامنة:** المهارة المفعّلة في حسابك تنزل تلقائياً إلى Claude Code عند تسجيل الدخول بنفس الحساب، في اتجاه واحد فقط.
- **مهارات تعمل في Chat:** frontend-design، theme-factory، canvas-design، brand-guidelines، hairline.
- **مهارات تبقى في Claude Code:** hyperframes و webapp-testing و design-taste-frontend، لأنها تحتاج برامج على الجهاز أو متصفحاً.

## حدود يجب معرفتها
- **خادم cad:** تصدير DWG إلى DXF في الإصدار المثبّت (1.7.8) قد يُسقط الرموز المكررة كمصفوفة (MINSERT) وقيم attributes. ولا يصدّر PDF. للأرقام المهمة صدّر DXF من AutoCAD.
- **Remotion:** رخصة شركة مطلوبة لأكثر من 3 موظفين.
- **HyperFrames:** يستخدم Chrome أو Edge الموجود. إن لم يوجد ينزّل متصفحه عند أول تصيير.
- **Windows:** بعض الـ hooks تحتاج Git Bash، ويأتي مع Git for Windows.

## حل المشاكل
| المشكلة | الحل |
|---|---|
| بند `FAILED` | السطر نفسه يحمل رسالة الخطأ. السجل الكامل في `prevaro-claude-setup/install-log-*.md` |
| `claude` لا يرى الجديد | افتح Terminal جديداً، أو `/reload-skills` |
| خادم cad لا يتصل | `/mcp`. على الماك ثبّت Chrome أو أعد التثبيت ليُنزّل Chromium |
| `npm` يرفض التثبيت العام على الماك | السكربت يحوّل تلقائياً إلى `~/.npm-global`. أضف `~/.npm-global/bin` إلى PATH في `~/.zshrc` |
| فيديو التحقق لم يُنشأ | ثبّت ffmpeg ثم أعد التثبيت |

---

<a id="english-guide"></a>
# Benefits & Usage Guide (English)

## Why this add-on pack?
Out of the box, Claude Code is capable but generic. This pack adds:

1. **Design taste.** Skills that prevent template-looking websites and require checking the result in a real browser.
2. **Eyes.** Claude opens what it built, screenshots desktop and mobile views, and fixes what it sees.
3. **Video.** Short motion videos written as code and rendered to MP4.
4. **CAD reading.** Opens DWG/DXF locally, counts blocks and measures distances.
5. **A team of specialists.** Nine subagents with focused expertise and working rules.
6. **Memory for long sessions.** A structured handoff brief, then a fresh session, so context is never lost.
7. **Safety.** Reviewed pinned versions and a clean one-command uninstall.

## Components
| Component | Benefit |
|---|---|
| design-taste-frontend, frontend-design | Professional, non-generic websites checked in a real browser |
| web-artifacts-builder | Single-file interactive HTML apps (React + Tailwind) |
| webapp-testing + Playwright MCP | Automated site testing, screenshots, form filling |
| theme-factory, canvas-design, brand-guidelines, hairline | Themes, posters, brand application, interactive line art |
| mcp-builder | Build your own MCP servers |
| HyperFrames, Remotion | Code-based video to MP4 |
| cad MCP | Open, query, measure, edit DWG/DXF; export DXF |
| auto-handoff | Context-safe long sessions; briefs stay on your machine |
| Firecrawl / Perplexity (optional) | Web scraping and cited search (paid keys) |
| 9 subagents | frontend, backend, code review, AI-code security audit, networking, UI, UX, brand, content |

## Token use
The goal is quality and structure, not direct savings. Savings come from:
- ignore rules that keep `node_modules` and large files out of context;
- automatic handoffs that keep long sessions small;
- skills that load fully only when used.

Costs come from MCP tool definitions and from subagents running their own context. Measure with `/context`.

## Activation
None needed. Claude picks skills and agents from your request. The first use of an MCP tool asks for permission. Useful commands: `/skills`, `/agents`, `/mcp`, `/context`, `/compact`, `/rewind`, `/resume`, `/reload-skills`.

## Claude chat
To use a skill in Claude chat:
1. Enable code execution in claude.ai **Settings > Capabilities**.
2. Zip the skill folder from `~/.claude/skills/<name>`.
3. Upload it in **Customize > Skills**.

Skills enabled on your account sync down to Claude Code (one way). Agents, plugins and MCP servers are Claude Code only.

## Known limits
- **cad 1.7.8:** its DWG-to-DXF export can drop MINSERT arrays and attribute values, and it has no PDF export. Use an AutoCAD DXF export for numbers that matter.
- **Remotion:** requires a company license above 3 employees.
- **Windows:** hooks need Git Bash.
