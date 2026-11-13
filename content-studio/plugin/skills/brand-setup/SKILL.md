---
name: brand-setup
description: >
  This skill should be used when the user asks to "set up my brand", "add my logo and colours",
  "change the brand colours", "جهّز هويتي", "أضف شعاري وألواني", or when another Content Studio skill
  reports that the brand profile (brand.json) is missing. It creates or updates the brand profile that
  the post composer reads: name, colours, font, logo files, banned words.
metadata:
  version: "0.1.0"
---

# Brand setup

Create or update `content-studio/brand.json` in the user's working folder. Every final post image is built from this file, so it must hold only what the owner confirmed. Talk to the user in their language.

## What to collect

Ask only for what is missing, in one message:

1. **Brand name** as it should appear in file names.
2. **Logo file** on their computer: the official version that reads well on the brand's background colour (for a dark background, the light or reversed logo). SVG is best; PNG, JPEG and WebP work. Optional: a separate logo per language, and the symbol alone.
3. **Colours** as hex codes: the background behind the text, the text colour, one accent colour.
4. **Font**: the brand font's name. Ask whether it is installed on the computer or whether they have the font files (regular and bold at least).
5. **Default language** of the posts.
6. **Banned words and claims**: anything that must never appear in a post.

## Rules

- Never redraw, recolour, trace or generate the logo. Use the file the owner gives, as it is. If they have no version for their background colour, say so and ask them for one.
- Never invent a colour or a font. If the owner does not know the hex codes, read them from a file they provide (brand guide, logo, website they point to), propose them, and wait for a yes.
- The font must cover every language they post in. An Arabic-only font file cannot draw Latin words, and the composer will refuse the post.
- No passwords, keys or personal data in the brand profile.

## Steps

1. Look for `content-studio/brand.json`. If it exists, show what it holds and ask what to change.
2. Otherwise copy `references/brand.template.json` to `content-studio/brand.json`, and copy the logo (and font files, if given) into `content-studio/`.
3. Fill the profile from the owner's answers. Remove template entries that do not apply (for example `logo.en`, `logo.mark`, `font.files`). Paths in the file are relative to the file's own folder.
4. Test it by composing one card with the post-composer script:
   `python <post-composer skill folder>/scripts/build_post.py --brand content-studio/brand.json --headline "<brand name>" --layout card --slug brand-test --out content-studio/deliver`
5. If the script refuses (contrast too low, font not found, a character the font cannot draw, logo not found), explain the reason in plain words and fix the profile with the owner. Do not work around a refusal.
6. Show the test card and ask the owner to confirm the logo, colours and font look right.

## If commands cannot run here

Write the profile anyway, say that it could not be tested in this chat, and tell the user the composer needs a computer with Chrome or Edge.
