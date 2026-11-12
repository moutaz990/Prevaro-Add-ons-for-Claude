# البلغنز
| البلغن | المتجر | الإصدار / sha | المرحلة | المراجعة |
|---|---|---|---|---|
| remotion | anthropic-plugin-directory (رسمي) | 4.0.528 / `b54a19c` | 2 | reviews/02-remotion.md |
| auto-handoff | prevaro-addons (هذا المستودع: `.claude-plugin/marketplace.json`) | 0.8.6 / `8d762ce` | 3 | reviews/03-auto-handoff.md |

- المتجر الخاص `prevaro-addons` يُضاف بالأمر `claude plugin marketplace add <مسار المستودع>`، ويشير إلى sha مراجَع لا إلى فرع.
- إعداد auto-handoff: `{"viewer":"off"}` عبر `claude plugin configure auto-handoff@prevaro-addons --values-stdin`.
- الإزالة: `claude plugin uninstall <id>` ثم `claude plugin marketplace remove prevaro-addons`.
