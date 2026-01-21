import { CadenceMode, Opponent, ShardDef, TraitDef } from "./types";

export const TRAITS: TraitDef[] = [
  { id: "INTERNAL_RHYME", name: "Internal Rhyme", desc: "Boost flow; increases internal rhyme chance.", mods: { flow: 8 } },
  { id: "CALLBACK", name: "Callback", desc: "Boost relevance; stronger opponent keyword callbacks.", mods: { presence: 6 } },
  { id: "PUNCHLINE_PACK", name: "Punchline Pack", desc: "Boost aggression; unlocks harder closers.", mods: { aggression: 10 } },
  { id: "BREATH_CONTROL", name: "Breath Control", desc: "Stabilizes flow; reduces variety penalty.", mods: { flow: 5, presence: 4 } },
  { id: "DOUBLE_TIME_READY", name: "Double-Time Ready", desc: "Unlocks double-time cadence mode.", mods: { flow: 6 } },
  { id: "LEXICON_UPLINK", name: "Lexicon Uplink", desc: "Boost complexity; unlocks denser word packs.", mods: { complexity: 10 } }
];

export const SHARDS: ShardDef[] = [
  { id: "agg_scorched", name: "Scorched Earth", rarity: "RARE", tags: ["AGGRO", "ROAST"], mods: { aggression: 18, complexity: -4 } },
  { id: "vocab_darkweb", name: "Webster's Dark-Web", rarity: "RARE", tags: ["LEXICON"], mods: { complexity: 18, aggression: -3 } },
  { id: "flow_tachyon", name: "Tachyon Tongue", rarity: "EPIC", tags: ["FLOW"], mods: { flow: 22 } },
  { id: "presence_anthem", name: "Anthem Core", rarity: "COMMON", tags: ["PRESENCE"], mods: { presence: 12 } },
  { id: "complexity_fractal", name: "Fractal Syntax", rarity: "EPIC", tags: ["LEXICON", "TECH"], mods: { complexity: 22, flow: -2 } },
  { id: "flow_metronome", name: "Metronome Driver", rarity: "COMMON", tags: ["FLOW"], mods: { flow: 10, presence: 4 } }
];

// BOSS-EXCLUSIVE SHARDS (MYTHIC TIER) — DROP ONLY
export const BOSS_SHARDS: ShardDef[] = [
  {
    id: "void_recursion",
    name: "Void Recursion Core",
    rarity: "MYTHIC",
    tags: ["VOID", "BOSS"],
    mods: { complexity: 28, flow: -8, presence: 18 }
  },
  {
    id: "entropy_catalyst",
    name: "Entropy Catalyst",
    rarity: "MYTHIC",
    tags: ["CHAOS", "BOSS"],
    mods: { aggression: 26, complexity: 12, flow: -6 }
  },
  {
    id: "signal_hijack",
    name: "Signal Hijack Module",
    rarity: "MYTHIC",
    tags: ["AGGRO", "BOSS"],
    mods: { aggression: 32, presence: 14, complexity: -10 }
  }
];

export const ALL_SHARDS: ShardDef[] = [...SHARDS, ...BOSS_SHARDS];

export const CADENCE: { id: CadenceMode; name: string; rate: number; desc: string }[] = [
  { id: "STANDARD", name: "Standard", rate: 1.05, desc: "Balanced cadence." },
  { id: "HALF_TIME", name: "Half-Time", rate: 0.92, desc: "Heavier pocket, more presence." },
  { id: "DOUBLE_TIME", name: "Double-Time", rate: 1.55, desc: "Fast delivery, higher flow ceiling." }
];

const BASE_OPPONENTS: Opponent[] = [
  {
    id: "latency_wraith",
    name: "Latency Wraith",
    tier: 1,
    base: { flow: 24, aggression: 18, complexity: 16, presence: 18 },
    tags: ["FLOW", "GHOST"],
    keywords: ["lag", "packet", "delay", "jitter"],
    openers: [
      "Your bars buffer like bad Wi-Fi — I’m the signal, you the glitch.",
      "I move in silence; you stall in public — watch your rhythm switch.",
      "You talk speed but you choke — I’m the sprint, you the hitch."
    ]
  },
  {
    id: "regex_witch",
    name: "Regex Witch",
    tier: 2,
    base: { flow: 18, aggression: 22, complexity: 30, presence: 18 },
    tags: ["LEXICON", "ARCANE"],
    keywords: ["pattern", "match", "capture", "token"],
    openers: [
      "I parse your whole persona — one pattern, one match, you’re done.",
      "You spit noise; I spit structure — capture groups, now run.",
      "Your syntax breaks on contact — mine compiles like a gun."
    ]
  },
  {
    id: "kernel_reaper",
    name: "Kernel Reaper",
    tier: 3,
    base: { flow: 22, aggression: 34, complexity: 26, presence: 24 },
    tags: ["BOSS", "AGGRO"],
    keywords: ["root", "privilege", "kernel", "system"],
    openers: [
      "I got root in your rhythm — privilege escalates when I speak.",
      "Kernel-level killer — your framework trembles, your firewall weak.",
      "I reboot your whole legacy — you crash, then you leak."
    ]
  }
];

export const BOSS_OPPONENTS: Opponent[] = [
  {
    id: "void_architect",
    name: "Void Architect",
    tier: 4,
    base: { flow: 38, aggression: 42, complexity: 44, presence: 36 },
    tags: ["BOSS", "VOID", "ENDGAME"],
    keywords: ["construct", "recursion", "paradox", "null"],
    openers: [
      "I architect the void — your patterns dissolve before compilation.",
      "Recursion loops your logic — I trap you in null reference hell.",
      "Your syntax breaks on paradox — I am the unsolvable proof.",
      "I compile the impossible — your runtime crashes on entry.",
      "Null pointer to your legacy — I deallocate your whole namespace."
    ]
  },
  {
    id: "entropy_overseer",
    name: "Entropy Overseer",
    tier: 4,
    base: { flow: 42, aggression: 38, complexity: 40, presence: 40 },
    tags: ["BOSS", "CHAOS", "ENDGAME"],
    keywords: ["decay", "chaos", "disorder", "collapse"],
    openers: [
      "I orchestrate decay — your structure crumbles into static.",
      "Chaos theory personified — I turn your order into noise.",
      "Your framework collapses under entropy — I am the heat death.",
      "Disorder is my language — you speak in fragile patterns.",
      "I unravel your syntax one bit at a time — irreversible."
    ]
  },
  {
    id: "signal_reaper",
    name: "Signal Reaper",
    tier: 4,
    base: { flow: 44, aggression: 46, complexity: 38, presence: 42 },
    tags: ["BOSS", "AGGRO", "ENDGAME"],
    keywords: ["terminate", "sever", "broadcast", "override"],
    openers: [
      "I terminate signals mid-flight — your broadcast dies in transit.",
      "Override complete — I sever your connection at the root.",
      "I reap the airwaves — your frequency gets flatlined.",
      "Signal hijacked — I broadcast your defeat on all channels.",
      "Root access granted — I delete your transmission in real time."
    ]
  }
];

export const OPPONENTS: Opponent[] = [...BASE_OPPONENTS, ...BOSS_OPPONENTS];
