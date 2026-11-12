# Gemini Images & Video — إضافة لتطبيق Claude Desktop

**العربية** | [English](#english)

إضافة تجعل Claude يولّد الصور ويعدّلها ويولّد مقاطع فيديو قصيرة عبر **Google Gemini**، بمفتاحك أنت. تُثبَّت بنقرتين، والملفات تُحفظ على جهازك.

**الملف نفسه يعمل على Mac و Windows.**

| | |
|---|---|
| **تنزيل الإضافة** | [gemini-media-1.0.0.mcpb](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/gemini-media/gemini-media-1.0.0.mcpb) |
| **دليل التثبيت PDF (عربي + إنجليزي)** | [gemini-media-install-guide-ar-en.pdf](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/gemini-media/gemini-media-install-guide-ar-en.pdf) |

> **الحالة:** الإضافة مختبَرة آلياً (35 فحصاً على الملف المحزوم نفسه، بخادم Google وهمي). لم تُجرَّب بعد داخل Claude Desktop حقيقي على Mac أو Windows، ولا على مفتاح حقيقي. جرّب صورة واحدة أولاً، وأخبرنا في [Issues](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/issues) إن واجهت مشكلة.

## ماذا تضيف إلى Claude؟
بعد التثبيت تقول لـClaude ما تريد بالعربية أو الإنجليزية، مثل «ولّد صورة مربعة لـ…» أو «عدّل هذه الصورة واجعل الخلفية بيضاء»، فيستخدم هذه الأدوات:

| الأداة | ماذا تفعل | التكلفة التقريبية على مفتاحك |
|---|---|---|
| `generate_image` | صور من وصف نصي: مقاس 1K أو 2K أو 4K، أي نسبة أبعاد، من 1 إلى 4 صور | 0.04 دولار للصورة 1K |
| `edit_image` | تعديل صورة من جهازك بتعليمات مكتوبة: تغيير خلفية، إعادة إظهار، تعديل جزء. الأصل لا يتغير | مثل التوليد |
| `generate_video` | مقطع 3 إلى 10 ثوانٍ، أفقي 16:9 أو رأسي 9:16، من وصف أو من صورة بداية | 0.10 دولار لكل ثانية |
| `get_job` | متابعة مهمة الفيديو حتى تكتمل وتُحفظ | مجاناً |
| `usage` | ما صرفتَه هذا الشهر مقابل الحد الذي وضعته | مجاناً |

## ماذا تحتاج؟
- تطبيق **Claude Desktop** على Mac أو Windows، محدَّثاً. الإضافة لا تعمل في المتصفح ولا في الجوال.
- **مفتاح Gemini API** من Google AI Studio: <https://aistudio.google.com/apikey>. يجب أن يكون لمشروع مفعّل فيه الدفع، فتوليد الصور والفيديو بلا باقة مجانية.
- لا شيء آخر. لا Node.js ولا أوامر.

## التثبيت
1. نزّل الملف [gemini-media-1.0.0.mcpb](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/gemini-media/gemini-media-1.0.0.mcpb).
2. افتحه **بنقرتين**. يفتح Claude Desktop نافذة التثبيت، فاضغط **Install**.
   - إن لم يفتح: في Claude Desktop افتح **Settings ← Extensions ← Advanced settings ← Install Extension…** واختر الملف.
3. املأ الحقول الثلاثة:

   | الحقل | ماذا تضع |
   |---|---|
   | **Gemini API key** | الصق مفتاحك |
   | **Save files to** | المجلد الذي تُحفظ فيه النتائج (الافتراضي `Documents/Gemini Media`) |
   | **Monthly spending cap (USD)** | أعلى مبلغ تسمح بصرفه شهرياً (الافتراضي 30) |

4. احفظ الإعدادات وتأكد أن الإضافة **مفعّلة**.
5. افتح محادثة جديدة واكتب: «ولّد صورة مربعة لكاميرا مراقبة بيضاء على خلفية رمادية». وافق على استخدام الأداة، وتجد الصورة في المجلد الذي اخترته.

## إن لم يعمل
| المشكلة | الحل |
|---|---|
| لا يحدث شيء عند فتح الملف | استخدم طريقة Settings في الخطوة 2، وتأكد أن Claude Desktop محدَّث |
| الأدوات لا تظهر في المحادثة | أغلق Claude Desktop وافتحه من جديد |
| Mac يعرض تنبيهاً أمنياً | System Settings ← Privacy & Security ثم اسمح |
| لا توجد صفحة Extensions، أو التثبيت مرفوض | حسابك ضمن مؤسسة (Team أو Enterprise) تقيّد الإضافات. اطلب من مالك المؤسسة السماح بها |
| Google ترفض المفتاح | تأكد أنه منسوخ كاملاً، وأن مشروعه مفعّل فيه الدفع |

## الخصوصية والأمان
- **مفتاحك** يحفظه Claude Desktop في التخزين الآمن للنظام (Keychain على Mac و Credential Manager على Windows). الإضافة ترسله إلى Google فقط، ولا تكتبه في أي ملف أو سجل.
- **لا خادم وسيط.** الاتصال الوحيد هو بـ`generativelanguage.googleapis.com`. لا telemetry.
- **الأوصاف والصور التي تطلب تعديلها تُرسل إلى Google.** لا ترسل بيانات عملاء أو بيانات شخصية.
- **قراءة الملفات:** الإضافة تقرأ فقط ملفاً بامتداد صورة، حتى 8 ميغابايت، ومحتواه صورة JPEG أو PNG أو WebP فعلاً. أي ملف آخر يُرفض قبل أي اتصال.
- **الكتابة:** في مجلد الحفظ فقط، بأسماء جديدة، ولا تكتب فوق ملف موجود.
- **الحد الشهري** يُفرض على جهازك. ضعه 0 لإيقاف الصرف كله. فاتورة Google هي المرجع، وأرقام الإضافة تقدير.
- **الإضافة غير موقّعة رقمياً**، فقد يعرض Claude تنبيهاً عند التثبيت. الكود كاملاً في [source/](source/) لمن يريد مراجعته أو بناء الملف بنفسه، والمراجعة الأمنية في [reviews/11-gemini-media.md](../reviews/11-gemini-media.md).

## تغيير الإعدادات والإزالة
| أريد | أفعل |
|---|---|
| تغيير المفتاح أو المجلد أو الحد الشهري | Settings ← Extensions ← Gemini Images & Video ← Configure |
| إيقاف الصرف فوراً | ضع الحد الشهري 0 |
| تعطيل الإضافة أو إزالتها | Settings ← Extensions: أطفئها أو اضغط Uninstall. الملفات المحفوظة تبقى |

## الأسعار
الأرقام أعلاه تقريبية، كما وجدناها لصفحة أسعار Google بتاريخ 2026-11-12. راجع الصفحة للأسعار الحالية: [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing). النماذج المستخدمة: `gemini-nano-banana-2.1` للصور و`gemini-omni-1.1-flash` للفيديو. دقة الفيديو 720p. الدقة الأعلى معطّلة لأن Google لم تنشر سعرها للثانية.

## للمطوّرين: البناء من المصدر
```bash
cd gemini-media/source
```
```bash
npm ci
```
```bash
npm run build
```
```bash
npm test
```
`npm run build` يجمع الخادم في ملف واحد، ويفحص `manifest.json` بأداة Anthropic الرسمية، ويكتب `gemini-media-<version>.mcpb`. و`npm test` يفك الملف المحزوم كما يفعل Claude Desktop ويختبره بعميل MCP الرسمي.

---

<a id="english"></a>
## English

An extension that lets Claude generate and edit images and generate short videos with **Google Gemini**, using your own API key. Two clicks to install; files are saved on your computer.

**The same file works on Mac and Windows.**

| | |
|---|---|
| **Download the extension** | [gemini-media-1.0.0.mcpb](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/gemini-media/gemini-media-1.0.0.mcpb) |
| **Install guide, PDF (Arabic + English)** | [gemini-media-install-guide-ar-en.pdf](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/gemini-media/gemini-media-install-guide-ar-en.pdf) |

> **Status:** tested automatically (35 checks against the packed file, with a fake Google server). It has not yet been tried inside a real Claude Desktop on Mac or Windows, or with a real key. Try one image first, and open an [issue](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/issues) if something fails.

### What it adds to Claude
After installing, tell Claude what you want, for example "generate a square image of…" or "edit this image and make the background white". Claude then uses these tools:

| Tool | What it does | Approximate cost on your key |
|---|---|---|
| `generate_image` | Images from a text description: 1K, 2K or 4K, any aspect ratio, 1 to 4 images | $0.04 per 1K image |
| `edit_image` | Edit an image from your computer with written instructions: change the background, re-render, change one part. The original is never modified | Same as generating |
| `generate_video` | A 3 to 10 second clip, landscape 16:9 or vertical 9:16, from a description or a starting image | $0.10 per second |
| `get_job` | Follow a video job until it is finished and saved | Free |
| `usage` | What you spent this month against the cap you set | Free |

### What you need
- The **Claude Desktop** app on Mac or Windows, up to date. The extension does not work in the browser or on mobile.
- A **Gemini API key** from Google AI Studio: <https://aistudio.google.com/apikey>. It must belong to a project with billing enabled; image and video generation have no free tier.
- Nothing else. No Node.js, no commands.

### Install
1. Download [gemini-media-1.0.0.mcpb](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/gemini-media/gemini-media-1.0.0.mcpb).
2. **Double-click** it. Claude Desktop opens an install window; click **Install**.
   - If nothing opens: in Claude Desktop go to **Settings → Extensions → Advanced settings → Install Extension…** and choose the file.
3. Fill in the three fields:

   | Field | What to enter |
   |---|---|
   | **Gemini API key** | Paste your key |
   | **Save files to** | The folder where results are saved (default `Documents/Gemini Media`) |
   | **Monthly spending cap (USD)** | The most you allow per month (default 30) |

4. Save the settings and make sure the extension is **enabled**.
5. Open a new chat and type: "Generate a square image of a white security camera on a grey background." Allow the tool, and find the image in the folder you chose.

### If it does not work
| Problem | Fix |
|---|---|
| Nothing happens when you open the file | Use the Settings route in step 2, and make sure Claude Desktop is up to date |
| The tools do not appear in the chat | Quit Claude Desktop and open it again |
| Mac shows a security warning | System Settings → Privacy & Security, then allow |
| There is no Extensions page, or the install is refused | Your account is in an organization (Team or Enterprise) that restricts extensions. Ask the organization owner to allow it |
| Google rejects the key | Check that it was copied in full and that its project has billing enabled |

### Privacy and security
- **Your key** is kept by Claude Desktop in the operating system's secure storage (Keychain on Mac, Credential Manager on Windows). The extension sends it only to Google and never writes it to a file or a log.
- **No server in the middle.** The only connection is to `generativelanguage.googleapis.com`. No telemetry.
- **Prompts, and images you ask to edit, are sent to Google.** Do not send client data or personal data.
- **Reading files:** the extension reads only a file with an image extension, up to 8 MB, whose content really is JPEG, PNG or WebP. Anything else is refused before any connection is made.
- **Writing files:** only in the output folder, under new names, never over an existing file.
- **The monthly cap** is enforced on your computer. Set it to 0 to block all spending. Google's invoice is authoritative; the extension's figures are estimates.
- **The extension is not code-signed**, so Claude may show a warning when you install it. The full code is in [source/](source/) for anyone who wants to review it or build the file themselves, and the security review is in [reviews/11-gemini-media.md](../reviews/11-gemini-media.md).

### Change settings or remove
| I want to | Do this |
|---|---|
| Change the key, the folder or the monthly cap | Settings → Extensions → Gemini Images & Video → Configure |
| Stop spending at once | Set the monthly cap to 0 |
| Disable or remove the extension | Settings → Extensions: switch it off or click Uninstall. Saved files stay |

### Prices
The figures above are approximate, as we found them for Google's pricing page on 2026-11-12. Check the page for current prices: [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing). Models used: `gemini-nano-banana-2.1` for images and `gemini-omni-1.1-flash` for video. Video is 720p; higher resolutions are disabled because Google has not published a per-second price for them.

### For developers: build from source
Run `npm ci`, `npm run build` and `npm test` inside `gemini-media/source`. The build bundles the server into one file, validates `manifest.json` with Anthropic's official packer and writes `gemini-media-<version>.mcpb`. The test unpacks the packed file the way Claude Desktop does and drives it with the official MCP client.
