// Minimal REST client for the Gemini Interactions API (image: Nano Banana, video: Gemini Omni).
// See NOTICE.md for the two MIT-licensed projects parts of this file are adapted from.
// The API key is sent only in the x-goog-api-key header, only to the pinned Google host, and is
// redacted from any upstream error text before that text can leave this module.
//
// Error classification, key redaction and interaction parsing are adapted from
// crabkun/nano-banana-mcp (MIT) src/google.ts + src/interaction.ts @ 1b0818d.
// The video request shape (response_format type "video", duration, delivery "uri", file polling)
// follows u2n4/gemini-media-mcp (MIT) servers/omni/src/omni_mcp_server/server.py @ e10cd49.
import type { Pricing } from "./pricing";

export type GeminiErrorKind = "auth" | "forbidden" | "not_found" | "rate_limit" | "upstream" | "bad_request" | "timeout";

export class GeminiError extends Error {
  constructor(
    readonly kind: GeminiErrorKind,
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

interface Block {
  type?: string;
  text?: string;
  data?: string;
  uri?: string;
  mime_type?: string;
}

interface Step {
  type?: string;
  content?: Block[];
}

export interface RawInteraction {
  id?: string;
  status?: string;
  steps?: Step[];
  outputs?: Block[];
  output_video?: Block;
  usage?: Record<string, unknown>;
  error?: { code?: string | number; message?: string };
}

export interface Usage {
  inputTokens: number;
  outputTokens: number;
  mediaOutputTokens: number;
}

export interface MediaInput {
  data: string; // base64
  mimeType: string;
}

const classify = (status: number, message: string): GeminiErrorKind => {
  if (status === 401 || (status === 400 && /api key/i.test(message))) return "auth";
  if (status === 403) return "forbidden";
  if (status === 404) return "not_found";
  if (status === 429) return "rate_limit";
  return status >= 500 ? "upstream" : "bad_request";
};

const toNumber = (v: unknown) => (typeof v === "number" && Number.isFinite(v) ? v : 0);

function outputBlocks(d: RawInteraction): Block[] {
  const fromSteps = (d.steps ?? []).filter((s) => s.type === "model_output").flatMap((s) => s.content ?? []);
  const extra = d.output_video ? [{ ...d.output_video, type: "video" }] : [];
  return [...fromSteps, ...(d.outputs ?? []), ...extra];
}

export function findMedia(d: RawInteraction, type: "image" | "video"): Block | null {
  return outputBlocks(d).filter((b) => b.type === type && (b.data || b.uri)).at(-1) ?? null;
}

export function summarizeUsage(usage: RawInteraction["usage"], modality: "image" | "video"): Usage {
  const byModality = Array.isArray(usage?.output_tokens_by_modality) ? (usage.output_tokens_by_modality as { modality?: string; tokens?: number }[]) : [];
  const media = byModality.filter((m) => String(m?.modality).toLowerCase() === modality).reduce((sum, m) => sum + toNumber(m.tokens), 0);
  return {
    inputTokens: toNumber(usage?.total_input_tokens),
    outputTokens: toNumber(usage?.total_output_tokens),
    mediaOutputTokens: media,
  };
}

/** Actual image cost in USD from token usage; null when Google reported no usage. */
export function imageCostUsd(u: Usage, p: Pricing): number | null {
  if (u.inputTokens + u.outputTokens === 0) return null;
  const textOut = Math.max(0, u.outputTokens - u.mediaOutputTokens);
  return (u.inputTokens * p.imageInputPerM + u.mediaOutputTokens * p.imageOutputPerM + textOut * p.imageTextOutputPerM) / 1e6;
}

/** Actual video cost in USD from token usage; null when Google reported no usage. */
export function videoCostUsd(u: Usage, p: Pricing): number | null {
  if (u.outputTokens === 0) return null;
  return (u.inputTokens * p.videoInputPerM + u.outputTokens * p.videoOutputPerM) / 1e6;
}

export function decodeBase64(data: string): Uint8Array {
  const native = (Uint8Array as unknown as { fromBase64?: (s: string) => Uint8Array }).fromBase64;
  if (native) return native.call(Uint8Array, data);
  const bin = atob(data);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

export function encodeBase64(bytes: Uint8Array): string {
  const native = (bytes as unknown as { toBase64?: () => string }).toBase64;
  if (native) return native.call(bytes);
  let s = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) s += String.fromCharCode(...bytes.subarray(i, i + chunk));
  return btoa(s);
}

const INTERACTION_ID_RE = /^[A-Za-z0-9_-]{8,512}$/;
const FILE_ID_RE = /^[a-z0-9][a-z0-9-]{0,63}$/;
const REDIRECT_HOST_RE = /(^|\.)(googleapis\.com|googleusercontent\.com)$/;

export class GeminiClient {
  constructor(
    private readonly apiKey: string,
    private readonly baseUrl: string,
    private readonly fetchFn: typeof fetch = (input, init) => fetch(input, init),
  ) {}

  private redact(text: string): string {
    return text.split(this.apiKey).join("[redacted]");
  }

  private async toError(res: Response): Promise<GeminiError> {
    const text = await res.text().catch(() => "");
    let message = text.slice(0, 400);
    try {
      message = String(JSON.parse(text)?.error?.message ?? message).slice(0, 400);
    } catch {}
    message = this.redact(message);
    return new GeminiError(classify(res.status, message), res.status, message);
  }

  private async request(path: string, init: RequestInit, timeoutMs: number): Promise<Response> {
    let res: Response;
    try {
      res = await this.fetchFn(this.baseUrl + path, {
        ...init,
        headers: { "x-goog-api-key": this.apiKey, ...init.headers },
        signal: AbortSignal.timeout(timeoutMs),
      });
    } catch (e) {
      const name = e instanceof Error ? e.name : "";
      if (name === "TimeoutError" || name === "AbortError") throw new GeminiError("timeout", 504, "Google did not answer in time.");
      throw new GeminiError("upstream", 502, "Could not reach Google.");
    }
    const manualRedirect = init.redirect === "manual" && res.status >= 300 && res.status < 400;
    if (!res.ok && !manualRedirect) throw await this.toError(res);
    return res;
  }

  private async createInteraction(body: unknown, timeoutMs: number): Promise<RawInteraction> {
    const res = await this.request(
      "/v1beta/interactions",
      { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) },
      timeoutMs,
    );
    return (await res.json()) as RawInteraction;
  }

  /** One synchronous image generation/edit. The prompt and images are passed through as data only. */
  generateImage(args: { model: string; prompt: string; size: string; aspectRatio?: string; references: MediaInput[]; store: boolean }): Promise<RawInteraction> {
    const input = args.references.length
      ? [{ type: "text", text: args.prompt }, ...args.references.map((r) => ({ type: "image", data: r.data, mime_type: r.mimeType }))]
      : args.prompt;
    return this.createInteraction(
      {
        model: args.model,
        input,
        response_format: {
          type: "image",
          mime_type: "image/jpeg",
          image_size: args.size,
          ...(args.aspectRatio && { aspect_ratio: args.aspectRatio }),
        },
        store: args.store,
      },
      200_000,
    );
  }

  /** Starts a background video generation and returns immediately with the interaction id. */
  startVideo(args: { model: string; prompt: string; durationSeconds: number; resolution: string; aspectRatio: string; startImage?: MediaInput }): Promise<RawInteraction> {
    const input = args.startImage
      ? [{ type: "image", data: args.startImage.data, mime_type: args.startImage.mimeType }, { type: "text", text: args.prompt }]
      : args.prompt;
    return this.createInteraction(
      {
        model: args.model,
        input,
        response_format: {
          type: "video",
          duration: `${args.durationSeconds}s`,
          aspect_ratio: args.aspectRatio,
          resolution: args.resolution,
          delivery: "uri",
        },
        background: true,
        store: true,
      },
      60_000,
    );
  }

  async getInteraction(id: string): Promise<RawInteraction> {
    if (!INTERACTION_ID_RE.test(id)) throw new GeminiError("bad_request", 400, "Invalid interaction id.");
    return (await (await this.request(`/v1beta/interactions/${id}`, { method: "GET" }, 30_000)).json()) as RawInteraction;
  }

  /**
   * Fetches a Google-hosted result file. Only URIs on the pinned Google host are accepted, the key
   * is sent to that host only, and a redirect is followed once, without the key, to a Google host.
   * Returns null while the file is still being processed.
   */
  async downloadFile(uri: string): Promise<Response | null> {
    let url: URL;
    try {
      url = new URL(uri);
    } catch {
      throw new GeminiError("upstream", 502, "Google returned an invalid file link.");
    }
    if (url.origin !== new URL(this.baseUrl).origin) throw new GeminiError("upstream", 502, "Google returned a file link on an unexpected host.");
    const fileId = url.pathname.match(/\/files\/([^/:]+)(?::download)?$/)?.[1];
    if (!fileId || !FILE_ID_RE.test(fileId)) throw new GeminiError("upstream", 502, "Google returned an unrecognized file link.");

    const info = (await (await this.request(`/v1beta/files/${fileId}`, { method: "GET" }, 30_000)).json()) as { state?: string };
    if (info.state === "FAILED") throw new GeminiError("upstream", 502, "Google failed to process the video file.");
    if (info.state && info.state !== "ACTIVE") return null;

    const res = await this.request(`/v1beta/files/${fileId}:download?alt=media`, { method: "GET", redirect: "manual" }, 120_000);
    if (res.status >= 300 && res.status < 400) {
      const location = res.headers.get("location");
      const target = location ? new URL(location, this.baseUrl) : null;
      if (!target || target.protocol !== "https:" || !REDIRECT_HOST_RE.test(target.hostname)) {
        throw new GeminiError("upstream", 502, "Google redirected the download to an unexpected host.");
      }
      const followed = await this.fetchFn(target.toString(), { signal: AbortSignal.timeout(120_000) });
      if (!followed.ok) throw new GeminiError("upstream", followed.status, "Could not download the video from Google.");
      return followed;
    }
    return res;
  }
}

/**
 * Checks a key with a free, read-only call (list one model). "invalid" means Google refused the key;
 * "unreachable" means no verdict could be obtained.
 */
export async function checkKey(apiKey: string, baseUrl: string, fetchFn: typeof fetch = (input, init) => fetch(input, init)): Promise<"valid" | "invalid" | "unreachable"> {
  try {
    const res = await fetchFn(`${baseUrl}/v1beta/models?pageSize=1`, { headers: { "x-goog-api-key": apiKey }, signal: AbortSignal.timeout(10_000) });
    await res.body?.cancel();
    if (res.ok) return "valid";
    return res.status === 400 || res.status === 401 || res.status === 403 ? "invalid" : "unreachable";
  } catch {
    return "unreachable";
  }
}

/** A short, fixed explanation for the user. Upstream text is included only as quoted data. */
export function describeGeminiError(e: unknown): { code: string; message: string } {
  if (!(e instanceof GeminiError)) return { code: "internal_error", message: "Internal error while handling the request." };
  const said = e.message ? ` Google said: "${e.message}"` : "";
  switch (e.kind) {
    case "auth":
    case "forbidden":
      return {
        code: `google_${e.kind}`,
        message:
          "Google rejected your API key (invalid, deleted, restricted, or its project has no billing; these models have no free tier). " +
          "To use another key, disconnect the connector in Claude and connect again." + said,
      };
    case "rate_limit":
      return { code: "google_rate_limit", message: "Google rate limit or quota exceeded (HTTP 429). Try again later." + said };
    case "timeout":
      return { code: "google_timeout", message: "Google did not answer in time. Nothing was delivered; check `usage` before retrying." };
    case "upstream":
      return { code: `google_${e.status}`, message: `Google service error (HTTP ${e.status}).` + said };
    default:
      return { code: `google_${e.status}`, message: `Google rejected the request (HTTP ${e.status}).` + said };
  }
}
