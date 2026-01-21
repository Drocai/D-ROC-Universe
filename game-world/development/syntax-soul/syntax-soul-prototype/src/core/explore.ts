import { ExploreNode, ExploreRun, NodeType } from "./types";
import { pick, randInt, uid } from "./util";

const REGIONS = [
  { id: "rust_district", name: "RUST DISTRICT", weights: { TRAIN: 0.25, BATTLE: 0.45, SHOP: 0.15, REST: 0.1, BOSS: 0.05 } },
  { id: "neon_arcade", name: "NEON ARCADE", weights: { TRAIN: 0.2, BATTLE: 0.5, SHOP: 0.15, REST: 0.05, BOSS: 0.1 } }
] as const;

function rollType(r: number, w: Record<NodeType, number>): NodeType {
  let t = r;
  const entries: [NodeType, number][] = Object.entries(w) as any;
  for (const [k, p] of entries) {
    t -= p;
    if (t <= 0) return k;
  }
  return "BATTLE";
}

export function newRun(seed: number): ExploreRun {
  const r = randInt(seed);
  const region = pick([...REGIONS], r());
  const nodes: ExploreNode[] = Array.from({ length: 12 }).map((_, idx) => {
    const type = idx === 11 ? "BOSS" : rollType(r(), region.weights as any);
    const label =
      type === "TRAIN" ? "GYM NODE" :
      type === "BATTLE" ? "ARENA NODE" :
      type === "SHOP" ? "BLACK MARKET" :
      type === "REST" ? "COOLDOWN BAY" :
      "BOSS GATE";

    return { idx, type, label, seed: Math.floor(r() * 1e9), completed: false };
  });

  nodes[0].type = "BATTLE";
  nodes[0].label = "ARENA NODE";

  return {
    id: uid("run"),
    regionId: region.id,
    regionName: region.name,
    nodes,
    cursor: 0,
    startedAt: Date.now()
  };
}

export function currentNode(run: ExploreRun): ExploreNode | null {
  return run.nodes[run.cursor] ?? null;
}

export function completeNode(run: ExploreRun): ExploreRun {
  const nodes = run.nodes.map((n) => (n.idx === run.cursor ? { ...n, completed: true } : n));
  const nextCursor = Math.min(run.cursor + 1, nodes.length - 1);
  const done = nextCursor === run.cursor;
  return { ...run, nodes, cursor: done ? run.cursor : nextCursor, completedAt: done ? Date.now() : undefined };
}
