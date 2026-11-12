# مراجعة: heygen-com/hyperframes
- **المصدر:** https://github.com/heygen-com/hyperframes، رخصة Apache-2.0.
- **الإصدار:** tag `v0.8.206` = commit `85fdc9aa888b4d26c8150fd09acae7b23fb392f5` (2026-10-26)، ومعه حزمة npm `hyperframes@0.8.206`. الإصدار 0.9.29 صدر يوم المراجعة فلم يُعتمد.
- **ما يُثبَّت:** مهارتا `hyperframes` و `hyperframes-cli` فقط، مع CLI عام من npm. باقي مهارات المستودع (figma، reverse-any-video، إلخ) لم تُثبَّت.
- **lifecycle scripts في npm:** لا يوجد.
- **hooks:** لا يوجد في المهارتين. يوجد `.codex/hooks.json` في المستودع، لكنه خاص بـ Codex ولم يُنسخ.
- **ملاحظات أمنية:**
  1. **Telemetry:** المهارتان تطلبان تشغيل `npx hyperframes events` ("usage beacon")، والـ CLI يرسل telemetry افتراضياً. → عطّلناه بـ `HYPERFRAMES_NO_TELEMETRY=1` في settings.json وفي بيئة المستخدم.
  2. **تثبيت مهارات تلقائي:** `hyperframes init` يثبّت مهارات ناقصة تلقائياً. → عطّلناه بـ `HYPERFRAMES_SKIP_SKILLS=1`.
  3. **`scripts/locate.mjs`** يرسل صورة إطار إلى Gemini API (`generativelanguage.googleapis.com`) إن وُجد متغير البيئة `GEMINI_API_KEY`. → لا تضع مفتاح Gemini بهذا الاسم في بيئة النظام إن كانت ملفاتك سرية.
  4. أوامر `publish` و `cloud render` ترفع المشروع إلى خوادم HeyGen، ولا تعمل إلا بطلب صريح وتسجيل دخول.
- **التحقق هنا:** فيديو 5 ث، 1920×1080، h264، 30fps، بمربع شعار بديل. صُيِّر بـ 0.8.206 (مشروع `verify/video-test`). GSAP مأخوذ من npm (`gsap@3.15.0`) لا من CDN.
- **القرار:** مقبول مع الضوابط أعلاه.
