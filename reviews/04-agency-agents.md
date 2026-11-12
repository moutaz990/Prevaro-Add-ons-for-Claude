# مراجعة: msitarzewski/agency-agents (9 وكلاء)
- **المصدر:** https://github.com/msitarzewski/agency-agents @ `8ae6164602c95ca78828b148b9052460ee426885` (2026-11-08).
- **الطريقة:** استنساخ إلى مجلد مؤقت **دون تشغيل install.sh**، وقراءة كل ملف. ثم نسخ الملفات المختارة مع سطر المصدر والـ commit في رأس كل ملف.
- **التعديلات:**
  - `name` حُوّل إلى slug صغير، لأن Claude Code يعتمده معرّفاً.
  - حُذفت حقول `emoji` و`vibe` و`color` غير القياسية.
  - **نص التعليمات لم يتغير.**

| الملف | الدور | الأدوات |
|---|---|---|
| frontend-developer | واجهات React/Vue، أداء، وصول | يرث الكل |
| backend-architect | أنظمة، قواعد بيانات، API | يرث الكل |
| code-reviewer | مراجعة صحة وأمان | يرث الكل |
| network-engineer | Cisco/Juniper/PAN-OS، يفرض rollback | يرث الكل |
| ui-designer | أنظمة تصميم | يرث الكل |
| ux-architect | هيكلة UX و CSS | يرث الكل |
| brand-guardian | هوية العلامة | يرث الكل |
| content-creator | محتوى متعدد المنصات | WebFetch, WebSearch, Read, Write, Edit |
| ai-generated-code-auditor | أمن الكود المولّد | يرث الكل |

**لم تُضمَّن:**
- **pricing-analyst:** يحتوي جدول صلاحيات خصم واقتراح تقسيط دفعات، وهذه سياسة تخص كل شركة.
- **proposal-strategist:** يشترط دراسات حالة وعملاء سابقين في كل ادعاء، مما يدفع لادعاءات غير موثقة إن لم يكن لديك ملف خبرات.
- **linkedin-content-creator:** يطلب أرقاماً وأسماء عملاء في كل منشور.

يمكنك إضافتها يدوياً من المصدر بعد قراءتها.
