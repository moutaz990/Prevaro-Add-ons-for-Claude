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

## قبل التثبيت: ماذا تحتاج؟
| تريد استخدام | الجهاز | ما تثبّته أولاً |
|---|---|---|
| **الحزمة كاملة** (Claude Code) | كمبيوتر Windows 10/11 أو macOS أو Linux | Claude Code، Node.js 22+، Git، ويُفضَّل Chrome أو Edge. ffmpeg اختياري للفيديو. الأوامر أدناه |
| **مهارات Chat فقط** (مجلد `chat-skills`) | أي متصفح أو تطبيق Claude للكمبيوتر، ولا تثبيت | حساب Claude فيه code execution مفعّل |
| **الجوال** | تطبيق Claude للجوال | لا تثبيت على الجوال. ترفع المهارات من المتصفح، ثم تستخدمها من حسابك [يُتحقق على الجوال] |

**أوامر التحضير على Windows (PowerShell، مرة واحدة):**
```powershell
irm https://claude.ai/install.ps1 | iex
```
```powershell
winget install OpenJS.NodeJS.LTS
```
```powershell
winget install Git.Git
```
```powershell
winget install Gyan.FFmpeg
```

**أوامر التحضير على macOS (Terminal، مرة واحدة):**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```
```bash
xcode-select --install
```
```bash
brew install node@22 ffmpeg
```

- **Homebrew:** إن لم يكن مثبتاً عندك، فثبّته من brew.sh.
- **بعد التحضير:** أغلق النافذة وافتحها من جديد، ثم اكتب `claude` وسجّل الدخول بحسابك.
- **الحزمة:** شغّل أمر التثبيت الموجود في README.

## أين يعمل كل شيء؟ وكيف تشغّله؟
| الواجهة | الجهاز | كيف تفتحها | ماذا يعمل فيها من الحزمة | ماذا يستفيد المستخدم |
|---|---|---|---|---|
| **Terminal** (الأمر `claude`) | كمبيوتر | افتح PowerShell أو Terminal واكتب `claude` | **كل شيء**: المهارات، الوكلاء، البلغنز، خوادم MCP (Playwright، cad) | أقوى تجربة. يعمل على ملفاتك ويفتح المواقع والمخططات ويصنع الفيديو |
| **Claude Code داخل تطبيق Claude للكمبيوتر** (قسم Code، جلسة محلية) | كمبيوتر | افتح تطبيق Claude، ثم Code، واختر مجلداً على جهازك | المهارات والبلغنز. الوكلاء وخوادم MCP [يُتحقق بالتجربة] | نفس قدرات Terminal بواجهة رسومية |
| **VS Code** (إضافة Claude Code) | كمبيوتر | ثبّت إضافة Claude Code في VS Code | كل شيء | العمل داخل محرر الكود |
| **Claude Code على الويب أو الجوال** (جلسات سحابية) | متصفح أو جوال | claude.ai/code أو تطبيق الجوال | **فقط** المهارات المرفوعة لحسابك (من `chat-skills`). لا يقرأ ملفات جهازك | برمجة على مستودعات GitHub من أي مكان |
| **Claude Chat** (claude.ai، تطبيق الكمبيوتر، تطبيق الجوال) | أي جهاز | محادثة عادية | **فقط** المهارات المرفوعة (`chat-skills`) | تصميم صفحات وملصقات وثيمات ورسوم تفاعلية داخل المحادثة |

**القاعدة المختصرة:**
- **كل ما يحتاج برنامجاً على جهازك** (فتح مخططات، فيديو، فحص مواقع، وكلاء، بلغنز) يعمل في **Claude Code على الكمبيوتر** فقط.
- **المهارات النصية والتصميمية** تعمل أيضاً في **Chat** بعد رفعها.

## ماذا أقدر أعمل من Chat، وماذا يحتاج Claude Code؟
| المهمة | Claude Chat (متصفح، تطبيق، جوال) | Claude Code على الكمبيوتر |
|---|---|---|
| قراءة مخطط **PDF**: فهمه، وصفه، استخراج الملاحظات | ✅ ارفع الـ PDF | ✅ |
| فتح ملف **DWG** وقراءته | ❌ عملياً لا: صيغة مغلقة ولا أداة لها في المحادثة. صدّره PDF أو DXF | ✅ خادم `cad`: فتح، عدّ الرموز، قياس، تعديل، تصدير DXF |
| عدّ الرموز في **DXF** | ⚠️ غير مضمون: يحتاج code execution ومكتبة مناسبة في بيئة المحادثة [يُتحقق] | ✅ خادم `cad` |
| **موشن جرافيك وفيديو MP4** (HyperFrames، Remotion) | ❌ يحتاج ffmpeg ومتصفحاً على الجهاز | ✅ |
| رسوم متحركة تُعرض داخل المحادثة (HTML أو SVG) | ✅ بدون ملف فيديو | ✅ |
| ملصقات، ثيمات، صفحات هبوط، رسوم Hairline | ✅ بعد رفع ملفات [chat-skills/](chat-skills/) | ✅ |
| فحص موقع حي ولقطات شاشة | ❌ | ✅ Playwright |
| الوكلاء الفرعيون، auto-handoff | ❌ | ✅ |

**القاعدة:**
- ما يحتاج **برنامجاً على الجهاز** يعمل في Claude Code على الكمبيوتر فقط: DWG، فيديو MP4، فحص المواقع، الوكلاء.
- **المحادثة:** للفهم والكتابة والتصميم، وقراءة المخططات بصيغة PDF.

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
**أسهل طريقة:** ملفات جاهزة في مجلد [`chat-skills/`](chat-skills/):
- frontend-design
- theme-factory
- canvas-design
- mcp-builder
- hairline-create
- hairline-adopt

**الخطوات:**
1. حمّل ملف ZIP من GitHub (Download raw file).
2. claude.ai: **Settings > Capabilities**، وفعّل «Code execution and file creation».
3. **Customize > Skills > + > Upload a skill**، وارفع الـ ZIP كما هو.
4. اطلب في أي محادثة، مثل «صمّم صفحة هبوط لـ...». Claude يستخدم المهارة تلقائياً.

**ملاحظات:**
- **المزامنة:** المهارة المفعّلة في حسابك تظهر أيضاً في Claude Code عند تسجيل الدخول بنفس الحساب، في اتجاه واحد فقط.
- **غير موجودة في `chat-skills`:** design-taste-frontend و hyperframes و webapp-testing، لأنها تحتاج متصفحاً أو برامج على الجهاز.

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

## Before installing
| You want | Device | Install first |
|---|---|---|
| The full pack (Claude Code) | Windows 10/11, macOS or Linux computer | Claude Code, Node.js 22+ and Git. Chrome or Edge is recommended, and ffmpeg is optional (video) |
| Chat skills only (`chat-skills/`) | Any browser or the Claude desktop app | Nothing; enable code execution in your account |
| Phone | Claude mobile app | Nothing on the phone. Upload skills from a browser, then use them from your account [to be verified on mobile] |

**Windows (one-time setup):**
```powershell
irm https://claude.ai/install.ps1 | iex
```
```powershell
winget install OpenJS.NodeJS.LTS
```
```powershell
winget install Git.Git
```
```powershell
winget install Gyan.FFmpeg
```

**macOS (one-time setup):**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```
```bash
xcode-select --install
```
```bash
brew install node@22 ffmpeg
```

## Where each part runs
| Surface | Device | What works | Benefit |
|---|---|---|---|
| Terminal (`claude`) | Computer | Everything: skills, agents, plugins, MCP (Playwright, cad) | Full power on your local files, sites, drawings and video |
| Desktop app, Code tab (local session) | Computer | Skills and plugins. Agents and MCP to be verified | The same power in a GUI |
| VS Code extension | Computer | Everything | Work inside your editor |
| Claude Code on the web or mobile (cloud sessions) | Browser or phone | Only skills uploaded to your account; your local files are not read | Coding on GitHub repos from anywhere |
| Claude chat (web, desktop, mobile) | Any | Only uploaded skills (`chat-skills/`) | Pages, posters, themes and interactive art in chat |

Rule of thumb: anything that needs software on your computer runs in Claude Code on the computer only. Text and design skills also run in chat once uploaded.

## What can I do in chat, and what needs Claude Code?
| Task | Claude chat (web, desktop, mobile) | Claude Code on a computer |
|---|---|---|
| Read a **PDF** drawing (understand it, describe it, extract notes) | Yes, upload the PDF | Yes |
| Open a **DWG** file | Practically no: closed format with no tool for it in chat. Export to PDF or DXF | Yes, with the `cad` server: open, count blocks, measure, edit, export DXF |
| Count blocks in a **DXF** | Not guaranteed: needs code execution and a suitable library in the chat sandbox (unverified) | Yes, with the `cad` server |
| **Motion graphics / MP4 video** (HyperFrames, Remotion) | No: needs ffmpeg and a browser on the computer | Yes |
| Animations shown inside the chat (HTML/SVG) | Yes, with no video file | Yes |
| Posters, themes, landing pages, Hairline art | Yes, after uploading [chat-skills/](chat-skills/) | Yes |
| Live site checks and screenshots | No | Yes, with Playwright |
| Subagents, auto-handoff | No | Yes |

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
Ready-made ZIPs are in [`chat-skills/`](chat-skills/). To use one:
1. Enable code execution in claude.ai **Settings > Capabilities**.
2. Go to **Customize > Skills > Upload a skill**, select the ZIP as is, and enable it.

Skills enabled on your account sync down to Claude Code (one way). Agents, plugins and MCP servers are Claude Code only.

## Known limits
- **cad 1.7.8:** its DWG-to-DXF export can drop MINSERT arrays and attribute values, and it has no PDF export. Use an AutoCAD DXF export for numbers that matter.
- **Remotion:** requires a company license above 3 employees.
- **Windows:** hooks need Git Bash.
