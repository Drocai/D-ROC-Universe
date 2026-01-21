import {
  BattleState,
  CadenceMode,
  JudgeBreakdown,
  Opponent,
  RoundResult,
  ShardDef,
  Soul,
  TraitDef
} from "./types";
import { approxSyllables, clamp, pick, randInt, rarityRoll, tokenize, uid } from "./util";
import { ALL_SHARDS, OPPONENTS, SHARDS, TRAITS } from "./data";

export type DerivedStats = { total: { flow: number; aggression: number; complexity: number; presence: number } };

export function getShardDef(id: ShardDef["id"]): ShardDef {
  const s = ALL_SHARDS.find((x) => x.id === id);
  if (!s) throw new Error(`Unknown shard: ${id}`);
  return s;
}

export function getTraitDef(id: TraitDef["id"]): TraitDef {
  const t = TRAITS.find((x) => x.id === id);
  if (!t) throw new Error(`Unknown trait: ${id}`);
  return t;
}

export function getOpponent(id: string): Opponent {
  const o = OPPONENTS.find((x) => x.id === id);
  if (!o) throw new Error(`Unknown opponent: ${id}`);
  return o;
}

export function deriveStats(soul: Soul): DerivedStats {
  const base = soul.base;
  const shardMods = soul.equippedShards.map(getShardDef).reduce(
    (acc, s) => ({
      flow: acc.flow + (s.mods.flow ?? 0),
      aggression: acc.aggression + (s.mods.aggression ?? 0),
      complexity: acc.complexity + (s.mods.complexity ?? 0),
      presence: acc.presence + (s.mods.presence ?? 0)
    }),
    { flow: 0, aggression: 0, complexity: 0, presence: 0 }
  );

  const traitMods = soul.traits.map(getTraitDef).reduce(
    (acc, t) => ({
      flow: acc.flow + (t.mods?.flow ?? 0),
      aggression: acc.aggression + (t.mods?.aggression ?? 0),
      complexity: acc.complexity + (t.mods?.complexity ?? 0),
      presence: acc.presence + (t.mods?.presence ?? 0)
    }),
    { flow: 0, aggression: 0, complexity: 0, presence: 0 }
  );

  const total = {
    flow: clamp(base.flow + shardMods.flow + traitMods.flow, 0, 100),
    aggression: clamp(base.aggression + shardMods.aggression + traitMods.aggression, 0, 100),
    complexity: clamp(base.complexity + shardMods.complexity + traitMods.complexity, 0, 100),
    presence: clamp(base.presence + shardMods.presence + traitMods.presence, 0, 100)
  };

  return { total };
}

const RHYME_FAMILIES: Record<string, string[]> = {
  "ation": ["creation", "mutation", "iteration", "calibration", "domination", "translation", "termination"],
  "ight": ["night", "flight", "byte", "ignite", "highlight", "rewrite", "satellite"],
  "ode": ["code", "mode", "node", "explode", "overload", "decode", "upload"]
};

const LEXICON_PACKS = {
  basic: ["clean", "sharp", "wired", "cold", "prime", "heavy", "silent", "neon", "steel", "hollow"],
  dense: ["multidimensional", "asymptotic", "orthogonal", "nonlinear", "cryptographic", "hyperthreaded", "quantized"],
  tech: ["kernel", "packet", "compiler", "payload", "protocol", "checksum", "runtime", "container", "pipeline"]
};

const PUNCHLINES = {
  mild: ["I take your best and still outclass it.", "You talk loud but you lack the pattern.", "Your aura weak—my presence happens."],
  savage: ["I delete your whole brand in one commit.", "Your lane gets repossessed—admit it.", "I turn your name to a warning label—ship it."],
  mythic: ["I rewrite your legacy at root level.", "I bend the judge—your score gets severed.", "I turn your mic to a relic—disassembled."]
};

function chooseCadenceTemplate(flow: number, cadence: CadenceMode): string[] {
  const fast = cadence === "DOUBLE_TIME" || flow >= 70;
  const heavy = cadence === "HALF_TIME" || flow <= 35;
  if (fast) return ["{A}, {B}, {C} — I’m moving like a {KW}.", "{A} with the {KW} — {B}, then {PUNCH}."];
  if (heavy) return ["{A}… {B}. {C}. {PUNCH}", "Slow burn — {A} on the {KW}, {PUNCH}."];
  return ["{A} {B} {C} — I snap with the {KW}.", "{A} then {B}; {C}. {PUNCH}"];
}

function pickRhymeFamily(complexity: number, r: number): { fam: string; word: string } {
  const keys = Object.keys(RHYME_FAMILIES);
  const fam = keys[Math.floor(r * keys.length)];
  const words = RHYME_FAMILIES[fam];
  const idx = Math.floor(((complexity / 100) * 0.6 + 0.4) * r * words.length) % words.length;
  return { fam, word: words[idx] };
}

function wordPool(stats: { flow: number; aggression: number; complexity: number; presence: number }): string[] {
  const pool = [...LEXICON_PACKS.basic];
  if (stats.complexity >= 45) pool.push(...LEXICON_PACKS.dense);
  if (stats.complexity >= 30) pool.push(...LEXICON_PACKS.tech);
  if (stats.presence >= 55) pool.push("anthem", "banner", "stadium", "spotlight", "legend");
  if (stats.aggression >= 55) pool.push("wreck", "shatter", "erase", "smoke", "sever");
  return pool;
}

export function generateBar(args: {
  seed: number;
  soul: Soul;
  opponent: Opponent;
  cadence: CadenceMode;
  opponentKeyword: string;
  lastBars: string[];
}): { bar: string; meta: { rhymeFam: string; rhymeWord: string; usedCallback: boolean } } {
  const r = randInt(args.seed);
  const stats = deriveStats(args.soul).total;
  const templates = chooseCadenceTemplate(stats.flow, args.cadence);
  const template = pick(templates, r());
  const pool = wordPool(stats);
  const callback = stats.presence >= 35 || args.soul.traits.includes("CALLBACK");
  const kw = callback ? args.opponentKeyword : pick(args.opponent.keywords, r());

  const { fam, word } = pickRhymeFamily(stats.complexity, r());
  const sigWord = args.soul.signatureWords.length ? pick(args.soul.signatureWords, r()) : "";
  const a = pick(pool, r());
  const b = pick(pool, r());
  const c = sigWord ? `${sigWord} ${pick(pool, r())}` : pick(pool, r());

  const punchTier = stats.aggression >= 70 ? "mythic" : stats.aggression >= 45 ? "savage" : "mild";
  const punch = pick(PUNCHLINES[punchTier as keyof typeof PUNCHLINES], r());

  let bar = template
    .replaceAll("{A}", a)
    .replaceAll("{B}", b)
    .replaceAll("{C}", c)
    .replaceAll("{KW}", kw)
    .replaceAll("{PUNCH}", punch);

  if (stats.complexity >= 40 && r() > 0.55) bar += ` — ${word}.`;
  if (args.soul.signaturePhrases.length && r() > 0.75) bar += ` ${pick(args.soul.signaturePhrases, r())}`;

  const normalized = bar.toLowerCase();
  const repetition = args.lastBars.some((x) => x.toLowerCase() === normalized);
  if (repetition) bar = bar.replace(punch, "I switch the pattern—new damage happens.");

  return { bar, meta: { rhymeFam: fam, rhymeWord: word, usedCallback: callback } };
}

function scoreVariety(bar: string, lastBars: string[]): number {
  if (!lastBars.length) return 18;
  const t = tokenize(bar);
  const prev = tokenize(lastBars[lastBars.length - 1]);
  const overlap = t.filter((w) => prev.includes(w)).length;
  const ratio = prev.length ? overlap / prev.length : 0;
  return clamp(18 - ratio * 12, 4, 18);
}

function scoreRelevance(bar: string, kw: string): number {
  const t = tokenize(bar);
  const hit = t.includes(kw.toLowerCase());
  return hit ? 18 : 10;
}

function scoreComplexity(bar: string): number {
  const words = tokenize(bar);
  const avgLen = words.reduce((a, w) => a + w.length, 0) / Math.max(1, words.length);
  const syll = words.reduce((a, w) => a + approxSyllables(w), 0) / Math.max(1, words.length);
  const rare = words.filter((w) => w.length >= 10).length;
  return clamp(8 + avgLen * 0.8 + syll * 1.2 + rare * 1.1, 5, 22);
}

function scoreFlow(bar: string, cadence: CadenceMode, flowStat: number): number {
  const words = tokenize(bar).length;
  const target = cadence === "DOUBLE_TIME" ? 20 : cadence === "HALF_TIME" ? 12 : 16;
  const diff = Math.abs(words - target);
  const base = 18 - diff * 0.7;
  return clamp(base + flowStat * 0.04, 6, 24);
}

function scoreAggression(bar: string, aggroStat: number): number {
  const t = tokenize(bar);
  const hot = ["delete", "erase", "sever", "kill", "wreck", "smoke", "crash", "repossessed", "root", "terminate"];
  const hits = t.filter((w) => hot.includes(w)).length;
  return clamp(8 + aggroStat * 0.08 + hits * 2.2, 6, 24);
}

export function judgeBar(args: {
  bar: string;
  cadence: CadenceMode;
  stats: { flow: number; aggression: number; complexity: number; presence: number };
  opponentKeyword: string;
  lastBars: string[];
}): JudgeBreakdown {
  const flow = scoreFlow(args.bar, args.cadence, args.stats.flow);
  const complexity = scoreComplexity(args.bar) + args.stats.complexity * 0.03;
  const aggression = scoreAggression(args.bar, args.stats.aggression);
  const relevance = scoreRelevance(args.bar, args.opponentKeyword) + args.stats.presence * 0.02;
  const variety = scoreVariety(args.bar, args.lastBars);

  const total = clamp(flow + aggression + complexity + relevance + variety, 20, 100);
  return {
    flow: Math.round(flow),
    aggression: Math.round(aggression),
    complexity: Math.round(clamp(complexity, 5, 24)),
    relevance: Math.round(clamp(relevance, 5, 24)),
    variety: Math.round(variety),
    total: Math.round(total)
  };
}

export function startNpcBattle(opponentId: string, cadence: CadenceMode): BattleState {
  return {
    id: uid("battle"),
    mode: "NPC",
    opponentId,
    cadence,
    roundIndex: 0,
    rounds: [],
    status: "IN_PROGRESS",
    createdAt: Date.now()
  };
}

export function playNpcRound(args: {
  battle: BattleState;
  soul: Soul;
  seed: number;
}): { battle: BattleState; result: RoundResult } {
  const opp = getOpponent(args.battle.opponentId);
  const r = randInt(args.seed);

  const isEndgameBoss = opp.tags.includes("ENDGAME");
  const opponentKeyword = pick(opp.keywords, r());

  let oppBar = pick(opp.openers, r());
  if (isEndgameBoss && args.battle.roundIndex >= 1) {
    oppBar += ` ${pick(PUNCHLINES.mythic, r())}`;
  }

  const lastBars = args.battle.rounds.map((x) => x.yourBar);

  const yourGen = generateBar({
    seed: args.seed ^ 0x9e3779b9,
    soul: args.soul,
    opponent: opp,
    cadence: args.battle.cadence,
    opponentKeyword,
    lastBars
  });

  const yourStats = deriveStats(args.soul).total;
  const oppStats = isEndgameBoss
    ? {
        flow: clamp(opp.base.flow + 6, 0, 100),
        aggression: clamp(opp.base.aggression + 6, 0, 100),
        complexity: clamp(opp.base.complexity + 6, 0, 100),
        presence: clamp(opp.base.presence + 6, 0, 100)
      }
    : opp.base;

  const yourScore = judgeBar({
    bar: yourGen.bar,
    cadence: args.battle.cadence,
    stats: yourStats,
    opponentKeyword,
    lastBars
  });

  const oppScore = judgeBar({
    bar: oppBar,
    cadence: args.battle.cadence,
    stats: oppStats,
    opponentKeyword,
    lastBars: args.battle.rounds.map((x) => x.oppBar)
  });

  const winner = yourScore.total > oppScore.total ? "YOU" : yourScore.total < oppScore.total ? "OPP" : "TIE";

  const result: RoundResult = { oppBar, yourBar: yourGen.bar, oppScore, yourScore, winner };

  const next: BattleState = {
    ...args.battle,
    roundIndex: args.battle.roundIndex + 1,
    rounds: [...args.battle.rounds, result],
    status: args.battle.roundIndex + 1 >= 3 ? "COMPLETE" : "IN_PROGRESS"
  };

  return { battle: next, result };
}

export function xpForWin(winner: "YOU" | "OPP" | "TIE", tier: number): number {
(winner: "YOU" | "OPP" | "TIE", tier: number): number {
  const base = tier * 20;
  if (winner === "YOU") return base + 18;
  if (winner === "TIE") return base + 8;
  return base + 3;
}

export function mmrDelta(winner: "YOU" | "OPP" | "TIE", tier: number): number {
  if (winner === "YOU") return 10 + tier * 2;
  if (winner === "TIE") return 3;
  return -6 - tier;
}

export function levelUpIfNeeded(soul: Soul): Soul {
  const nextLevelXp = (lvl: number) => 60 + lvl * 40;
  let s = { ...soul };
  while (s.xp >= nextLevelXp(s.level)) {
    const nextLevel = s.level + 1;
    s = {
      ...s,
      xp: s.xp - nextLevelXp(s.level),
      level: nextLevel,
      traitPoints: s.traitPoints + 1,
      evoStage: nextLevel === 5 || nextLevel === 10 || nextLevel === 15 ? s.evoStage + 1 : s.evoStage
    };
  }
  return s;
}

export function lootDrop(seed: number, tier: number): { mats: number; shardId?: ShardDef['id'] } {
  const r = randInt(seed);
  const mats = 8 + tier * 6 + Math.floor(r() * 6);
  const roll = r();
  const rarity = rarityRoll(roll);
  const pool = SHARDS.filter((s) => {
    if (tier <= 1) return s.rarity === "COMMON" || s.rarity === "RARE";
    if (tier === 2) return s.rarity !== "MYTHIC";
    return true;
  }).filter((s) => s.rarity === rarity);

  const picked = pool.length ? pick(pool, r()) : undefined;
  return { mats, shardId: picked?.id };
}

export function lootDropBoss(
  seed: number,
  bossId: string
): { mats: number; shardId: ShardDef["id"]; isBossLoot: true } {
  const r = randInt(seed);
  const mats = 80 + Math.floor(r() * 41); // 80–120 inclusive

  const bossShardMap: Record<string, ShardDef["id"]> = {
    void_architect: "void_recursion",
    entropy_overseer: "entropy_catalyst",
    signal_reaper: "signal_hijack"
  };

  const shardId = bossShardMap[bossId] ?? "void_recursion";
  return { mats, shardId, isBossLoot: true };
}
