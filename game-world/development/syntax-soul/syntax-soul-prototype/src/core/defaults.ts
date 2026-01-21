import { Inventory, Soul } from "./types";
import { uid } from "./util";

export function defaultSoul(): Soul {
  return {
    id: uid("soul"),
    name: "SYNTAX_SOUL",
    level: 1,
    xp: 0,
    mmr: 1000,
    evoStage: 0,
    traitPoints: 0,
    base: { flow: 20, aggression: 20, complexity: 20, presence: 20 },
    traits: [],
    cadenceUnlocked: ["STANDARD", "HALF_TIME"],
    equippedShards: ["presence_anthem"],
    signatureWords: ["neon", "kernel"],
    signaturePhrases: ["// SYSTEMS ONLINE"],
    themeWeights: { tech: 60, street: 20, cosmic: 20 }
  };
}

export function defaultInventory(): Inventory {
  return {
    shards: {
      agg_scorched: 0,
      vocab_darkweb: 0,
      flow_tachyon: 0,
      presence_anthem: 1,
      complexity_fractal: 0,
      flow_metronome: 1,
      void_recursion: 0,
      entropy_catalyst: 0,
      signal_hijack: 0
    },
    mats: 40
  };
}
