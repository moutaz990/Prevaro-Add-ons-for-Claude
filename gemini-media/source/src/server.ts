// Claude Desktop extension: a local MCP server (stdio) that generates and edits images and
// generates video with Google Gemini, using the user's own API key.
//
// - The key comes from the extension settings (kept by Claude Desktop in the OS keychain) and is
//   sent only to Google, in the x-goog-api-key header.
// - Results are written to a folder on this computer. Nothing is uploaded anywhere else.
// - A monthly spending cap and a per-minute limit are enforced locally.
// - stdout carries the MCP protocol, so the only log line (time, tool, model, cost, outcome) goes
//   to stderr. Prompts, images and the key are never logged.
import { McpServer } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import { randomBytes } from "node:crypto";
import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { extname, isAbsolute, join } from "node:path";
import { z } from "zod";
import {
  GeminiClient,
  GeminiError,
  decodeBase64,
  describeGeminiError,
  encodeBase64,
  findMedia,
  imageCostUsd,
  summarizeUsage,
  videoCostUsd,
  type MediaInput,
} from "./gemini";
import { ConfigError, mergePricing, microsToUsd, usdToMicros, type Pricing } from "./pricing";
import { sniffImageMime } from "./sniff";
import { StateStore, type Job } from "./state";

export const VERSION = "1.0.0";
const GOOGLE_API = "https://generativelanguage.googleapis.com";
const DATA_WARNING =
  "تنبيه: لا ترسل بيانات عملاء أو بيانات شخصية؛ الأوصاف والصور تذهب إلى Google. (Warning: never send client data or personal data; prompts and images are sent to Google.)";

const IMAGE_SIZES = ["1K", "2K", "4K"] as const;
const ASPECT_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "4:1"] as const;
const VIDEO_ASPECTS = ["16:9", "9:16"] as const;
const VIDEO_RESOLUTIONS = ["360p", "720p", "1080p", "4k"] as const;
const MAX_IMAGES = 4;
const MAX_IMAGES_4K = 2;
const MAX_REFERENCES = 14;
const MAX_REFERENCE_TOTAL_BYTES = 14 * 1024 * 1024;
const MAX_VIDEO_BYTES = 200 * 1024 * 1024;
const VIDEO_JOB_TIMEOUT_SECONDS = 2 * 3600;
const REFERENCE_INPUT_COST_USD = 0.002;
const IMAGE_EXTENSIONS = new Set([".jpg", ".jpeg", ".png", ".webp"]);
const EXTENSION_FOR: Record<string, string> = { "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp" };

// ---------------------------------------------------------------------------------------------
// Settings (filled in by Claude Desktop from the extension's settings screen)

/** A setting the user left empty arrives as "" or as the unreplaced "${user_config.x}" placeholder. */
const setting = (name: string): string => {
  const value = (process.env[name] ?? "").trim();
  return value.startsWith("${") ? "" : value;
};

const numberSetting = (name: string, fallback: number, min: number, max: number): number => {
  const raw = setting(name);
  const n = raw === "" ? NaN : Number(raw);
  return Number.isFinite(n) && n >= min && n <= max ? n : fallback;
};

export interface Settings {
  apiKey: string;
  outputDir: string;
  capMicros: number;
  rateLimitPerMinute: number;
  maxImageBytes: number;
  baseUrl: string;
  imageModel: string;
  videoModel: string;
  pricing: Pricing;
}

export function loadSettings(): Settings {
  // The Google endpoint is pinned: the key must never be sent anywhere else. Another base URL is
  // accepted only for loopback hosts (tests with a fake).
  let baseUrl = GOOGLE_API;
  const override = setting("GEMINI_BASE_URL").replace(/\/+$/, "");
  if (override && override !== GOOGLE_API) {
    const host = new URL(override).hostname;
    if (host !== "localhost" && host !== "127.0.0.1") throw new ConfigError("GEMINI_BASE_URL may only point at Google or a loopback mock");
    baseUrl = override;
  }
  return {
    apiKey: setting("GEMINI_API_KEY"),
    outputDir: setting("OUTPUT_DIR") || join(homedir(), "Documents", "Gemini Media"),
    capMicros: usdToMicros(numberSetting("MONTHLY_CAP_USD", 30, 0, 100_000)),
    rateLimitPerMinute: Math.floor(numberSetting("RATE_LIMIT_PER_MINUTE", 6, 1, 600)),
    maxImageBytes: Math.floor(numberSetting("MAX_IMAGE_BYTES", 8 * 1024 * 1024, 1024, 14 * 1024 * 1024)),
    baseUrl,
    imageModel: setting("IMAGE_MODEL") || "gemini-nano-banana-2.1",
    videoModel: setting("VIDEO_MODEL") || "gemini-omni-1.1-flash",
    pricing: mergePricing(setting("PRICING_OVERRIDES")),
  };
}

// ---------------------------------------------------------------------------------------------
// Helpers

interface ToolResult {
  [key: string]: unknown;
  content: { type: "text"; text: string }[];
  isError?: boolean;
}

const ok = (value: unknown): ToolResult => ({ content: [{ type: "text", text: JSON.stringify(value, null, 2) }] });
const fail = (code: string, message: string): ToolResult => ({ isError: true, content: [{ type: "text", text: JSON.stringify({ error: code, message }, null, 2) }] });

const OUTCOME_RE = /^[a-z0-9_:.-]{1,64}$/;
/** The only log line. Fixed fields; nothing from a prompt, an image, a path or the key can enter it. */
function audit(tool: string, model: string, costMicros: number, outcome: string): void {
  process.stderr.write(
    JSON.stringify({ ts: new Date().toISOString(), tool, model, cost_usd: microsToUsd(costMicros), outcome: OUTCOME_RE.test(outcome) ? outcome : "invalid_outcome_code" }) + "\n",
  );
}

const nowSeconds = () => Math.floor(Date.now() / 1000);
const newId = () => randomBytes(8).toString("hex");

function stamp(): string {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}-${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`;
}

async function mapLimit<T, R>(items: T[], limit: number, fn: (item: T, index: number) => Promise<R>): Promise<R[]> {
  const results = new Array<R>(items.length);
  let next = 0;
  await Promise.all(
    Array.from({ length: Math.min(limit, items.length) }, async () => {
      while (next < items.length) {
        const i = next++;
        results[i] = await fn(items[i] as T, i);
      }
    }),
  );
  return results;
}

/**
 * Reads a reference image from this computer. Only a regular file with an image extension, within
 * the size limit, whose CONTENT is really JPEG/PNG/WebP is accepted, so this tool cannot be used to
 * send any other kind of file to Google.
 */
async function readImage(path: string, maxBytes: number): Promise<{ bytes: Uint8Array; mime: string } | string> {
  const shown = path.length > 120 ? `${path.slice(0, 117)}...` : path;
  if (!isAbsolute(path)) return `"${shown}" is not a full path. Ask the user for the complete path of the image file.`;
  if (!IMAGE_EXTENSIONS.has(extname(path).toLowerCase())) return `"${shown}" is not a .jpg, .jpeg, .png or .webp file.`;
  let info;
  try {
    info = await stat(path);
  } catch {
    return `"${shown}" was not found.`;
  }
  if (!info.isFile()) return `"${shown}" is not a file.`;
  if (info.size > maxBytes) return `"${shown}" is larger than ${Math.floor(maxBytes / 1024 / 1024)} MB. Use a smaller image.`;
  const bytes = new Uint8Array(await readFile(path));
  const mime = sniffImageMime(bytes);
  if (!mime) return `"${shown}" is not really a JPEG, PNG or WebP image.`;
  return { bytes, mime };
}

// ---------------------------------------------------------------------------------------------
// Tool schemas

const prompt = z.string().min(3).max(4000);

const generateImageSchema = z.object({
  prompt: prompt.describe("What to draw, in English for best results. Do not ask for Arabic text inside the image."),
  size: z.enum(IMAGE_SIZES).default("1K").describe("Output size. 1K is the default and cheapest; 2K costs about 1.5x and 4K about 3.4x."),
  aspect_ratio: z.enum(ASPECT_RATIOS).default("1:1").describe("Aspect ratio, e.g. 1:1 square post, 9:16 story, 16:9 landscape, 21:9 or 4:1 wide banner."),
  count: z.number().int().min(1).max(MAX_IMAGES).default(1).describe(`How many variations (1-${MAX_IMAGES}; at most ${MAX_IMAGES_4K} for 4K). Each one is billed.`),
});

const editImageSchema = z.object({
  image_paths: z
    .array(z.string())
    .min(1)
    .max(MAX_REFERENCES)
    .describe("Full paths on this computer of one or more reference images (.jpg, .png, .webp): files the user named, or `path` values returned by earlier calls."),
  instructions: prompt.describe("What to change and what to keep, e.g. 're-render at dusk, keep the building exactly as is' or 'replace the background with plain white'."),
  size: z.enum(IMAGE_SIZES).default("1K").describe("Output size. Default 1K."),
  aspect_ratio: z.enum(ASPECT_RATIOS).optional().describe("Output aspect ratio. Omit to follow the first reference image."),
});

const generateVideoSchema = z.object({
  prompt: prompt.describe("What happens in the clip: subject, action, camera movement, lighting, mood."),
  start_image_path: z.string().optional().describe("Optional full path of an image on this computer to use as the first frame."),
  duration_seconds: z.number().int().min(3).max(10).default(5).describe("Clip length in seconds (3-10). Billed per second."),
  resolution: z.enum(VIDEO_RESOLUTIONS).default("720p").describe("720p by default. A resolution without a configured price is refused."),
  aspect_ratio: z.enum(VIDEO_ASPECTS).default("16:9").describe("16:9 landscape or 9:16 vertical."),
});

const getJobSchema = z.object({ job_id: z.string().describe("The job_id returned by generate_image, edit_image or generate_video.") });

// ---------------------------------------------------------------------------------------------
// Server

export function createServer(settings: Settings, store: StateStore, fetchFn?: typeof fetch): McpServer {
  const server = new McpServer({ name: "gemini-media-desktop", version: VERSION });
  const client = () => new GeminiClient(settings.apiKey, settings.baseUrl, fetchFn);

  /** Checks shared by the tools that spend money. */
  async function guard(tool: string): Promise<ToolResult | null> {
    if (!/^[A-Za-z0-9._-]{16,256}$/.test(settings.apiKey)) {
      audit(tool, "-", 0, "no_key");
      return fail(
        "no_key",
        "No Gemini API key is set. In Claude Desktop open Settings > Extensions > Gemini Images & Video > Configure, paste the key from Google AI Studio, save, and try again.",
      );
    }
    if (!(await store.allowRequest(settings.rateLimitPerMinute))) {
      audit(tool, "-", 0, "rate_limited");
      return fail("rate_limited", `Refused: more than ${settings.rateLimitPerMinute} generation requests in one minute. Wait a minute and try again.`);
    }
    return null;
  }

  const capRefusal = async (tool: string, model: string, estimateMicros: number): Promise<ToolResult> => {
    const spent = await store.monthSpent();
    audit(tool, model, 0, "monthly_cap");
    return fail(
      "monthly_cap",
      `Refused: your monthly spending cap would be exceeded. Spent this month $${microsToUsd(spent)} of $${microsToUsd(settings.capMicros)}; ` +
        `this request is estimated at $${microsToUsd(estimateMicros)}. The cap resets on the 1st. To change it, open the extension's settings in Claude Desktop.`,
    );
  };

  const budget = async () => ({ month_spent_usd: microsToUsd(await store.monthSpent()), month_cap_usd: microsToUsd(settings.capMicros) });
  const notes = `Tell the user where each file was saved (path). Files stay on this computer in ${settings.outputDir}. estimated_cost_usd is an estimate; Google's invoice is authoritative.`;

  async function runImageJob(args: {
    tool: "generate_image" | "edit_image";
    prompt: string;
    size: (typeof IMAGE_SIZES)[number];
    aspectRatio?: string;
    count: number;
    references: MediaInput[];
  }): Promise<ToolResult> {
    const model = settings.imageModel;
    const perImage = settings.pricing.imagePerImage[args.size];
    if (!perImage) return fail("size_not_priced", `Size ${args.size} has no configured price, so it is disabled.`);
    if (args.size === "4K" && args.count > MAX_IMAGES_4K) return fail("too_many_4k", `At most ${MAX_IMAGES_4K} images per request at 4K. Ask for fewer, or use 2K.`);
    const perCallEstimate = perImage + settings.pricing.imageOverheadPerImage + args.references.length * REFERENCE_INPUT_COST_USD;
    const estimateMicros = usdToMicros(perCallEstimate * args.count);

    const jobId = newId();
    const reserved = await store.reserve({ id: jobId, tool: args.tool, model, costMicros: estimateMicros, capMicros: settings.capMicros, params: { size: args.size, aspect_ratio: args.aspectRatio ?? null, count: args.count, references: args.references.length } });
    if (!reserved) return capRefusal(args.tool, model, estimateMicros);

    await mkdir(settings.outputDir, { recursive: true });
    const base = `gemini-image-${stamp()}-${jobId.slice(0, 4)}`;
    const gemini = client();
    type Outcome = { path: string; bytes: number; costUsd: number } | { failure: { code: string; message: string }; costUsd: number };
    const outcomes = await mapLimit<number, Outcome>(
      Array.from({ length: args.count }, (_, i) => i),
      2,
      async (index) => {
        try {
          const interaction = await gemini.generateImage({ model, prompt: args.prompt, size: args.size, aspectRatio: args.aspectRatio, references: args.references, store: false });
          const usageCost = imageCostUsd(summarizeUsage(interaction.usage, "image"), settings.pricing);
          const image = findMedia(interaction, "image");
          if (!image?.data) {
            return { failure: { code: "no_image_returned", message: "Google returned no image (often a safety refusal). Rephrase the description and try again." }, costUsd: usageCost ?? perCallEstimate };
          }
          const bytes = decodeBase64(image.data);
          const mime = sniffImageMime(bytes);
          if (!mime) return { failure: { code: "bad_image_data", message: "Google returned data that is not a JPEG, PNG or WebP image." }, costUsd: usageCost ?? perCallEstimate };
          const path = join(settings.outputDir, `${base}${args.count > 1 ? `-${index + 1}` : ""}.${EXTENSION_FOR[mime]}`);
          await writeFile(path, bytes, { flag: "wx" });
          return { path, bytes: bytes.byteLength, costUsd: usageCost ?? perCallEstimate };
        } catch (e) {
          // A request Google rejected outright is not billed. A timeout or 5xx may have been, so it is counted.
          const billed = !(e instanceof GeminiError) || e.kind === "timeout" || e.kind === "upstream";
          return { failure: e instanceof GeminiError ? describeGeminiError(e) : { code: "write_failed", message: "Could not save the image to the output folder." }, costUsd: billed ? perCallEstimate : 0 };
        }
      },
    );

    const delivered = outcomes.filter((o): o is Extract<Outcome, { path: string }> => "path" in o);
    const failures = outcomes.filter((o): o is Extract<Outcome, { failure: unknown }> => "failure" in o).map((o) => o.failure);
    const costMicros = usdToMicros(outcomes.reduce((sum, o) => sum + o.costUsd, 0));
    const outcome = delivered.length ? (failures.length ? "partial" : "ok") : (failures[0]?.code ?? "failed");
    await store.settle(jobId, { status: delivered.length ? "succeeded" : "failed", costMicros, files: delivered.map((d) => d.path), error: delivered.length ? null : outcome });
    audit(args.tool, model, costMicros, outcome);

    const body = {
      job_id: jobId,
      status: delivered.length ? "succeeded" : "failed",
      model,
      requested: args.count,
      delivered: delivered.length,
      images: delivered.map((d) => ({ path: d.path, bytes: d.bytes })),
      ...(failures.length && { failures }),
      estimated_cost_usd: microsToUsd(costMicros),
      ...(await budget()),
      notes,
    };
    return delivered.length ? ok(body) : { ...ok(body), isError: true };
  }

  server.registerTool(
    "generate_image",
    {
      title: "Generate image",
      description:
        `Generate 1-4 images from a text description with Google Gemini, billed to the user's own Gemini key, and save them on this computer. ` +
        `Sizes: 1K (default), 2K, 4K. Costs money on every call and counts against the monthly cap. Takes 15-90 seconds. ` +
        `Returns the saved file paths, the estimated cost in USD and the model used. ${DATA_WARNING}`,
      inputSchema: generateImageSchema,
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
    },
    async (args) => (await guard("generate_image")) ?? runImageJob({ tool: "generate_image", prompt: args.prompt, size: args.size, aspectRatio: args.aspect_ratio, count: args.count, references: [] }),
  );

  server.registerTool(
    "edit_image",
    {
      title: "Edit image",
      description:
        `Edit or re-render one or more images from this computer following written instructions (re-render, change background, change one part), and save the result as a new file. ` +
        `The originals are never modified. There is no mask: say exactly what to change and what to keep. The reference images are sent to Google. ` +
        `Costs money on every call. Returns the saved file path, the estimated cost in USD and the model used. ${DATA_WARNING}`,
      inputSchema: editImageSchema,
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
    },
    async (args) => {
      const refused = await guard("edit_image");
      if (refused) return refused;
      const references: MediaInput[] = [];
      let total = 0;
      for (const path of [...new Set(args.image_paths)]) {
        const loaded = await readImage(path, settings.maxImageBytes);
        if (typeof loaded === "string") return fail("image_not_usable", loaded);
        total += loaded.bytes.byteLength;
        if (total > MAX_REFERENCE_TOTAL_BYTES) return fail("references_too_large", `The reference images are larger than ${MAX_REFERENCE_TOTAL_BYTES / 1024 / 1024} MB in total. Use fewer or smaller images.`);
        references.push({ data: encodeBase64(loaded.bytes), mimeType: loaded.mime });
      }
      return runImageJob({ tool: "edit_image", prompt: args.instructions, size: args.size, aspectRatio: args.aspect_ratio, count: 1, references });
    },
  );

  server.registerTool(
    "generate_video",
    {
      title: "Generate video",
      description:
        `Start a short video (3-10 s, 16:9 or 9:16) from a description, optionally starting from an image on this computer. Returns a job_id immediately; ` +
        `poll get_job until it is done, then the video is saved on this computer. Video is billed per second and is the most expensive tool: ` +
        `always show the user the estimated cost and get an explicit yes first. ${DATA_WARNING}`,
      inputSchema: generateVideoSchema,
      annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: false, openWorldHint: true },
    },
    async (args) => {
      const tool = "generate_video";
      const refused = await guard(tool);
      if (refused) return refused;
      const model = settings.videoModel;
      const perSecond = settings.pricing.videoPerSecond[args.resolution];
      if (!perSecond) {
        return fail("resolution_not_priced", `Resolution ${args.resolution} is disabled because Google's price per second for it has not been confirmed. Available: ${Object.keys(settings.pricing.videoPerSecond).join(", ")}.`);
      }
      let startImage: MediaInput | undefined;
      if (args.start_image_path) {
        const loaded = await readImage(args.start_image_path, settings.maxImageBytes);
        if (typeof loaded === "string") return fail("image_not_usable", loaded);
        startImage = { data: encodeBase64(loaded.bytes), mimeType: loaded.mime };
      }
      const estimateMicros = usdToMicros(perSecond * args.duration_seconds + (startImage ? REFERENCE_INPUT_COST_USD : 0));
      const jobId = newId();
      const params = { duration_seconds: args.duration_seconds, resolution: args.resolution, aspect_ratio: args.aspect_ratio, start_image: Boolean(startImage) };
      if (!(await store.reserve({ id: jobId, tool, model, costMicros: estimateMicros, capMicros: settings.capMicros, params }))) return capRefusal(tool, model, estimateMicros);

      try {
        const interaction = await client().startVideo({ model, prompt: args.prompt, durationSeconds: args.duration_seconds, resolution: args.resolution, aspectRatio: args.aspect_ratio, startImage });
        if (!interaction.id) throw new GeminiError("upstream", 502, "Google accepted the request but returned no job id.");
        await store.setOperation(jobId, interaction.id);
      } catch (e) {
        const billed = !(e instanceof GeminiError) || e.kind === "timeout" || e.kind === "upstream";
        const described = describeGeminiError(e);
        await store.settle(jobId, { status: "failed", costMicros: billed ? estimateMicros : 0, files: [], error: described.code });
        audit(tool, model, billed ? estimateMicros : 0, described.code);
        return fail(described.code, described.message);
      }
      audit(tool, model, estimateMicros, "started");
      return ok({
        job_id: jobId,
        status: "running",
        model,
        estimated_cost_usd: microsToUsd(estimateMicros),
        ...(await budget()),
        notes:
          "The video is being generated (usually 1-5 minutes). Call get_job with this job_id about every 30 seconds until status is succeeded or failed. " +
          "The video is only downloaded when get_job is called, so do not skip this.",
      });
    },
  );

  /** Asks Google once about a running video; saves it when ready. Idempotent. */
  async function refreshVideo(job: Job): Promise<Job> {
    const failWith = async (code: string, billed: boolean): Promise<Job> => {
      const cost = billed ? job.cost_micros : 0;
      audit(job.tool, job.model, cost, code);
      return store.settle(job.id, { status: "failed", costMicros: cost, files: [], error: code });
    };
    const age = nowSeconds() - job.created_at;
    if (!job.operation) return age > 300 ? failWith("start_not_confirmed", false) : job;
    const gemini = client();
    let interaction;
    try {
      interaction = await gemini.getInteraction(job.operation);
    } catch (e) {
      if (e instanceof GeminiError && e.kind === "not_found") return failWith("google_job_not_found", false);
      return age > VIDEO_JOB_TIMEOUT_SECONDS ? failWith("timeout", true) : job;
    }
    const status = String(interaction.status ?? "").toLowerCase();
    if (status === "failed" || status === "cancelled") return failWith(`google_${status}`, false);
    if (status !== "completed") return age > VIDEO_JOB_TIMEOUT_SECONDS ? failWith("timeout", true) : job;

    const usageCost = videoCostUsd(summarizeUsage(interaction.usage, "video"), settings.pricing);
    const video = findMedia(interaction, "video");
    if (!video) {
      const cost = usageCost !== null ? usdToMicros(usageCost) : 0;
      audit(job.tool, job.model, cost, "no_video_returned");
      return store.settle(job.id, { status: "failed", costMicros: cost, files: [], error: "no_video_returned" });
    }
    let bytes: Uint8Array;
    if (video.data) {
      bytes = decodeBase64(video.data);
    } else {
      let res;
      try {
        res = await gemini.downloadFile(video.uri!);
      } catch {
        return age > VIDEO_JOB_TIMEOUT_SECONDS ? failWith("download_failed", true) : job;
      }
      if (!res) return job; // Google is still processing the file.
      bytes = new Uint8Array(await res.arrayBuffer());
    }
    if (bytes.byteLength === 0 || bytes.byteLength > MAX_VIDEO_BYTES) return failWith("bad_video_size", true);
    await mkdir(settings.outputDir, { recursive: true });
    const path = join(settings.outputDir, `gemini-video-${stamp()}-${job.id.slice(0, 4)}.mp4`);
    await writeFile(path, bytes, { flag: "wx" });
    const cost = usageCost !== null ? usdToMicros(usageCost) : job.cost_micros;
    audit(job.tool, job.model, cost, "ok");
    return store.settle(job.id, { status: "succeeded", costMicros: cost, files: [path], error: null });
  }

  server.registerTool(
    "get_job",
    {
      title: "Get job status",
      description: "Status of a job and, when finished, where its files were saved, the estimated cost and the model. Use it to poll a video job until it is done.",
      inputSchema: getJobSchema,
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    },
    async (args) => {
      let job = /^[a-f0-9]{16}$/.test(args.job_id) ? await store.getJob(args.job_id) : null;
      if (!job) return fail("job_not_found", "No such job. Check the job_id.");
      if (job.status === "running" && job.tool === "generate_video") job = await refreshVideo(job);
      const body = {
        job_id: job.id,
        tool: job.tool,
        status: job.status,
        model: job.model,
        created_at: new Date(job.created_at * 1000).toISOString(),
        params: job.params,
        estimated_cost_usd: microsToUsd(job.cost_micros),
        ...(job.error && { error: job.error }),
      };
      if (job.status === "succeeded") return ok({ ...body, files: job.files.map((path) => ({ path })), notes });
      if (job.status === "running") return ok({ ...body, notes: "Still running. Call get_job again in about 30 seconds." });
      return ok({ ...body, notes: "The job failed. If estimated_cost_usd is 0 nothing was counted against the cap." });
    },
  );

  server.registerTool(
    "usage",
    {
      title: "Spending this month",
      description: "What has been spent this month against the monthly cap, what was spent today, the current price list, and the folder where files are saved.",
      inputSchema: z.object({}),
      annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    },
    async () => {
      const spent = await store.monthSpent();
      const p = settings.pricing;
      return ok({
        month: store.month(),
        month_spent_usd: microsToUsd(spent),
        month_cap_usd: microsToUsd(settings.capMicros),
        month_remaining_usd: microsToUsd(Math.max(0, settings.capMicros - spent)),
        spent_today_usd: microsToUsd(await store.daySpent()),
        requests_this_month: await store.byTool(),
        models: { image: settings.imageModel, video: settings.videoModel },
        price_list_usd: {
          image_each: Object.fromEntries(Object.entries(p.imagePerImage).map(([k, v]) => [k, Math.round((v + p.imageOverheadPerImage) * 1e4) / 1e4])),
          video_per_second: p.videoPerSecond,
        },
        output_folder: settings.outputDir,
        key_configured: settings.apiKey !== "",
        notes: "Amounts are this extension's estimates in USD; Google's invoice is authoritative. The cap and the folder are changed in the extension's settings in Claude Desktop.",
      });
    },
  );

  return server;
}

// ---------------------------------------------------------------------------------------------
// Entry point

export function main(): void {
  let settings: Settings;
  try {
    settings = loadSettings();
  } catch (e) {
    process.stderr.write(`gemini-media-desktop: ${e instanceof ConfigError ? e.message : "invalid settings"}\n`);
    process.exit(1);
  }
  const store = new StateStore(join(settings.outputDir, ".gemini-media", "state.json"));
  serveStdio(() => createServer(settings, store));
}

main();
