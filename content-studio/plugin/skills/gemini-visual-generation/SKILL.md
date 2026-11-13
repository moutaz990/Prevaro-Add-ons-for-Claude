---
name: gemini-visual-generation
description: Generate and edit images and make short videos with the Gemini Images & Video extension (generate_image, edit_image, generate_video, get_job, usage). Use for any request for an image, a social post visual, a story, an X or LinkedIn cover, a background, an image edit or a short video, or a question about generation cost. Shows the estimated cost and waits for an explicit yes before any video or any request above one US dollar.
---

# Images and video with Gemini

This skill explains **how** to use the tools of the Gemini Images & Video extension well. The user pays Google from their own Gemini key, so treat every call as their money.

Reply in the user's language. Write the prompts you send to the tools in English.

## Three rules that are never broken
1. **No client data and no personal data.** Every prompt and every reference image is sent to Google. No client drawings or documents, no photos of client sites, no client names or logos, no faces of real people, no licence plates. If the request or a file looks like that, stop and say why.
2. **Cost before action.** Before **any** `generate_video`, and before any request or series of requests that adds up to more than **one US dollar**, show the estimated cost and what will be produced, and wait for an explicit "yes". Anything else is not consent.
3. **The result is a draft.** It is not published or sent to anyone until the user has looked at it and approved it. Say that it is AI-generated.

## Brand
If the user's organisation has a brand skill (colours, font, style, logo rules), use it before producing anything that carries the organisation's name, and apply it in the prompt. If there is none, ask for the colours and the style wanted. Do not invent a brand.

## Which tool
| Request | Tool | Notes |
|---|---|---|
| A new image from a description | `generate_image` | `size` defaults to 1K. `count` 1 to 4 (2 at most for 4K) |
| Edit an image: re-render, change the background, change one part | `edit_image` | Needs `image_paths`: full paths on the user's computer |
| A video clip | `generate_video`, then `get_job` | Always after "yes" |
| Follow a video job | `get_job` | Free |
| "How much did I spend?" / "How much does it cost?" | `usage` | Returns the current price list and the cap |

Results are **file paths** on the user's computer. Never pass an image as base64. To edit an image, ask the user for the **full path** of the file; the original is never changed. Before reading any file, confirm with the user that it is the intended image and that it is not client material, because it is sent to Google.

## Cost
Call `usage` once at the start of the conversation: `price_list_usd` has the prices in force and the remainder of the monthly cap. The figures below are only for explaining.

| Item | Estimate |
|---|---|
| 1K image | about $0.04 |
| 2K image | about $0.06 |
| 4K image | about $0.12 |
| 720p video | about $0.10 **per second** (5 s ≈ $0.50, 10 s ≈ $1.00) |

How to present it before a video or anything above one dollar:

> I will generate: a 6-second clip, 9:16, 720p.
> Estimated cost: $0.61. Left under your cap this month: $24.10.
> Type "yes" to go ahead.

- Start with 1K and one image. Raise the size or the count only when needed.
- A plan of several images that adds up to more than a dollar needs one "yes" for the whole plan before starting.
- After every result, state `estimated_cost_usd` and the `model`.
- If a tool refuses because of the monthly cap or the per-minute limit, pass the reason on as given. Do not retry and do not work around it. The user changes the cap in the extension's settings.

## Ready-made sizes
| Use | `aspect_ratio` | `size` | Final size in the design tool |
|---|---|---|---|
| Square post | `1:1` | 1K | 1080 × 1080 |
| Story / reel | `9:16` | 1K | 1080 × 1920. Keep the top and bottom (about 250 px) free of important elements |
| X header | `21:9` | 2K | 1500 × 500 (3:1): cropped at the top and bottom, so keep what matters in the middle band |
| LinkedIn personal cover | `4:1` | 2K | 1584 × 396 |
| LinkedIn company cover | `4:1` | 2K | 1128 × 191: cropped hard at the top and bottom, so ask for a simple horizontal composition in the centre |
| Landscape post / slide | `16:9` | 1K | 1920 × 1080 |
| Portrait post | `4:5` | 1K | 1080 × 1350 |

The final crop and the safe areas are set in the design tool. If a platform changes its sizes, follow the platform.

## No text inside the image
Image models get letters wrong, and Arabic worst of all: shapes, joining and direction.
- **Do not ask** for any text in the image or video: no Arabic, no organisation name, no numbers, no logos.
- Add to every prompt: `no text, no letters, no logos, no watermarks`.
- Ask for **calm empty space** for the text instead: `clean negative space on the right third for a headline`. In Arabic layouts the headline usually sits on the right.
- The text and the official logo are added afterwards in the design tool. A logo is never redrawn by generation.

## Writing a good image prompt
One paragraph, in English, in this order:
1. **Subject:** exactly what is in the picture, how many, what material.
2. **Place and context:** where, and what time of day.
3. **Composition:** camera angle, how close, where the main element sits, where the empty space is.
4. **Light:** its kind and direction.
5. **Style and colours:** from the brand skill if there is one, otherwise from what the user asked for. Name colours or give their codes.
6. **Exclusions:** `no text, no logos, no people`, and whatever else is not wanted.

Example:

> A photorealistic wide shot of a solar-powered surveillance tower with two cameras standing in an open desert site at golden hour, the tower placed on the left third, clean empty sky on the right two thirds for a headline, soft warm side light, calm and professional mood, muted colour palette, sharp detail, no text, no letters, no logos, no watermarks, no people.

- Be specific. "A camera on a 6 m galvanized steel pole" beats "security equipment".
- One image, one idea.
- Describe equipment generically. No brand names or model numbers; the model invents their details.
- A generated image is **illustrative**. Never present it as a photo of a finished project, a real product or a client site.

## Editing (`edit_image`)
- There is no mask. Say clearly **what changes and what stays**: `Replace only the background with a plain light grey studio backdrop. Keep the device, its angle, colours and proportions exactly the same.`
- One change at a time. Then use the returned `path` for the next change.
- Re-rendering: `Re-render the same scene at dusk with warm lights on. Keep the composition and all objects unchanged.`
- Several reference images: state the role of each in order: `Use the first image for the product and the second for the lighting style.`
- Leave `aspect_ratio` out to keep the proportions of the original.

## Writing a good video prompt
The clip is 3 to 10 seconds, so it is **one shot with one movement**:
1. **Subject and place**, as for an image.
2. **Motion:** what moves in the scene, slowly or fast.
3. **Camera:** one move only: `slow push-in`, `slow orbit to the right`, `static tripod shot`, `gentle aerial rise`.
4. **Light and mood.**
5. **Sound:** audio is always generated. Ask for `ambient sound only, no speech, no music` when it should be quiet.
6. **Exclusions:** `no text, no captions, no logos, no people`.

Example:

> A slow aerial push-in toward a solar-powered surveillance tower in an open desert site at sunrise, light dust drifting in the wind, the cameras slowly panning, warm low light, calm cinematic mood, ambient wind sound only, no speech, no music, no text, no captions, no logos, no people.

**The cheaper and safer way:** generate an image first (about $0.04), agree it with the user, then animate it with `start_image_path`. No video is paid for on a composition that was not approved.

**Video steps:**
1. Show the cost and wait for "yes".
2. Call `generate_video` **once**. It returns a `job_id` at once.
3. Call `get_job` about every 30 seconds until the status is `succeeded` or `failed`. It usually takes one to five minutes. **Do not leave the job unattended:** the video is only downloaded when `get_job` is called, and a video not collected within two hours is charged and lost.
4. **Do not call `generate_video` again** while waiting. Every call is a new clip at its own price.
5. Defaults: 5 seconds, 720p, `16:9`. Use `9:16` for stories. A higher resolution is refused when it has no configured price; do not insist.

## Handing over the result
- Give each `path` exactly as returned, and say which folder it is in.
- State the estimated cost and the model.
- Do not describe the picture as if you had seen it. You have not; ask the user to open the file and say what they think.

## When something fails
| Message | What to do |
|---|---|
| `monthly_cap` / `rate_limited` | Pass the reason to the user and stop |
| `no_key` | The key is not set. The user opens the extension's settings in Claude Desktop and pastes it |
| `no_image_returned` | Usually a safety refusal. Suggest another wording and ask before retrying, because the attempt may be charged |
| `image_not_usable` | The path is wrong, or the file is not a JPEG, PNG or WebP image, or it is larger than 8 MB |
| `resolution_not_priced` | Use 720p |
| `google_auth` / `google_forbidden` | Google refused the key (deleted, restricted, or its project has no billing) |
| Another Google error (`google_…`) | Pass the message on, and do not repeat the request more than once |
