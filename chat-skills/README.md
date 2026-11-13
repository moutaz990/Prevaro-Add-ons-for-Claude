# مهارات جاهزة للرفع على Claude Chat | Chat-ready skills

**العربية:** ملفات ZIP جاهزة للرفع مباشرة إلى Claude Chat، دون تثبيت أي شيء على الكمبيوتر.

| الملف | ماذا يفعل في المحادثة | الرخصة |
|---|---|---|
| `frontend-design.zip` | يصمم صفحات ومكونات ويب مميزة وغير مكررة | Apache-2.0 |
| `theme-factory.zip` | يطبّق ثيماً احترافياً (ألوان وخطوط) على عرض أو مستند أو صفحة | Apache-2.0 |
| `canvas-design.zip` | يصنع ملصقات وتصاميم ثابتة PNG/PDF | Apache-2.0 |
| `mcp-builder.zip` | يرشدك لبناء خادم MCP يربط Claude بأي نظام | Apache-2.0 |
| `hairline-create.zip` | يرسم شكلاً خطياً أيزومترياً تفاعلياً في ملف HTML واحد | MIT |
| `hairline-adopt.zip` | يحوّل شعاراً أو أيقونة SVG إلى رسم خطي تفاعلي | MIT |
| `gemini-visual-generation.zip` | يرافق إضافة [Gemini Images & Video](../gemini-media/): مقاسات جاهزة للمنشور والستوري والأغلفة، كتابة وصف جيد للصورة والفيديو، وعرض التكلفة قبل أي فيديو. **بلا الإضافة لا يولّد شيئاً** | MIT |

### طريقة الرفع (من المتصفح أو تطبيق الكمبيوتر)
1. حمّل الملف: افتحه في GitHub ثم اضغط **Download raw file**.
2. في claude.ai: **Settings > Capabilities**، وفعّل **Code execution and file creation**.
3. **Customize > Skills > + > Upload a skill**، واختر ملف الـ ZIP كما هو، **دون فك الضغط**.
4. فعّل المهارة من القائمة، ثم اطلب منها ما تريد في أي محادثة، مثلاً «صمّم صفحة هبوط لـ...».

### ملاحظات
- **الخطط:** المهارات متاحة لخطط Free و Pro و Max و Team و Enterprise، بشرط تفعيل code execution. في Team و Enterprise قد يعطّل المسؤول الرفع.
- **المزامنة:** المهارة المفعّلة في حسابك تظهر أيضاً في Claude Code حين تسجّل الدخول بنفس الحساب.
- **الجوال:** الرفع يتم من المتصفح أو تطبيق الكمبيوتر. استخدامها من تطبيق الجوال بعد التفعيل [يُتحقق].
- **canvas-design** حجمه 2.6MB لأنه يضم خطوطاً. إن رفض الرفع بسبب الحجم، فالحد الأقصى غير منشور [يُتحقق].
- **ما الذي تغيّر عن الأصل:** اختصرت وصف كل مهارة إلى 200 حرف أو أقل (شرط الرفع) وأبقيت الاسم والوصف فقط. التعليمات والسكربتات لم تتغير. المصدر والـ commit في `NOTICE.txt` داخل كل ملف.
- **إعادة البناء:** `python3 tools/build_chat_skills.py`

---

**English:** ZIP files ready to upload to Claude chat. No computer install is needed.
1. Download a ZIP (open it on GitHub, then **Download raw file**).
2. In claude.ai, enable **Settings > Capabilities > Code execution and file creation**.
3. Go to **Customize > Skills > + > Upload a skill**, select the ZIP as is (do not unzip it), and enable it.

`gemini-visual-generation.zip` goes with the [Gemini Images & Video](../gemini-media/README.md#english) extension: ready-made sizes for posts, stories and covers, how to write image and video prompts, and showing the cost before any video. It generates nothing without the extension, and it is written for this repository (MIT).

Each of the other packages keeps the upstream instructions and files unchanged. The only change is the frontmatter: `name` plus a description of 200 characters or less, to meet the upload rules. Source, commit and license are in `NOTICE.txt` and `LICENSE.txt` inside each ZIP.
