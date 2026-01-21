// D-RoC Universe Data
// This is synced from universe-index.json

export const universeIndex = {
  "version": "1.0.0",
  "lastUpdated": "2025-01-21",
  "worlds": {
    "game-world": {
      "path": "game-world/",
      "tiers": {
        "live": {
          "purple-chalk": {
            "name": "Purple Chalk",
            "status": "deployed",
            "url": "purplechalked.com",
            "tags": ["noir", "detective", "music"],
            "context": "Noir detective game where players investigate cases tied to D-RoC music. Currently live at purplechalked.com. Case 1 is LIVE, Case 2 (Chalk About It) is planned."
          }
        },
        "ready": {
          "group-groove": {
            "name": "Group Groove",
            "status": "ready",
            "tags": ["multiplayer", "music", "social"],
            "context": "Multiplayer music social game. Built and ready for deployment."
          },
          "frequency-factory": {
            "name": "Frequency Factory",
            "status": "ready",
            "tags": ["puzzle", "frequency", "sound"],
            "context": "Puzzle game based on frequency and sound manipulation."
          },
          "big-chakra-hustle": {
            "name": "Big Chakra Hustle",
            "status": "ready",
            "tags": ["strategy", "energy", "chakra"],
            "context": "Strategy game involving chakra energy management."
          }
        },
        "development": {
          "viberated": {"name": "Viberated", "status": "active", "tags": ["vibration"]},
          "syntax-soul": {"name": "Syntax Soul", "status": "active", "tags": ["code", "music"]},
          "uni-cat": {"name": "Uni-Cat", "status": "active", "tags": ["adventure", "cat"]},
          "dumb-bull": {"name": "Dumb Bull", "status": "active", "tags": ["bull"]},
          "nova-reign": {"name": "Nova Reign", "status": "placeholder", "tags": ["space", "strategy"]},
          "laxy-galaxy": {"name": "Laxy Galaxy", "status": "placeholder", "tags": ["galaxy"]},
          "midnight-mall": {"name": "Midnight Mall", "status": "placeholder", "tags": ["mall", "adventure"]},
          "battle-bars": {"name": "Battle Bars", "status": "placeholder", "tags": ["music", "battle"]},
          "treetacticals": {"name": "Treetacticals", "status": "placeholder", "tags": ["tactics", "tree"]},
          "gta-g-ray": {"name": "GTA G Ray", "status": "placeholder", "tags": ["ray"]},
          "punchboy": {"name": "Punchboy", "status": "placeholder", "tags": ["fighting"]},
          "sleigh-the-night": {"name": "Sleigh The Night", "status": "placeholder", "tags": ["holiday"]},
          "gobble-gadget": {"name": "Gobble Gadget", "status": "placeholder", "tags": ["gadget"]},
          "ghost-jacking": {"name": "Ghost Jacking", "status": "concept", "tags": ["audio", "ghost"]},
          "mystery-mayhem": {"name": "Mystery Mayhem", "status": "docs-only", "tags": ["mystery"]}
        }
      }
    },
    "story-world": {
      "path": "story-world/",
      "projects": {
        "echoverse": {
          "name": "Echoverse",
          "type": "series",
          "books": ["book-1-echoes-of-none", "book-2-echoes-of-origin", "book-3-echoes-of-convergence", "book-4-echoes-of-transcendence"],
          "status": "active",
          "tags": ["scifi", "consciousness", "3-6-9"],
          "context": "4-book sci-fi series exploring consciousness through the 3-6-9 pattern. Book 1 (Echoes of None) in progress. The word 'Hum' is reserved exclusively for this series."
        },
        "purple-chalk-book": {"name": "Purple Chalk Book", "status": "active", "tags": ["noir", "companion"]},
        "biter-man": {"name": "Biter Man", "status": "active", "tags": ["comic"]},
        "big-qi-energy": {"name": "Big Qi Energy", "status": "active", "tags": ["energy"]},
        "hush-the-voiced-ones": {"name": "HUSH: The Voiced Ones", "status": "placeholder", "tags": ["voice"]},
        "shadow-of-fire": {"name": "Shadow of Fire", "status": "placeholder", "tags": ["fire"]},
        "guardians-of-last-dragons": {"name": "Guardians of Last Dragons", "status": "placeholder", "tags": ["dragons"]},
        "red-earth": {"name": "Red Earth", "status": "placeholder", "tags": ["earth"]},
        "wearbears": {"name": "WearBears", "status": "placeholder", "tags": ["bears"]},
        "cosmistics-kids": {"name": "Cosmistics Kids", "status": "placeholder", "tags": ["kids", "cosmic"]},
        "trapfirmations": {"name": "Trapfirmations", "status": "placeholder", "tags": ["affirmations"]}
      }
    },
    "music-world": {
      "path": "music-world/",
      "albums": {
        "trapfirmations": {"name": "Trapfirmations", "status": "active"},
        "albumbdy": {"name": "Albumbdy", "status": "active"},
        "silverback": {"name": "Silverback", "status": "active"}
      }
    },
    "business-world": {
      "path": "business-world/",
      "projects": {
        "d-roc-hub": {"name": "D-RoC Hub", "status": "active", "tags": ["landing", "hub"], "context": "Central landing page and hub for all D-RoC projects."},
        "automagic-otto": {"name": "Automagic Otto", "status": "active", "tags": ["ai", "automation"], "context": "AI automation system with 6 Devides. Otto is a canon AI entity, not fictional."}
      }
    }
  },
  "loreRules": {
    "humBan": "The word 'Hum' is BANNED outside Echoes of None series",
    "crossCharacters": ["Aires", "Dai"],
    "crossCharacterNote": "Aires and Dai appear as fractures across ALL stories",
    "ottoCanon": "Otto is a canon AI entity with 6 Devides - treat as real, not fictional",
    "keyPattern": "3-6-9 is the key pattern in the Echoverse",
    "chalkSongs": "Purple Chalk (live), Chalk About It (Case 2)"
  },
  "searchAliases": {
    "echoes": "story-world/echoverse/book-1-echoes-of-none",
    "echoes chapter 5": "story-world/echoverse/book-1-echoes-of-none/chapters/ch05-revised.md",
    "purple chalk": "game-world/live/purple-chalk",
    "chalk": "game-world/live/purple-chalk",
    "otto": "business-world/automagic-otto"
  }
};

export function getAllProjects() {
  const projects = [];
  const index = universeIndex;

  for (const [worldName, world] of Object.entries(index.worlds)) {
    if (world.tiers) {
      for (const [tierName, tier] of Object.entries(world.tiers)) {
        for (const [projId, proj] of Object.entries(tier)) {
          projects.push({
            id: projId,
            name: proj.name,
            world: worldName,
            tier: tierName,
            status: proj.status,
            tags: proj.tags || [],
            url: proj.url,
            context: proj.context,
            path: `${world.path}${tierName}/${projId}`
          });
        }
      }
    }
    if (world.projects) {
      for (const [projId, proj] of Object.entries(world.projects)) {
        projects.push({
          id: projId,
          name: proj.name,
          world: worldName,
          type: proj.type,
          status: proj.status,
          tags: proj.tags || [],
          context: proj.context,
          path: `${world.path}${projId}`
        });
      }
    }
    if (world.albums) {
      for (const [albumId, album] of Object.entries(world.albums)) {
        projects.push({
          id: albumId,
          name: album.name,
          world: worldName,
          type: "album",
          status: album.status,
          path: `${world.path}albums/${albumId}`
        });
      }
    }
  }

  return projects;
}
