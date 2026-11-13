---
name: post-composer
description: >
  This skill should be used when the user asks to "make the final post image", "add the headline and logo
  to this picture", "make a quote card", "resize this post for stories", "ركّب المنشور", "أضف العنوان والشعار
  على الصورة", or when a generated picture needs its text and logo before publishing. It composes a picture
  without text, a headline in the brand font and the official logo into exact-size PNGs for square, 4:5,
  story 9:16 and landscape 16:9. Not for generating the picture itself and not for video.
metadata:
  version: "0.1.0"
---

# Post composer

Image models misspell text, especially Arabic, and cannot draw a real logo. So the picture is generated with no text, and this skill adds the headline and the logo afterwards with a script, the same way every time. The output is a draft for the owner; nothing is published.

## Inputs

- **Headline** (required), an optional second line, and an optional small label above the headline. Use the owner's approved wording, or mark the result as a draft.
- **Picture** (optional): no text and no logo inside it. An AI-generated image, or a real photo with confirmed rights.
- **Brand profile** `content-studio/brand.json`. If it is missing, use the brand-setup skill first.

## Layouts

| `--layout` | Look | When |
|---|---|---|
| `photo` | Picture fills the post; text over a scrim in the brand colour (bottom, or the reading-start side in landscape) | A strong picture with a calm area for text |
| `split` | Picture in one half; text and logo on a brand-colour panel | A busy picture, a longer headline, or a light brand colour |
| `card` | No picture: brand-colour background, large headline, logo | Introductions, tips, quotes, announcements |

Default: `photo` with a picture, else `card`.

## Sizes

| `--sizes` | Pixels | Use |
|---|---|---|
| `square` | 1080 × 1080 | Square post, all platforms |
| `portrait` | 1080 × 1350 | 4:5 post (Instagram, Facebook, LinkedIn) |
| `story` | 1080 × 1920 | Stories, Reels, Shorts. Top 250 px and bottom 340 px stay clear |
| `landscape` | 1920 × 1080 | 16:9 post (X, LinkedIn, YouTube) |

Each size is composed on its own, never cropped from another.

## Run

```
python scripts/build_post.py --brand content-studio/brand.json \
    --headline "Three questions before you buy" --sub "What to ask before you sign" --label "Weekly tip" \
    --image <picture path> --layout photo --sizes square,story --slug three-questions --out content-studio/deliver
```

- `--lang ar` or `--lang en` sets the text direction and the logo version. Default: `language` in brand.json.
- `--real-photo` for a real photo with confirmed rights: the "Illustrative image" tag is left out. Without it the tag is always added to a picture.
- Output: `<brand>_post_<slug>_<size>_<date>.png` per size, plus a `.json` record of the text, layout and checks.
- Needs Python 3 and a local Chrome, Chromium or Edge. Where commands cannot run on a computer with a browser, say so; do not imitate the result another way.

## What the script refuses (nothing is delivered)

- The brand font did not load, or its bold weight is missing.
- A character the font cannot draw: an emoji, an arrow, or Latin words with an Arabic-only font file. The script names the characters.
- The text does not fit even at the smallest allowed size. Shorten the headline; the script shrinks it within limits and never cuts a word.
- A banned word from brand.json, or a placeholder such as `[TBC]` left in the text.
- Colours without readable contrast, a missing logo file, a file that is not an image.
- If one size fails, no size is delivered.

Treat a refusal as information: fix the cause it names. Never bypass it.

## Rules

- The logo is the owner's file, used as it is. Never redraw it or ask a model for it.
- No text inside the generated picture. If a picture arrives with letters or a logo in it, reject it and regenerate without text.
- A generated picture is illustrative. Never present it as a real project, product or customer site; keep the tag.
- No customer names, personal data, prices or unverified claims in the text.
- Never publish or schedule from this skill.

## Steps

1. Take the wording, pillar and platform from the approved calendar row when there is one.
2. Pick the layout for the picture and the sizes for the platform.
3. Run the script. On a refusal, fix the cause.
4. Look at every output: the text is readable on its background, nothing important sits under the text or the logo, the story keeps its clear zones. With mixed right-to-left and left-to-right text, check the word order on the line and reword if it reads badly.
5. Give the owner the file paths and say it is a draft awaiting approval.
