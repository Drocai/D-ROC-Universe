export type Rarity = "COMMON" | "RARE" | "EPIC" | "MYTHIC";
export type NodeType = "TRAIN" | "BATTLE" | "SHOP" | "REST" | "BOSS";
export type CadenceMode = "STANDARD" | "HALF_TIME" | "DOUBLE_TIME";

export type StatBlock = {
  flow: number;
  aggression: number;
  complexity: number;
  presence: number;
};

export type TraitId =
  | "INTERNAL_RHYME"
  | "CALLBACK"
  | "PUNCHLINE_PACK"
  | "BREATH_CONTROL"
  | "DOUBLE_TIME_READY"
  | "LEXICON_UPLINK";

export type TraitDef = {
  id: TraitId;
  name: string;
  desc: string;
  mods?: Partial<StatBlock>;
};

export type ShardId =
  | "agg_scorched"
  | "vocab_darkweb"
  | "flow_tachyon"
  | "presence_anthem"
  | "complexity_fractal"
  | "flow_metronome"
  | "void_recursion"
  | "entropy_catalyst"
  | "signal_hijack";


export type ShardDef = {
  id: ShardId;
  name: string;
  rarity: Rarity;
  tags: string[];
  mods: Partial<StatBlock>;
};

export type Soul = {
  id: string;
  name: string;
  level: number;
  xp: number;
  mmr: number;
  evoStage: number;
  base: StatBlock;
  traitPoints: number;
  traits: TraitId[];
  cadenceUnlocked: CadenceMode[];
  equippedShards: ShardId[];
  signatureWords: string[];
  signaturePhrases: string[];
  themeWeights: Record<string, number>;
};

export type Inventory = {
  shards: Record<ShardId, number>;
  mats: number;
};

export type Opponent = {
  id: string;
  name: string;
  tier: 1 | 2 | 3 | 4;
  base: StatBlock;
  tags: string[];
  openers: string[];
  keywords: string[];
};

export type BossId = "void_architect" | "entropy_overseer" | "signal_reaper";

export type JudgeBreakdown = {
  flow: number;
  aggression: number;
  complexity: number;
  relevance: number;
  variety: number;
  total: number;
};

export type RoundResult = {
  oppBar: string;
  yourBar: string;
  oppScore: JudgeBreakdown;
  yourScore: JudgeBreakdown;
  winner: "YOU" | "OPP" | "TIE";
};

export type BattleState = {
  id: string;
  mode: "NPC" | "FRIEND";
  opponentId: string;
  cadence: CadenceMode;
  roundIndex: number;
  rounds: RoundResult[];
  status: "IN_PROGRESS" | "COMPLETE";
  createdAt: number;
};

export type ExploreNode = {
  idx: number;
  type: NodeType;
  label: string;
  seed: number;
  completed: boolean;
};

export type ExploreRun = {
  id: string;
  regionId: string;
  regionName: string;
  nodes: ExploreNode[];
  cursor: number;
  startedAt: number;
  completedAt?: number;
};

export type TurnCode = {
  v: 1;
  battleId: string;
  createdAt: number;
  from: { soulName: string; soulSnapshot: Pick<Soul, "name" | "level" | "evoStage"> };
  to: { hint?: string };
  context: {
    round: number;
    cadence: CadenceMode;
    opponentKeyword: string;
  };
  payload: {
    opener: string;
    lastBar?: string;
    lastScore?: JudgeBreakdown;
  };
};
