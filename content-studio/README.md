# Content Studio — استوديو المحتوى لـClaude

**العربية** | [English](#english)

بلغن يجعل Claude مسؤول محتوى لوسائل التواصل، لأي شركة أو علامة: يخطط، يصمم صورة المنشور النهائية بشعارك وخطك، يسلّمك كل منشور للاعتماد، ويعطيك كل صباح تقريراً عن حساباتك ومنافسيك.

**القاعدة: Claude يُعدّ وأنت تعتمد.** لا يُنشر شيء ولا يُجدول ولا يُصرف مال إلا بعد «نعم» منك على ذلك الشيء بعينه.

| الملف | ما هو |
|---|---|
| [content-studio-0.2.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/content-studio-0.2.0.plugin) | البلغن نفسه: 7 مهارات، بلا أي ربط |
| [connect-typefully-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/connect-typefully-0.1.0.plugin) | ربط Typefully بمفتاح API (اختياري) |
| [connect-buffer-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/connect-buffer-0.1.0.plugin) | ربط Buffer بمفتاح API (اختياري) |
| [connect-metricool-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/connect-metricool-0.1.0.plugin) | ربط Metricool بتسجيل الدخول (اختياري) |

> **الحالة:** السكربتات مختبَرة آلياً على Linux (تركيب الصورة بعلامتين تجريبيتين، التقويم، أرقام التقرير)، وكل البلغنز تجتاز فحص `claude plugin validate`، وتثبيت إضافة الربط مع إدخال المفتاح جُرّب في Claude Code. لم يُجرَّب شيء بعد داخل Claude Desktop حقيقي، ولا مع مفاتيح أو حسابات حقيقية في الأدوات الثلاث. أخبرنا في [Issues](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/issues) إن واجهت مشكلة.

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

## أداة الجدولة: أيها تختار؟

البلغن يعمل بلا أي أداة: يجهّز لك مجلداً فيه الصورة والنص لكل منصة وترفعها بيدك. إن أردت أن يضع Claude المنشورات المعتمدة في أداة جدولة، فاختر واحدة وثبّت إضافتها فقط.

### مقارنة الباقات المجانية
فُحصت في 13 نوفمبر 2026، ومعظمها من مواقع مقارنة لا من صفحات الأسعار نفسها. الباقات تتغير كثيراً: راجع صفحة التسعير عند كل أداة قبل الاعتماد على أي رقم.

| | Typefully | Buffer | Metricool |
|---|---|---|---|
| باقة مجانية | نعم | نعم | نعم |
| عدد المنشورات مجاناً | 10 في الشهر | 10 مجدولة لكل قناة في الوقت نفسه، وتتجدد كلما نُشر واحد | 20 في الشهر لكل القنوات معاً |
| عدد الحسابات مجاناً | مجموعة حسابات واحدة | 3 قنوات | علامة واحدة |
| X | نعم | نعم | ليس في المجاني |
| لينكدإن | نعم | نعم | ليس في المجاني |
| فيسبوك، إنستغرام، تيك توك، يوتيوب | لا | نعم | نعم |
| طريقة ربط Claude | مفتاح API، أو تسجيل دخول | مفتاح API، أو تسجيل دخول | تسجيل دخول فقط (مفتاحه في الباقة المدفوعة) |
| ميزة إضافية | — | — | أرقام 5 حسابات منافسة |

**كيف تختار:**
- **أغلب نشرك على X ولينكدإن، ومنشورات قليلة في الشهر:** Typefully.
- **فيسبوك أو إنستغرام أو تيك توك أو يوتيوب، ونشر متكرر:** Buffer. حدّه المجاني على الطابور لا على الشهر.
- **تريد أرقام المنافسين في تقرير الصباح:** أضف Metricool للقراءة، حتى لو نشرت بأداة أخرى.
- يمكن الجمع بينها: Buffer للنشر و Metricool للأرقام مثلاً.

### كيف تربط كل أداة

| الأداة | ما تدخله | من أين تحصل عليه |
|---|---|---|
| Typefully | مفتاح API | إعدادات حسابك في Typefully، قسم API |
| Buffer | مفتاح API | إعدادات حسابك في Buffer ← API ← «personal API key». ينشئه مالك الحساب |
| Metricool | لا شيء: تسجّل الدخول في صفحة Metricool | — |

**في Claude Code** (مثال Buffer، ومثله البقية):
```
/plugin marketplace add moutaz990/Prevaro-Add-ons-for-Claude
/plugin install connect-buffer@prevaro-addons
```
يسألك Claude عن المفتاح مرة واحدة ويحفظه في التخزين الآمن لنظامك. لتغييره لاحقاً: `/plugin configure connect-buffer@prevaro-addons`. ولـMetricool: بعد التثبيت شغّل `/mcp` واختر metricool ثم Authenticate.

**في تطبيق Claude للكمبيوتر أو المتصفح:** الأسهل صفحة الموصلات في التطبيق نفسه. أضف الأداة هناك وسجّل الدخول في صفحتها. العناوين: `https://mcp.typefully.com/mcp` و`https://mcp.buffer.com/mcp` و`https://ai.metricool.com/mcp`، و Metricool موجود أيضاً في دليل الموصلات داخل التطبيق.

### عن المفاتيح وكلمات السر
- مفتاح API تصدره الأداة لهذا الغرض بالذات، وتلغيه من عندها متى شئت. عامله ككلمة سر: من يملكه ينشر من حساباتك. لا تلصقه في محادثة.
- البلغن لا يطلب أسماء المستخدمين ولا كلمات السر ولا رموز التحقق لحساباتك في وسائل التواصل. أنت تربط حساباتك داخل أداة الجدولة، في موقعها.
- لماذا أداة جدولة لا ربط مباشر بكل منصة؟ النشر عبر واجهات المنصات نفسها يحتاج موافقة كل منصة على التطبيق (صفحات لينكدإن، النشر العام في تيك توك) أو يُدفع بالاستخدام (X). أدوات الجدولة حاصلة على هذه الموافقات.
- إضافات الربط لا تحوي كوداً: كل واحدة ملفان يقولان لـClaude أين خادم الأداة وأي مفتاح يرسل. الأدوات التي تظهر لك هي أدوات الشركة صاحبة الخدمة.

**توليد الصور والفيديو:** عبر إضافة [Gemini Images & Video](../gemini-media) من هذا المستودع، بمفتاحك من Google.

## التثبيت

**تطبيق Claude Desktop (Cowork)، على Mac أو Windows:**
1. نزّل الملف [content-studio-0.2.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/content-studio-0.2.0.plugin).
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

- قراءة حسابات المنافسين تعتمد على ما تعرضه الصفحات العامة، أو على أداة أرقام مربوطة، أو على متصفح أنت مسجل فيه. ما لم يُقرأ يُذكر في أول التقرير، ولا يُقدَّر أي رقم.
- التقرير اليومي للقراءة فقط: لا إعجاب ولا متابعة ولا تعليق ولا رسائل ولا إعلانات.
- المحاور والوتيرة في القالب نقطة بداية تتفق عليها، لا نصيحة جاهزة.
- أنت المسؤول عن الالتزام بشروط كل منصة وكل أداة تربطها.

---

## English

A plugin that makes Claude your social media content lead, for any company or brand: it plans, composes the final post image with your logo and font, hands each post over for approval, and gives you a morning report on your accounts and competitors.

**The rule: Claude prepares, you approve.** Nothing is published, scheduled or paid for until you say yes to that specific thing.

| File | What it is |
|---|---|
| [content-studio-0.2.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/content-studio-0.2.0.plugin) | The plugin itself: 7 skills, no connections |
| [connect-typefully-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/connect-typefully-0.1.0.plugin) | Typefully connection with an API key (optional) |
| [connect-buffer-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/connect-buffer-0.1.0.plugin) | Buffer connection with an API key (optional) |
| [connect-metricool-0.1.0.plugin](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/raw/main/content-studio/connect-metricool-0.1.0.plugin) | Metricool connection by sign-in (optional) |

> **Status:** the scripts are tested automatically on Linux (image composition with two demo brands, the calendar, the report figures), every plugin passes `claude plugin validate`, and installing a connector add-on with a key was tried in Claude Code. Nothing has yet been tried inside a real Claude Desktop install, or with real keys or accounts in the three tools. Please report problems in [Issues](https://github.com/moutaz990/Prevaro-Add-ons-for-Claude/issues).

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

### Which scheduler?

The plugin works with no tool at all: it prepares a folder with the image and caption per platform for you to upload by hand. If you want Claude to place approved posts in a scheduling tool, pick one and install only its add-on.

**Free plans compared.** Checked on 13 November 2026, mostly from comparison sites rather than the vendors' own pricing pages. Plans change often: read each vendor's pricing page before relying on a number.

| | Typefully | Buffer | Metricool |
|---|---|---|---|
| Free plan | Yes | Yes | Yes |
| Posts on the free plan | 10 a month | 10 scheduled per channel at a time; the queue refills as posts go out | 20 a month across all channels |
| Accounts on the free plan | 1 social set | 3 channels | 1 brand |
| X | Yes | Yes | Not on the free plan |
| LinkedIn | Yes | Yes | Not on the free plan |
| Facebook, Instagram, TikTok, YouTube | No | Yes | Yes |
| How Claude connects | API key, or sign-in | API key, or sign-in | Sign-in only (its API token needs a paid plan) |
| Extra | — | — | Figures for 5 competitor accounts |

- **Mostly X and LinkedIn, a few posts a month:** Typefully.
- **Facebook, Instagram, TikTok or YouTube, posting often:** Buffer. Its free limit is on the queue, not on the month.
- **You want competitor figures in the morning report:** add Metricool for reading, even if you post with another tool.

**How to connect each one**

| Tool | What you enter | Where it comes from |
|---|---|---|
| Typefully | An API key | Typefully account settings, API section |
| Buffer | An API key | Buffer account settings → API → "personal API key". The account owner creates it |
| Metricool | Nothing: you sign in on Metricool's page | — |

In Claude Code (Buffer shown; the others are the same):
```
/plugin marketplace add moutaz990/Prevaro-Add-ons-for-Claude
/plugin install connect-buffer@prevaro-addons
```
Claude asks for the key once and keeps it in your system's secure storage. Change it later with `/plugin configure connect-buffer@prevaro-addons`. For Metricool, after installing run `/mcp`, choose metricool, then Authenticate.

In the Claude desktop or web app, the simplest way is the app's own connectors page: add the tool there and sign in on its page. Addresses: `https://mcp.typefully.com/mcp`, `https://mcp.buffer.com/mcp`, `https://ai.metricool.com/mcp`. Metricool is also in the app's connector directory.

**Keys and passwords**
- An API key is issued by the tool for exactly this purpose, and you can revoke it there at any time. Treat it like a password: its holder can post from your accounts. Never paste it into a chat.
- The plugin never asks for your social media usernames, passwords or login codes. You connect your social accounts inside the scheduler, on its website.
- Why a scheduler rather than a direct link to each platform: posting through the platforms' own APIs needs each platform's approval of the app (LinkedIn pages, public TikTok posting) or is paid per use (X). Scheduling tools already hold those approvals.
- The connector add-ons contain no code: each is two files telling Claude where the tool's server is and which key to send. The tools you see are the vendor's own.

**Image and video generation:** through the [Gemini Images & Video](../gemini-media) extension in this repository, with your own Google key.

### Install

**Claude Desktop (Cowork), Mac or Windows:** download `content-studio-0.2.0.plugin` above, then upload it in the app's plugins section (Customize → Plugins) or drop it into a Cowork chat and accept it. Menu names may differ between app versions. Choose a working folder and say "set up my brand".

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

- Reading competitor accounts depends on what public pages show, on a connected figures tool, or on a browser you are logged in to. Whatever could not be read is listed at the top of the report; no number is ever estimated.
- The daily report is read-only: no likes, follows, comments, messages or ads.
- The pillars and pace in the template are a starting point to agree, not ready-made advice.
- You are responsible for following the terms of each platform and each tool you connect.
