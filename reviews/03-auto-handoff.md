# مراجعة: alexknowshtml/claude-auto-handoff
- **المصدر:** https://github.com/alexknowshtml/claude-auto-handoff @ `8d762ce726c962268e2dbe24c1c60f0889a2fcde` (2026-10-04)، v0.8.6، رخصة MIT.
- **التثبيت:** كبلغن عبر متجر خاص داخل هذا المستودع (`.claude-plugin/marketplace.json`) يشير إلى الـ sha المراجَع (نوع source `url` + `sha`، كالمتجر الرسمي). `claude plugin validate` ✓.
- **hooks:** `hooks/hooks.json` = `{"modules": ["./register.tsx"]}`، أي mod من نوع function-hook. ما ينفّذه:
  1. يقيس حجم السياق بعد كل دور. عند 160k توكن يرفض أدوات جديدة، ثم يطلب من **Haiku** (عبر `$.model.complete`، أي Claude نفسه) كتابة ملخص من المحادثة.
  2. يكتب الملخص في `~/.claude/state/auto-handoff/<session>.md`، ثم صفحات HTML في `pages/`.
  3. ينفّذ `/clear` ويبدأ جلسة جديدة بسطر يشير إلى الملخص.
  4. **خادم عرض (viewer):** افتراضياً على عنوان Tailscale منفذ 3846 (`node -e` خادم http يخدم ملفات .html فقط)، وبدون Tailscale على 127.0.0.1. يُشغَّل بـ `sh -c ... setsid/nohup`.
  5. ينفّذ `tailscale ip -4` لمعرفة العنوان.
- **المخاطر والقرار:**
  - الملخصات قد تحوي بيانات عملاء، والخادم الافتراضي يعرضها على الشبكة (tailnet). → **ضبطنا `viewer=off`** (عنوان غير صالح = لا خادم). تحققنا في الكود: `parseAddress('off')` يعيد undefined، فلا يُشغَّل `launchServer`.
  - لا طلبات شبكة خارجية غير نموذج Claude.
  - يحتاج `sh` (Git Bash على Windows). بدونه يعمل الملخص ويتعطل الخادم فقط، وهو معطّل أصلاً.
  - `statusline/handoff-link.sh` لم يُفعَّل.
- **القرار:** مقبول مع `viewer=off`.

## المدمج في Claude Code 2.1.322 (تحققنا منه في الملف التنفيذي)
`/compact` · `/context` · `/clear` · `/resume` · `/rewind` (alias `/checkpoint`) · `/export` · `/memory` · الإعداد `autoCompactEnabled` · المتغيران `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` و `DISABLE_AUTO_COMPACT`.
- **تنبيه:** `DISABLE_AUTO_COMPACT` يعطّل auto-handoff أيضاً (من README البلغن)، فلم نضبطه.
- **`.claudeignore`:** غير مدعوم في هذا الإصدار، ولا أثر له في الملف التنفيذي. استخدمنا `permissions.deny` بدلاً منه.

## قرار 2026-11-12: مثبّت ومعطّل افتراضياً
فُحص كود البلغن (commit `8d762ce`):
- **لا وضع موافقة:** خياراته الستة (الحد، عدد التسليمات المتتالية، قالبا الملخص، ملفات مستثناة، عنوان العرض) ليس فيها وضع موافقة، وبعد كتابة الملخص ينفّذ `/clear` تلقائياً (`register.tsx:244`).
- **يقاطع المهمة الجارية:** عند تجاوز الحد يرفض الأدوات (`register.tsx:451-463`) ويكتب «Stopping this turn to hand off» (`:494`).
- **المعالجة:** يبقى مثبّتاً ومعطّلاً (`claude plugin disable`)، والمثبّتان يعطّلانه بعد كل تثبيت. حفظ السياق يدوي: `/compact` و`/resume` و`/rewind`.
- **للتفعيل (غير موصى به):** `claude plugin enable auto-handoff@prevaro-addons`.

