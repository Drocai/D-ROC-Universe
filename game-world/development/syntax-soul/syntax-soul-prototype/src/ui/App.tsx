import React, { useMemo, useState } from "react";
import { defaultInventory, defaultSoul } from "../core/defaults";
import { ExploreRun, ShardId, TraitId, TurnCode } from "../core/types";
import { useLocalStorageState } from "./hooks";
import {
  deriveStats,
  generateBar,
  getOpponent,
  getShardDef,
  getTraitDef,
  judgeBar,
  levelUpIfNeeded,
  lootDrop,
  lootDropBoss,
  mmrDelta,
  playNpcRound,
  startNpcBattle,
  xpForWin
} from "../core/engine";
import { ALL_SHARDS, CADENCE, OPPONENTS, TRAITS } from "../core/data";
import { completeNode, currentNode, newRun } from "../core/explore";
import { now, randInt } from "../core/util";
import { canSpeak, speakBar } from "./speech";

type Screen = "HUB" | "SOUL" | "TRAIN" | "EXPLORE" | "ARENA" | "FRIENDS";

type SaveState = {
  soul: ReturnType<typeof defaultSoul>;
  inventory: ReturnType<typeof defaultInventory>;
  run: ExploreRun | null;
  lastBattleSummary?: { lastOpponent: string; lastResult: string; lastLoot?: string };
};

const SAVE_KEY = "syntax_soul_save_v1";

function jsonPretty(x: unknown): string {
  return JSON.stringify(x, null, 2);
}

export default function App() {
  const [save, setSave, resetSave] = useLocalStorageState<SaveState>(SAVE_KEY, {
    soul: defaultSoul(),
    inventory: defaultInventory(),
    run: null
  });

  const [screen, setScreen] = useState<Screen>("HUB");
  const [logs, setLogs] = useState<string[]>(["> SYSTEM ONLINE", "> WAITING FOR ARCHITECT"]);
  const [ttsEnabled, setTtsEnabled] = useState<boolean>(true);

  const soul = save.soul;
  const inv = save.inventory;
  const derived = useMemo(() => deriveStats(soul).total, [soul]);

  const addLog = (m: string) => setLogs((p) => [m, ...p].slice(0, 6));

  const updateSoul = (patch: Partial<typeof soul>) => setSave({ ...save, soul: { ...save.soul, ...patch } });
  const updateInv = (patch: Partial<typeof inv>) => setSave({ ...save, inventory: { ...save.inventory, ...patch } });

  const addXp = (xp: number) => {
    const next = levelUpIfNeeded({ ...soul, xp: soul.xp + xp });
    if (next.level !== soul.level) addLog(`> LEVEL UP: ${soul.level} → ${next.level} (Trait +1)`);
    setSave({ ...save, soul: next });
  };

  const toggleShard = (id: ShardId) => {
    const count = inv.shards[id] ?? 0;
    if (count <= 0 && !soul.equippedShards.includes(id)) {
      addLog("> NO INVENTORY: shard not owned");
      return;
    }
    const equipped = soul.equippedShards.includes(id)
      ? soul.equippedShards.filter((x) => x !== id)
      : [...soul.equippedShards, id].slice(0, 3);

    updateSoul({ equippedShards: equipped });
    addLog(`> SHARD ${equipped.includes(id) ? "EQUIPPED" : "REMOVED"}: ${getShardDef(id).name}`);
  };

  const buyShard = (id: ShardId) => {
  const def = getShardDef(id);
  if (def.tags.includes("BOSS")) {
    addLog("> BOSS DROP ONLY");
    return;
  }

  const rarity = def.rarity;
  const cost = rarity === "COMMON" ? 18 : rarity === "RARE" ? 35 : 60;
  if (inv.mats < cost) {
    addLog("> INSUFFICIENT MATS");
    return;
  }
  updateInv({
    mats: inv.mats - cost,
    shards: { ...inv.shards, [id]: (inv.shards[id] ?? 0) + 1 }
  });
  addLog(`> ACQUIRED: ${def.name}`);
};

  const spendTrait = (id: TraitId) => {
    if (soul.traitPoints <= 0) return;
    if (soul.traits.includes(id)) return;
    const t = getTraitDef(id);
    const nextTraits = [...soul.traits, id];
    const cadenceUnlocked =
      id === "DOUBLE_TIME_READY" && !soul.cadenceUnlocked.includes("DOUBLE_TIME")
        ? [...soul.cadenceUnlocked, "DOUBLE_TIME"]
        : soul.cadenceUnlocked;

    updateSoul({ traits: nextTraits, traitPoints: soul.traitPoints - 1, cadenceUnlocked });
    addLog(`> TRAIT INSTALLED: ${t.name}`);
  };

  const trainWordFuel = (wordsRaw: string) => {
    const words = wordsRaw
      .split(/[\s,]+/)
      .map((w) => w.trim().toLowerCase())
      .filter(Boolean)
      .slice(0, 6);

    if (!words.length) return;

    const merged = Array.from(new Set([...soul.signatureWords, ...words])).slice(0, 40);
    updateSoul({ signatureWords: merged });
    addXp(28);
    addLog(`> WORD FUEL: learned ${words.join(", ")}`);
  };

  const trainCadenceGym = (mode: string) => {
    if (!soul.cadenceUnlocked.includes(mode as any)) {
      addLog("> CADENCE LOCKED");
      return;
    }
    addXp(mode === "DOUBLE_TIME" ? 32 : 22);
    addLog(`> CADENCE DRILL: ${mode}`);
  };

  const ensureRun = () => {
    if (save.run) return;
    const seed = Math.floor(Math.random() * 1e9);
    setSave({ ...save, run: newRun(seed) });
    addLog("> RUN STARTED");
  };

  const progressRun = () => {
    if (!save.run) return;
    const node = currentNode(save.run);
    if (!node) return;

    if (!node.completed) {
      addLog("> COMPLETE CURRENT NODE FIRST");
      return;
    }
    setSave({ ...save, run: completeNode(save.run) });
  };

  const completeCurrentNode = () => {
    if (!save.run) return;
    const node = currentNode(save.run);
    if (!node) return;
    if (node.completed) return;

    const r = randInt(node.seed);
    if (node.type === "TRAIN") {
      addXp(20 + Math.floor(r() * 10));
      addLog("> NODE COMPLETE: TRAIN");
    } else if (node.type === "REST") {
      addLog("> NODE COMPLETE: REST (no-op in v1 slice)");
    } else if (node.type === "SHOP") {
      const mats = 20 + Math.floor(r() * 20);
      updateInv({ mats: inv.mats + mats });
      addLog(`> NODE COMPLETE: SHOP SCORE (+${mats} mats)`);
    } else if (node.type === "BATTLE" || node.type === "BOSS") {
  if (node.type === "BOSS") {
    const bossPool = OPPONENTS.filter((o) => o.tags.includes("BOSS") && o.tags.includes("ENDGAME"));
    const r = randInt(node.seed);
    const boss = bossPool[Math.floor(r() * bossPool.length)];
    if (boss) {
      setNpcOpponentId(boss.id);
      if (soul.cadenceUnlocked.includes("HALF_TIME")) setNpcCadence("HALF_TIME");
      addLog(`> BOSS GATE DETECTED: ${boss.name}`);
    }
  }
  setScreen("ARENA");
  addLog("> NODE REQUIRES BATTLE");
  return;
}

    setSave({
      ...save,
      run: { ...save.run, nodes: save.run.nodes.map((n) => (n.idx === save.run!.cursor ? { ...n, completed: true } : n)) }
    });
  };

  const [npcBattle, setNpcBattle] = useState<ReturnType<typeof startNpcBattle> | null>(null);
  const [npcOpponentId, setNpcOpponentId] = useState<string>(OPPONENTS[0].id);
  const [npcCadence, setNpcCadence] = useState<string>("STANDARD");

  const startBattle = () => {
    const cadence = npcCadence as any;
    if (!soul.cadenceUnlocked.includes(cadence)) {
      addLog("> CADENCE LOCKED");
      return;
    }
    const b = startNpcBattle(npcOpponentId, cadence);
    setNpcBattle(b);
    addLog(`> BATTLE START: ${getOpponent(npcOpponentId).name}`);
  };

  const playRound = () => {
    if (!npcBattle || npcBattle.status !== "IN_PROGRESS") return;

    const seed = Math.floor(Math.random() * 1e9);
    const { battle, result } = playNpcRound({ battle: npcBattle, soul, seed });
    setNpcBattle(battle);

    if (ttsEnabled && canSpeak()) speakBar(result.yourBar, soul, battle.cadence);

    addLog(`> ROUND ${battle.roundIndex}: ${result.winner === "YOU" ? "WIN" : result.winner === "OPP" ? "LOSS" : "TIE"}`);

    if (battle.status === "COMPLETE") {
      const opp = getOpponent(battle.opponentId);
      const wins = battle.rounds.filter((x) => x.winner === "YOU").length;
      const losses = battle.rounds.filter((x) => x.winner === "OPP").length;
      const outcome = wins > losses ? "YOU" : wins < losses ? "OPP" : "TIE";

      const xp = xpForWin(outcome, opp.tier);
      const delta = mmrDelta(outcome, opp.tier);
      addXp(xp);
      updateSoul({ mmr: Math.max(0, soul.mmr + delta) });

const isBossNode = !!(save.run && currentNode(save.run)?.type === "BOSS");
const isEndgameBoss = getOpponent(battle.opponentId).tags.includes("ENDGAME");

const loot = isBossNode && isEndgameBoss
  ? lootDropBoss(seed ^ 0x51ed, battle.opponentId)
  : lootDrop(seed ^ 0x51ed, opp.tier);

const shardName = loot.shardId ? getShardDef(loot.shardId).name : "";

      updateInv({
        mats: inv.mats + loot.mats,
        shards: loot.shardId ? { ...inv.shards, [loot.shardId]: (inv.shards[loot.shardId] ?? 0) + 1 } : inv.shards
      });

      if ("isBossLoot" in loot && loot.isBossLoot && outcome === "YOU") {
  addLog(`> BOSS DEFEATED: ${opp.name.toUpperCase()}`);
  addLog(`> MYTHIC LOOT: ${shardName}`);
}

addLog(
  `> REWARD: +${xp} XP, ${delta >= 0 ? "+" : ""}${delta} MMR, +${loot.mats} mats${loot.shardId ? `, shard: ${shardName}` : ""}`
);

      if (save.run) {
        const node = currentNode(save.run);
        if (node && (node.type === "BATTLE" || node.type === "BOSS")) {
          setSave({
            ...save,
            run: { ...save.run, nodes: save.run.nodes.map((n) => (n.idx === save.run.cursor ? { ...n, completed: true } : n)) }
          });
        }
      }
    }
  };

  // FRIEND TURN-CODE (no backend)
  const [turnOut, setTurnOut] = useState<string>("");
  const [turnIn, setTurnIn] = useState<string>("");

  const createChallenge = () => {
    const oppKeyword = "signal";
    const cadence = (soul.cadenceUnlocked.includes("DOUBLE_TIME") ? "DOUBLE_TIME" : "STANDARD") as any;

    const code: TurnCode = {
      v: 1,
      battleId: `friend_${Math.random().toString(16).slice(2)}_${Date.now().toString(16)}`,
      createdAt: now(),
      from: { soulName: soul.name, soulSnapshot: { name: soul.name, level: soul.level, evoStage: soul.evoStage } },
      to: { hint: "Paste this into your friend's FRIENDS tab." },
      context: { round: 1, cadence, opponentKeyword: oppKeyword },
      payload: { opener: "I set the tempo—your whole style gets audited in silence." }
    };

    setTurnOut(jsonPretty(code));
    addLog("> FRIEND CHALLENGE CODE GENERATED");
  };

  const respondToTurn = () => {
    let parsed: TurnCode;
    try {
      parsed = JSON.parse(turnIn) as TurnCode;
    } catch {
      addLog("> INVALID TURN CODE");
      return;
    }
    if (parsed.v !== 1) {
      addLog("> TURN CODE VERSION MISMATCH");
      return;
    }

    const r = randInt(parsed.createdAt ^ soul.level ^ 0xabcdef);
    const opponentKeyword = parsed.context.opponentKeyword || "signal";

    const fakeOpponent = {
      id: "friend_opponent",
      name: parsed.from.soulName,
      tier: 2 as const,
      base: { flow: 20, aggression: 20, complexity: 20, presence: 20 },
      tags: ["FRIEND"],
      keywords: [opponentKeyword],
      openers: [parsed.payload.opener]
    };

    const lastBars = parsed.payload.lastBar ? [parsed.payload.lastBar] : [];
    const { bar } = generateBar({
      seed: Math.floor(r() * 1e9),
      soul,
      opponent: fakeOpponent as any,
      cadence: parsed.context.cadence,
      opponentKeyword,
      lastBars
    });

    const yourStats = deriveStats(soul).total;
    const yourScore = judgeBar({
      bar,
      cadence: parsed.context.cadence,
      stats: yourStats,
      opponentKeyword,
      lastBars
    });

    if (ttsEnabled && canSpeak()) speakBar(bar, soul, parsed.context.cadence);

    const next: TurnCode = {
      v: 1,
      battleId: parsed.battleId,
      createdAt: now(),
      from: { soulName: soul.name, soulSnapshot: { name: soul.name, level: soul.level, evoStage: soul.evoStage } },
      to: { hint: "Send this back. It’s their turn." },
      context: { round: parsed.context.round + 1, cadence: parsed.context.cadence, opponentKeyword },
      payload: { opener: parsed.payload.opener, lastBar: bar, lastScore: yourScore }
    };

    setTurnOut(jsonPretty(next));
    addLog("> TURN RESPONDED — CODE READY TO SEND");
  };

  const nav = (id: Screen) => () => setScreen(id);

  return (
    <div className="app">
      <div className="scanlines" />
      <header className="header">
        <div className="brand">
          <h1>SYNTAX_SOUL // VERTICAL SLICE</h1>
          <div className="tag">Train. Evolve. Explore. Battle. (Local save, no backend)</div>
        </div>
        <div className="row">
          <button className={"btn " + (ttsEnabled ? "hot" : "")} onClick={() => setTtsEnabled((p) => !p)}>
            {ttsEnabled ? "VOICE: ON" : "VOICE: OFF"}
          </button>
          <button
            className="btn danger"
            onClick={() => {
              resetSave();
              setNpcBattle(null);
              addLog("> WIPE SAVE");
            }}
          >
            WIPE
          </button>
        </div>
      </header>

      <div className="row" style={{ marginBottom: 12 }}>
        <button className={"btn " + (screen === "HUB" ? "hot" : "")} onClick={nav("HUB")}>HUB</button>
        <button className={"btn " + (screen === "SOUL" ? "hot" : "")} onClick={nav("SOUL")}>SOUL LAB</button>
        <button className={"btn " + (screen === "TRAIN" ? "hot" : "")} onClick={nav("TRAIN")}>TRAIN</button>
        <button className={"btn " + (screen === "EXPLORE" ? "hot" : "")} onClick={() => { ensureRun(); setScreen("EXPLORE"); }}>EXPLORE</button>
        <button className={"btn " + (screen === "ARENA" ? "hot" : "")} onClick={nav("ARENA")}>ARENA</button>
        <button className={"btn " + (screen === "FRIENDS" ? "hot" : "")} onClick={nav("FRIENDS")}>FRIEND BATTLE</button>
      </div>

      <div className="grid">
        <aside className="panel">
          <h2>SOUL STATUS</h2>
          <div className="kv"><span>Name</span><b>{soul.name}</b></div>
          <div className="kv"><span>Level</span><b>{soul.level} (Evo {soul.evoStage})</b></div>
          <div className="kv"><span>XP</span><b>{soul.xp}</b></div>
          <div className="kv"><span>MMR</span><b>{soul.mmr}</b></div>
          <div className="kv"><span>Trait Points</span><b>{soul.traitPoints}</b></div>

          <div className="hr" />
          <h2>DERIVED STATS</h2>
          <div className="kv"><span>Flow</span><b>{derived.flow}</b></div>
          <div className="kv"><span>Aggression</span><b>{derived.aggression}</b></div>
          <div className="kv"><span>Complexity</span><b>{derived.complexity}</b></div>
          <div className="kv"><span>Presence</span><b>{derived.presence}</b></div>

          <div className="hr" />
          <h2>INVENTORY</h2>
          <div className="kv"><span>Mats</span><b>{inv.mats}</b></div>
          <div className="mini">Owned shards:</div>
          <div className="list" style={{ marginTop: 10 }}>
            {ALL_SHARDS.map((s) => (
              <div key={s.id} className="card">
                <div className="title">
                  <b>{s.name}</b>
                  <span className="pill">{s.rarity}</span>{s.tags.includes("BOSS") ? <span className="pill">BOSS DROP</span> : null}
                </div>
                <div className="mini">Owned: {inv.shards[s.id] ?? 0} | Equipped: {soul.equippedShards.includes(s.id) ? "YES" : "NO"}</div>
                <div className="row" style={{ marginTop: 10 }}>
                  <button className={"btn " + (soul.equippedShards.includes(s.id) ? "hot" : "")} onClick={() => toggleShard(s.id)}>
                    {soul.equippedShards.includes(s.id) ? "UNEQUIP" : "EQUIP"} (slots 3)
                  </button>
                  <button className="btn" onClick={() => buyShard(s.id)}>BUY</button>
                </div>
              </div>
            ))}
          </div>

          <div className="hr" />
          <h2>OPS LOG</h2>
          <div className="mini" style={{ whiteSpace: "pre-wrap" }}>{logs.map((l) => `• ${l}`).join("\n")}</div>
        </aside>

        <main className="panel">
          {screen === "HUB" && (
            <>
              <h2>HUB</h2>
              <div className="row">
                <span className="badge hot">Core Loop: Train → Explore → Battle → Loot → Evolve</span>
                {save.run ? <span className="badge">Active Run: {save.run.regionName}</span> : <span className="badge warn">No active run</span>}
              </div>

              <div className="hr" />
              <div className="card">
                <div className="title"><b>Quick Actions</b><span className="pill">Test Loop</span></div>
                <div className="row" style={{ marginTop: 12 }}>
                  <button className="btn hot" onClick={() => setScreen("TRAIN")}>TRAIN NOW</button>
                  <button className="btn hot" onClick={() => { ensureRun(); setScreen("EXPLORE"); }}>EXPLORE RUN</button>
                  <button className="btn hot" onClick={() => setScreen("ARENA")}>NPC ARENA</button>
                  <button className="btn" onClick={() => setScreen("FRIENDS")}>FRIEND TURN-CODES</button>
                </div>
              </div>
            </>
          )}

          {screen === "SOUL" && (
            <>
              <h2>SOUL LAB</h2>
              <div className="card">
                <div className="title"><b>Identity</b><span className="pill">Persistent</span></div>
                <div className="row" style={{ marginTop: 10 }}>
                  <input className="input" value={soul.name} onChange={(e) => updateSoul({ name: e.target.value.toUpperCase().slice(0, 20) })} />
                  <button className="btn" onClick={() => addLog("> NAME LOCKED")}>LOCK</button>
                </div>
                <div className="mini" style={{ marginTop: 10 }}>
                  Signature words: {soul.signatureWords.slice(0, 12).join(", ")}{soul.signatureWords.length > 12 ? "…" : ""}
                </div>
              </div>

              <div className="hr" />
              <div className="card">
                <div className="title"><b>Traits</b><span className="pill">Trait Points: {soul.traitPoints}</span></div>
                <div className="list" style={{ marginTop: 10 }}>
                  {TRAITS.map((t) => {
                    const owned = soul.traits.includes(t.id);
                    return (
                      <div key={t.id} className="card">
                        <div className="title"><b>{t.name}</b><span className="pill">{owned ? "INSTALLED" : "AVAILABLE"}</span></div>
                        <div className="mini">{t.desc}</div>
                        <div className="row" style={{ marginTop: 10 }}>
                          <button className={"btn " + (owned ? "hot" : "")} disabled={owned || soul.traitPoints <= 0} onClick={() => spendTrait(t.id)}>
                            {owned ? "ACTIVE" : "INSTALL"}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="hr" />
              <div className="card">
                <div className="title"><b>Cadence Modes</b><span className="pill">Unlocked</span></div>
                <div className="row" style={{ marginTop: 10, flexWrap: "wrap" }}>
                  {CADENCE.map((c) => (
                    <span key={c.id} className={"badge " + (soul.cadenceUnlocked.includes(c.id) ? "hot" : "warn")}>
                      {c.name}
                    </span>
                  ))}
                </div>
              </div>
            </>
          )}

          {screen === "TRAIN" && (
            <>
              <h2>TRAINING GYM</h2>

              <div className="card">
                <div className="title"><b>Word Fuel</b><span className="pill">Personalization</span></div>
                <div className="mini">Feed 2–6 words. They become part of your Soul’s signature bank.</div>
                <div className="row" style={{ marginTop: 10 }}>
                  <WordFuel onCommit={trainWordFuel} />
                </div>
              </div>

              <div className="hr" />

              <div className="card">
                <div className="title"><b>Cadence Gym</b><span className="pill">Flow Control</span></div>
                <div className="mini">Run a cadence drill. Double-time requires the trait unlock.</div>
                <div className="row" style={{ marginTop: 10 }}>
                  <select className="input" value={npcCadence} onChange={(e) => setNpcCadence(e.target.value)}>
                    {CADENCE.map((c) => (
                      <option key={c.id} value={c.id} disabled={!soul.cadenceUnlocked.includes(c.id)}>
                        {c.name} {!soul.cadenceUnlocked.includes(c.id) ? "(LOCKED)" : ""}
                      </option>
                    ))}
                  </select>
                  <button className="btn hot" onClick={() => trainCadenceGym(npcCadence)}>RUN</button>
                </div>
              </div>
            </>
          )}

          {screen === "EXPLORE" && (
            <>
              <h2>EXPLORE</h2>
              {!save.run ? (
                <div className="card">
                  <div className="title"><b>No active run</b><span className="pill">Create</span></div>
                  <button className="btn hot" onClick={ensureRun}>START RUN</button>
                </div>
              ) : (
                <>
                  <div className="row">
                    <span className="badge hot">{save.run.regionName}</span>
                    <span className="badge">Node {save.run.cursor + 1}/{save.run.nodes.length}</span>
                  </div>

                  <div className="hr" />

                  <div className="list">
                    {save.run.nodes.map((n) => {
                      const active = n.idx === save.run!.cursor;
                      return (
                        <div key={n.idx} className="card" style={{ borderColor: active ? "rgba(57,255,207,.45)" : undefined }}>
                          <div className="title">
                            <b>#{n.idx + 1} — {n.label}</b>
                            <span className="pill">{n.type}{n.completed ? " ✅" : ""}</span>
                          </div>
                          {active && (
                            <div className="row" style={{ marginTop: 10 }}>
                              <button className="btn hot" onClick={completeCurrentNode}>
                                {n.type === "BATTLE" || n.type === "BOSS" ? "ENTER ARENA" : "COMPLETE NODE"}
                              </button>
                              <button className="btn" onClick={progressRun}>ADVANCE</button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </>
          )}

          {screen === "ARENA" && (
            <>
              <h2>ARENA</h2>
              <div className="row">
                <div className="badge">NPC Opponent</div>
                <select className="input" value={npcOpponentId} onChange={(e) => setNpcOpponentId(e.target.value)}>
                  {OPPONENTS.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name} (Tier {o.tier})
                    </option>
                  ))}
                </select>
                <select className="input" value={npcCadence} onChange={(e) => setNpcCadence(e.target.value)}>
                  {CADENCE.map((c) => (
                    <option key={c.id} value={c.id} disabled={!soul.cadenceUnlocked.includes(c.id)}>
                      {c.name} {!soul.cadenceUnlocked.includes(c.id) ? "(LOCKED)" : ""}
                    </option>
                  ))}
                </select>
                <button className="btn hot" onClick={startBattle}>START</button>
                <button className="btn" onClick={() => setNpcBattle(null)}>RESET</button>
              </div>

              <div className="hr" />

              {!npcBattle ? (
                <div className="card">
                  <div className="title"><b>Ready</b><span className="pill">Best of 3</span></div>
                  <div className="mini">Start a battle to test scoring + loot + progression.</div>
                </div>
              ) : (
                <>
                  <div className="card">
                    <div className="title"><b>{getOpponent(npcBattle.opponentId).name}</b><span className="pill">{npcBattle.status}</span></div>
                    <div className="mini">Cadence: {npcBattle.cadence} | Round: {npcBattle.roundIndex}/3</div>
                    <div className="row" style={{ marginTop: 10 }}>
                      <button className="btn hot" disabled={npcBattle.status !== "IN_PROGRESS"} onClick={playRound}>
                        PLAY ROUND
                      </button>
                    </div>
                  </div>

                  <div className="hr" />

                  <div className="list">
                    {npcBattle.rounds.map((r, i) => (
                      <div key={i} className="card">
                        <div className="title"><b>ROUND {i + 1}</b><span className="pill">{r.winner}</span></div>
                        <div className="mini" style={{ marginTop: 8 }}><b>OPP:</b> {r.oppBar}</div>
                        <div className="mini" style={{ marginTop: 8 }}><b>YOU:</b> {r.yourBar}</div>
                        <div className="row" style={{ marginTop: 10 }}>
                          <ScoreBox label="YOU" s={r.yourScore} />
                          <ScoreBox label="OPP" s={r.oppScore} />
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}

          {screen === "FRIENDS" && (
            <>
              <h2>FRIEND BATTLE // TURN-CODES</h2>
              <div className="card">
                <div className="title"><b>Create Challenge</b><span className="pill">No Backend</span></div>
                <div className="mini">Generate a code, send it to your friend. They paste it and respond. You paste theirs back. Async battle loop.</div>
                <div className="row" style={{ marginTop: 10 }}>
                  <button className="btn hot" onClick={createChallenge}>GENERATE CODE</button>
                </div>
              </div>

              <div className="hr" />

              <div className="card">
                <div className="title"><b>Paste Incoming Turn Code</b><span className="pill">Respond</span></div>
                <textarea className="code" value={turnIn} onChange={(e) => setTurnIn(e.target.value)} placeholder="Paste code here..." />
                <div className="row" style={{ marginTop: 10 }}>
                  <button className="btn hot" onClick={respondToTurn}>GENERATE RESPONSE CODE</button>
                </div>
              </div>

              <div className="hr" />

              <div className="card">
                <div className="title"><b>Outgoing Turn Code</b><span className="pill">Send</span></div>
                <textarea className="code" value={turnOut} readOnly placeholder="Your outgoing code will appear here." />
                <div className="row" style={{ marginTop: 10 }}>
                  <button className="btn" onClick={() => navigator.clipboard.writeText(turnOut)}>COPY</button>
                  <button className="btn" onClick={() => setTurnOut("")}>CLEAR</button>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

function ScoreBox({ label, s }: { label: string; s: { total: number; flow: number; aggression: number; complexity: number; relevance: number; variety: number } }) {
  return (
    <div className="scorebox">
      <div className="l">{label} TOTAL</div>
      <div className="n">{s.total}</div>
      <div className="scorebar">
        <span className="pill">FLOW {s.flow}</span>
        <span className="pill">AGG {s.aggression}</span>
        <span className="pill">COMP {s.complexity}</span>
        <span className="pill">REL {s.relevance}</span>
        <span className="pill">VAR {s.variety}</span>
      </div>
    </div>
  );
}

function WordFuel({ onCommit }: { onCommit: (wordsRaw: string) => void }) {
  const [v, setV] = React.useState("");
  return (
    <>
      <input className="input" value={v} onChange={(e) => setV(e.target.value)} placeholder="e.g. neon kernel ruthless quantum" />
      <button className="btn hot" onClick={() => { onCommit(v); setV(""); }}>
        INJECT
      </button>
    </>
  );
}
