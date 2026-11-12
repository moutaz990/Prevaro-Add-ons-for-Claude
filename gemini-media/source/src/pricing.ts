// Prices and money helpers.

export class ConfigError extends Error {}

export interface Pricing {
  /** USD per 1M input tokens (image model). */
  imageInputPerM: number;
  /** USD per 1M image output tokens. */
  imageOutputPerM: number;
  /** USD per 1M text/thinking output tokens (image model). */
  imageTextOutputPerM: number;
  /** USD per generated image, by size. Used for the pre-flight estimate/reservation. */
  imagePerImage: Record<string, number>;
  /** USD added per image to the reservation for input + thinking tokens. */
  imageOverheadPerImage: number;
  /** USD per 1M input tokens (video model). */
  videoInputPerM: number;
  /** USD per 1M video output tokens. */
  videoOutputPerM: number;
  /** USD per second of generated video, by resolution. A resolution with no price is refused. */
  videoPerSecond: Record<string, number>;
}

// Defaults checked on 2026-11-12 against Google's pricing page (https://ai.google.dev/gemini-api/docs/pricing).
// Google's invoice is authoritative; override with the PRICING_OVERRIDES environment variable.
export const DEFAULT_PRICING: Pricing = {
  imageInputPerM: 1.5,
  imageOutputPerM: 30,
  imageTextOutputPerM: 7.5,
  imagePerImage: { "1K": 0.0336, "2K": 0.0504, "4K": 0.113 },
  imageOverheadPerImage: 0.01,
  videoInputPerM: 1.5,
  videoOutputPerM: 17.5,
  // Google publishes only the 720p rate (5,792 tokens/s x $17.50/1M). 360p is reserved at the 720p rate
  // as an upper bound. 1080p/4K have no published per-second rate, so they stay disabled until the owner
  // sets one through PRICING_OVERRIDES.
  videoPerSecond: { "360p": 0.1014, "720p": 0.1014 },
};

export const usdToMicros = (usd: number): number => Math.ceil(usd * 1_000_000 - 1e-6);
export const microsToUsd = (micros: number): number => Math.round(micros / 100) / 10_000;

export function mergePricing(raw: string | undefined): Pricing {
  const merged: Pricing = structuredClone(DEFAULT_PRICING);
  if (!raw || !raw.trim()) return merged;
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new ConfigError("PRICING_OVERRIDES is not valid JSON");
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) throw new ConfigError("PRICING_OVERRIDES must be a JSON object");
  const target = merged as unknown as Record<string, unknown>;
  for (const [key, value] of Object.entries(parsed)) {
    if (!(key in merged)) throw new ConfigError(`PRICING_OVERRIDES: unknown key ${key}`);
    if (typeof target[key] === "number") {
      if (typeof value !== "number" || !Number.isFinite(value) || value < 0) throw new ConfigError(`PRICING_OVERRIDES.${key} must be a non-negative number`);
      target[key] = value;
    } else {
      if (typeof value !== "object" || value === null) throw new ConfigError(`PRICING_OVERRIDES.${key} must be an object`);
      for (const [k, v] of Object.entries(value)) {
        if (typeof v !== "number" || !Number.isFinite(v) || v <= 0) throw new ConfigError(`PRICING_OVERRIDES.${key}.${k} must be a positive number`);
        (target[key] as Record<string, number>)[k] = v;
      }
    }
  }
  return merged;
}
