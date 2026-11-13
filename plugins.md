# البلغنز
| البلغن | المتجر | الإصدار / sha | المرحلة | المراجعة |
|---|---|---|---|---|
| remotion | anthropic-plugin-directory (رسمي) | 4.0.528 / `b54a19c` | 2 | reviews/02-remotion.md |
| auto-handoff (**معطّل**) | prevaro-addons (هذا المستودع: `.claude-plugin/marketplace.json`) | 0.8.6 / `8d762ce` | 3 | reviews/03-auto-handoff.md |
| content-studio (**لا يُثبَّت تلقائياً**) | prevaro-addons (المصدر في هذا المستودع: `content-studio/plugin/`) | 0.1.0 | — | reviews/12-content-studio.md |

- `content-studio` مكتوب لهذا المستودع وليس من طرف ثالث. أمر التثبيت العام لا يثبّته؛ يثبّته من يريده بالأمر `/plugin install content-studio@prevaro-addons` أو بملف `.plugin`.
- المتجر الخاص `prevaro-addons` يُضاف بالأمر `claude plugin marketplace add <مسار المستودع>`، ويشير إلى sha مراجَع لا إلى فرع.
- إعداد auto-handoff: `{"viewer":"off"}` عبر `claude plugin configure auto-handoff@prevaro-addons --values-stdin`.
- الإزالة: `claude plugin uninstall <id>` ثم `claude plugin marketplace remove prevaro-addons`.
