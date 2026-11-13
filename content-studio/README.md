# Content Studio — استوديو المحتوى لـClaude

**العربية** | [English](#english)

بلغن يجعل Claude مسؤول محتوى لوسائل التواصل، لأي شركة أو علامة: يخطط، يصمم صورة المنشور النهائية بشعارك وخطك، يسلّمك كل منشور للاعتماد، ويعطيك كل صباح تقريراً عن حساباتك ومنافسيك.

**القاعدة: Claude يُعدّ وأنت تعتمد.** لا يُنشر شيء ولا يُجدول ولا يُصرف مال إلا بعد «نعم» منك على ذلك الشيء بعينه.

| | |
|---|---|
| **تنزيل البلغن** | [content-studio-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/content-studio-0.1.0.plugin) |
| **المصدر** | مجلد [`plugin/`](plugin) |

> **الحالة:** السكربتات مختبَرة آلياً على Linux (تركيب الصورة بعلامتين تجريبيتين، التقويم، أرقام التقرير)، والبلغن يجتاز فحص `claude plugin validate`. لم يُجرَّب بعد داخل Claude Desktop حقيقي ولا مع حسابات حقيقية. أخبرنا في [Issues](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/issues) إن واجهت مشكلة.

## ماذا يضيف إلى Claude؟

| المهارة | ماذا تفعل | اطلبها هكذا |
|---|---|---|
| `brand-setup` | تحفظ هويتك مرة واحدة: الاسم، الألوان، الخط، الشعار، الكلمات الممنوعة | «جهّز هويتي» |
| `content-lead` | تدير العمل كله: الأسئلة، مسح المنافسين، الاستراتيجية، خطة أسبوعين، ثم الإنتاج بثلاث بوابات اعتماد | «جهّز خطة محتوى للأسبوعين القادمين» |
| `content-calendar` | خطة المحتوى (المحاور وحصصها والوتيرة) وتقويم يُبنى ويُفحص بسكربت | «اعمل تقويم أسبوعين» |
| `gemini-visual-generation` | استخدام أدوات Gemini للصور والفيديو، مع عرض التكلفة قبل الصرف | «ولّد عيّنة لهذا المنشور» |
| `post-composer` | تضيف العنوان وشعارك الرسمي فوق الصورة، بمقاسات المنصات بالبكسل | «ركّب المنشور مربعاً وستوري» |
| `post-handover` | بطاقة التسليم، ثم مسودة في أداة الجدولة أو «حزمة نشر» | «سلّم المنشور» |
| `social-monitor` | تقرير الصباح: المنافسون، الترندات، حساباتك، أفكار الأسبوع | «موجز الصباح» |

### بوابات الاعتماد الثلاث
1. **بطاقة الفكرة:** مجانية، بضعة أسطر. تعتمد أو تعدّل.
2. **العيّنة:** صورة واحدة بسنتات. لا يُولَّد فيديو كعيّنة.
3. **النهائي:** بعد موافقتك على التكلفة المعروضة.

## كيف تُربط حساباتك؟ (بلا كلمات سر)

البلغن لا يطلب اسم مستخدم ولا كلمة سر ولا رمز تحقق، ولا يُحفظ شيء منها في المحادثة.

1. تربط حساباتك مرة واحدة داخل أداة جدولة (Typefully أو Buffer)، من موقعها.
2. في Claude تضغط **Connect** على موصل الأداة، فتنتقل إلى صفحتها وتسجّل الدخول هناك. التحقق بخطوتين يتم في تلك الصفحة.
3. بعدها Claude يضع المنشورات المعتمدة مسودات مجدولة في الأداة، ويقرأ أرقام منشوراتك منها.

لماذا أداة جدولة لا ربط مباشر بكل منصة؟ النشر عبر واجهات المنصات نفسها يحتاج موافقة كل منصة على التطبيق (صفحات لينكدإن، النشر العام في تيك توك) أو يُدفع بالاستخدام (X). أدوات الجدولة حاصلة على هذه الموافقات.

بلا أداة جدولة يعمل البلغن أيضاً: يجهّز لك مجلداً فيه الصورة والنص لكل منصة، وترفعها بيدك.

| الموصل | ماذا يغطي | ملاحظة |
|---|---|---|
| Typefully | X، لينكدإن، Threads، Bluesky، Mastodon | مضمّن، اختياري |
| Buffer | فيسبوك، إنستغرام، تيك توك، يوتيوب، لينكدإن، X وغيرها | مضمّن، اختياري. راجع ما تتيحه باقتك |
| Gemini Images & Video | توليد الصور والفيديو بمفتاحك | [إضافة منفصلة](../gemini-media) من هذا المستودع |

## التثبيت

**تطبيق Claude Desktop (Cowork)، على Mac أو Windows:**
1. نزّل الملف [content-studio-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/content-studio-0.1.0.plugin).
2. في التطبيق افتح قسم البلغنز (Customize ← Plugins) وارفع الملف، أو اسحبه إلى محادثة Cowork واقبله. أسماء القوائم قد تختلف حسب إصدار التطبيق.
3. اختر مجلد عمل، وقل: «جهّز هويتي».

**Claude Code:**
```
/plugin marketplace add moutaz990/Prevaro-Add-ons-for-Claude
/plugin install content-studio@prevaro-addons
```

## ماذا تحتاج؟

- ملف شعارك (النسخة التي تظهر جيداً على لون خلفيتك)، وألوانك، واسم خطك.
- لصورة المنشور النهائية: Python 3، ومتصفح Chrome أو Edge، وخط العلامة مثبتاً أو ملفاته. تعمل حيث يستطيع Claude تشغيل أوامر على جهازك.
- اختياري: حساب في أداة جدولة، وإضافة Gemini.

## ملفاتك

كلها في مجلد `content-studio/` داخل مجلد عملك، لا داخل البلغن: `brand.json` (الهوية)، `content-brief.md` (الهدف والجمهور والمنافسون)، `content-plan.json` (المحاور والوتيرة)، `calendar.csv`، `social-log.csv`، `deliver/` (الصور النهائية)، `publish/` (حزم النشر).

## حدود معروفة

- قراءة حسابات المنافسين تعتمد على ما تعرضه الصفحات العامة، أو على متصفح أنت مسجل فيه. ما لم يُقرأ يُذكر في أول التقرير، ولا يُقدَّر أي رقم.
- التقرير اليومي للقراءة فقط: لا إعجاب ولا متابعة ولا تعليق ولا رسائل ولا إعلانات.
- المحاور والوتيرة في القالب نقطة بداية تتفق عليها، لا نصيحة جاهزة.

---

## English

A plugin that makes Claude your social media content lead, for any company or brand: it plans, composes the final post image with your logo and font, hands each post over for approval, and gives you a morning report on your accounts and competitors.

**The rule: Claude prepares, you approve.** Nothing is published, scheduled or paid for until you say yes to that specific thing.

| | |
|---|---|
| **Download** | [content-studio-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/content-studio-0.1.0.plugin) |
| **Source** | the [`plugin/`](plugin) folder |

> **Status:** the scripts are tested automatically on Linux (image composition with two demo brands, the calendar, the report figures), and the plugin passes `claude plugin validate`. It has not yet been tried inside a real Claude Desktop install or with real accounts. Please report problems in [Issues](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/issues).

### What it adds

| Skill | What it does | Ask for it like this |
|---|---|---|
| `brand-setup` | Saves your brand once: name, colours, font, logo, banned words | "Set up my brand" |
| `content-lead` | Runs the whole job: questions, competitor scan, strategy, two-week plan, production through three approval gates | "Plan my content for the next two weeks" |
| `content-calendar` | The content plan (pillars, shares, pace) and a calendar built and checked by a script | "Make a two-week calendar" |
| `gemini-visual-generation` | Using the Gemini image and video tools, with the cost shown before spending | "Generate a sample for this post" |
| `post-composer` | Adds the headline and your official logo to a picture, at exact platform sizes | "Compose this post, square and story" |
| `post-handover` | Handover card, then a draft in your scheduler or a publish pack | "Hand over the post" |
| `social-monitor` | Morning report: competitors, trends, your accounts, ideas for the week | "Morning brief" |

The three approval gates: a free concept card, then one sample image for cents (never a video as a sample), then the final only after you accept the stated cost.

### Connecting your accounts (no passwords)

The plugin never asks for a username, a password or a login code, and none is kept in a chat.

1. Connect your accounts once inside a scheduling tool (Typefully or Buffer), on its website.
2. In Claude press **Connect** on that tool's connector; you sign in on the tool's own page. Two-step verification happens there.
3. Claude then places approved posts in the tool as scheduled drafts and reads your post figures from it.

Why a scheduler rather than a direct link to each platform: posting through the platforms' own APIs needs each platform's approval of the app (LinkedIn pages, public TikTok posting) or is paid per use (X). Scheduling tools already hold those approvals. Without a scheduler the plugin still works: it prepares a folder with the image and caption per platform for you to upload by hand.

| Connector | Covers | Note |
|---|---|---|
| Typefully | X, LinkedIn, Threads, Bluesky, Mastodon | Included, optional |
| Buffer | Facebook, Instagram, TikTok, YouTube, LinkedIn, X and more | Included, optional. Check what your plan offers |
| Gemini Images & Video | Image and video generation with your own key | [Separate extension](../gemini-media) in this repository |

### Install

**Claude Desktop (Cowork), Mac or Windows:** download the `.plugin` file above, then upload it in the app's plugins section (Customize → Plugins) or drop it into a Cowork chat and accept it. Menu names may differ between app versions. Choose a working folder and say "set up my brand".

**Claude Code:**
```
/plugin marketplace add moutaz990/Prevaro-Add-ons-for-Claude
/plugin install content-studio@prevaro-addons
```

### What you need

- Your logo file (the version that reads well on your background colour), your colours and your font's name.
- For the final post image: Python 3, Chrome or Edge, and the brand font installed or as files. It runs wherever Claude can run commands on your computer.
- Optional: a scheduling tool account, and the Gemini extension.

### Known limits

- Reading competitor accounts depends on what public pages show, or on a browser you are logged in to. Whatever could not be read is listed at the top of the report; no number is ever estimated.
- The daily report is read-only: no likes, follows, comments, messages or ads.
- The pillars and pace in the template are a starting point to agree, not ready-made advice.
