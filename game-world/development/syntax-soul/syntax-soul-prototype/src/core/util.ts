export function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n));
}

export function randInt(seed: number): () => number {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let x = t;
    x = Math.imul(x ^ (x >>> 15), x | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

export function uid(prefix = "id"): string {
  return `${prefix}_${Math.random().toString(16).slice(2)}_${Date.now().toString(16)}`;
}

export function pick<T>(arr: T[], r: number): T {
  return arr[Math.floor(r * arr.length)];
}

export function now(): number {
  return Date.now();
}

export function approxSyllables(word: string): number {
  const w = word.toLowerCase().replace(/[^a-z]/g, "");
  if (!w) return 0;
  const groups = w.match(/[aeiouy]+/g);
  return Math.max(1, groups?.length ?? 1);
}

export function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .split(/[\s,.;:!?()"'`]+/)
    .map((t) => t.trim())
    .filter(Boolean);
}

export function rarityRoll(r: number): "COMMON" | "RARE" | "EPIC" | "MYTHIC" {
  if (r < 0.72) return "COMMON";
  if (r < 0.92) return "RARE";
  if (r < 0.99) return "EPIC";
  return "MYTHIC";
}
