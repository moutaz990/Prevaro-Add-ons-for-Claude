# Prevaro Add-ons for Claude

**العربية** | [English](#english)

إضافات جاهزة لـ **Claude Code** تجعله أقوى في تصميم المواقع، والفيديو، وقراءة مخططات CAD، ومراجعة الكود، والجلسات الطويلة.
- **مراجعة:** كل مكوّن مراجَع أمنياً ومثبّت على إصدار محدد.
- **تثبيت وإزالة:** أمر واحد لكل منهما.
- **الفوائد بالتفصيل:** [GUIDE.md](GUIDE.md).

## المحتوى
| المجال | ما يضيفه |
|---|---|
| تصميم مواقع | 7 مهارات + Playwright (Claude يفتح الصفحة ويلتقط صوراً ويصحح) |
| رسومات وهوية | ملصقات، ثيمات، رسوم خطية تفاعلية |
| فيديو | HyperFrames و Remotion: فيديو موشن بالكود إلى MP4 |
| مخططات CAD | خادم `cad`: فتح DWG/DXF، استعلام، قياس، تعديل، تصدير DXF |
| وكلاء متخصصون (9) | واجهات، backend، مراجعة كود، أمن الكود المولّد، شبكات، UI، UX، هوية، محتوى |
| جلسات طويلة | auto-handoff: ملخص تلقائي وجلسة نظيفة دون فقدان السياق |
| بحث (اختياري) | Firecrawl و Perplexity بمفتاحك المدفوع |

## التثبيت
**المتطلبات:**
| البرنامج | Windows | macOS |
|---|---|---|
| Claude Code 2.1.275+ | `irm https://claude.ai/install.ps1 \| iex` | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Node.js 22+ | `winget install OpenJS.NodeJS.LTS` | `brew install node@22` |
| Git 2.25+ | `winget install Git.Git` | `xcode-select --install` |
| ffmpeg (اختياري، للفيديو) | `winget install Gyan.FFmpeg` | `brew install ffmpeg` |
| Chrome أو Edge (موصى به) | Edge موجود في Windows | أي منهما |

السكربت يفحص كل ذلك أولاً، ولا يغيّر شيئاً إن نقص المطلوب.

**Windows (PowerShell):**
```powershell
git clone https://github.com/moutaz990/Prevaro-Add-ons-for-Clude.git "$HOME\prevaro-addons"; powershell -ExecutionPolicy Bypass -File "$HOME\prevaro-addons\install\install.ps1"
```
**macOS / Linux (Terminal):**
```bash
git clone https://github.com/moutaz990/Prevaro-Add-ons-for-Clude.git ~/prevaro-addons && bash ~/prevaro-addons/install/install.sh
```

- **في أول مرة على Windows:** ابدأ بإضافة `-CheckOnly` (`--check-only` على الماك). يفحص فقط دون أي تغيير.
- **أسئلة المفاتيح:** اختيارية، واضغط Enter للتخطي. مفتاح Perplexity يتطلب شحن رصيد مسبق.
- **بعد الانتهاء:** افتح Terminal جديداً واكتب `claude`.
- **لا تحذف ولا تنقل مجلد `prevaro-addons` بعد التثبيت:** بلغن auto-handoff يُقرأ منه.

## التحديث والإزالة
```powershell
cd "$HOME\prevaro-addons"; git pull; powershell -ExecutionPolicy Bypass -File .\install\install.ps1
```
```powershell
powershell -ExecutionPolicy Bypass -File "$HOME\prevaro-addons\install\uninstall.ps1"
```
على الماك:
```bash
cd ~/prevaro-addons && git pull && bash install/install.sh
```
```bash
bash ~/prevaro-addons/install/uninstall.sh
```

- الإزالة تحذف كل ما أُضيف وتعيد `settings.json` كما كان.
- النسخ الاحتياطية تبقى في مجلد `prevaro-claude-setup/backups`.

## أين تعمل؟
| المكان | المهارات | الوكلاء والبلغنز وخوادم MCP |
|---|---|---|
| Claude Code: Terminal، أو قسم Code في تطبيق Claude للكمبيوتر، أو VS Code | ✅ تلقائياً | ✅ |
| Claude Chat (claude.ai، الجوال) | ✅ برفع ZIP يدوي ([GUIDE.md](GUIDE.md#chat)) | ❌ |

## الأمان
- **الإصدارات:** ثابتة، وحزم npm المختارة عمرها 14 يوماً على الأقل (باستثناء موثق واحد).
- **سكربتات التثبيت الخارجية:** لا تُشغَّل.
- **الخصوصية:** telemetry معطّل، ولا خوادم مكشوفة على الشبكة.
- **المراجعات الأمنية:** في [reviews/](reviews/)، والمصادر والإصدارات في [manifest.json](manifest.json).
- **المفاتيح:** تبقى في متغيرات بيئة جهازك فقط، ولا شيء منها في هذا المستودع.
- **رخص المكوّنات:** لكل مكوّن رخصته، ومنها:
  - **Remotion:** مجاني حتى 3 موظفين، وما فوق ذلك Company License.
  - **محرك DWG في خادم cad:** برخصة GPL-3.0.

## خطط قادمة
- بلغن Gemini (بعد نشره على Cloudflare). سيُضاف إلى `.claude-plugin/marketplace.json` بعد مراجعته بنفس الطريقة.

---

<a id="english"></a>
## English

Ready-made add-ons for **Claude Code**. Each component is security-reviewed and version-pinned. One command installs everything, and one command removes it. Benefits in detail: [GUIDE.md](GUIDE.md).

**Includes:**
- 12 skills: web design, graphics, video and MCP building.
- 9 specialist subagents.
- Remotion and auto-handoff plugins.
- MCP servers: Playwright, a local DWG/DXF `cad` server, and optional Firecrawl/Perplexity.

**Requirements:** Claude Code 2.1.275+, Node.js 22+, Git 2.25+. ffmpeg is optional (video), and Chrome/Edge is recommended.

**Install:**
- Windows:
  ```powershell
  git clone https://github.com/moutaz990/Prevaro-Add-ons-for-Clude.git "$HOME\prevaro-addons"; powershell -ExecutionPolicy Bypass -File "$HOME\prevaro-addons\install\install.ps1"
  ```
- macOS/Linux:
  ```bash
  git clone https://github.com/moutaz990/Prevaro-Add-ons-for-Clude.git ~/prevaro-addons && bash ~/prevaro-addons/install/install.sh
  ```
- Add `-CheckOnly` / `--check-only` for a dry run.
- Keep the `prevaro-addons` folder after installing: the auto-handoff plugin is read from it.

**Update:** run `git pull`, then run the installer again.

**Uninstall:** run `install/uninstall.ps1` (Windows) or `install/uninstall.sh` (macOS/Linux). It removes everything recorded in the install ledger and restores your previous `settings.json`.

**Where it works:** everything works in Claude Code (terminal, desktop Code tab, IDE). Skills can also be uploaded to Claude chat as ZIP files. Agents, plugins and MCP servers are Claude Code only.
