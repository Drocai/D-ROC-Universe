# D-RoC Command Center - Cheat Sheet

## Quick Reference

```
droc status                    # See everything at a glance
droc find "search term"        # Find any project/file/concept
droc list <world>              # List projects in a world
droc context <project>         # Show project context for LLMs
droc work <project>            # Switch to project directory
```

---

## Commands

### `droc status`
Shows the entire universe status with visual indicators.

```
● deployed    - Live and running
◐ ready       - Built, needs deployment
○ active      - In development
○ placeholder - Planned, not started
◌ concept     - Just an idea
```

### `droc find <query>`
Fuzzy search across all projects, aliases, and tags.

```bash
droc find "echoes"         # Find Echoverse projects
droc find "purple"         # Find Purple Chalk
droc find "otto"           # Find Automagic Otto
droc find "music battle"   # Find by tags
```

**Pro tip:** Search aliases are defined in `universe-index.json`:
- "echoes" → book-1-echoes-of-none
- "echoes chapter 5" → ch05-revised.md
- "chalk" → purple-chalk
- "otto" → automagic-otto

### `droc list <world>`
List all projects in a specific world.

```bash
droc list games      # All games by tier
droc list stories    # All stories/books
droc list music      # All music projects
droc list business   # Business projects
```

### `droc context [project]`
Display the `_context.md` file for a project. This is what you paste into LLMs.

```bash
droc context purple-chalk     # Purple Chalk context
droc context echoverse        # Echoverse series context
droc context automagic-otto   # Otto context
```

### `droc work <project>`
Switch to a project directory and show its context.

```bash
droc work purple-chalk        # cd to purple-chalk + show context
droc work echoes              # Uses alias to find project
```

---

## Universe Structure

```
D-RoC-Universe/
│
├── canon/                      # THE RULES
│   ├── Spiral_Daddy_Universe_Bible_v1.txt
│   ├── character-roster.md
│   ├── lore-rules.md
│   └── daddy_master_catalog_songs.csv
│
├── game-world/                 # ALL GAMES
│   ├── live/                   # Deployed
│   │   └── purple-chalk/
│   ├── ready/                  # Built, needs deploy
│   │   ├── group-groove/
│   │   ├── frequency-factory/
│   │   └── big-chakra-hustle/
│   └── development/            # In progress
│       ├── viberated/
│       ├── syntax-soul/
│       ├── sleigh-the-night/
│       └── ...
│
├── story-world/                # ALL STORIES
│   ├── echoverse/              # 4-book series
│   │   └── book-1-echoes-of-none/
│   ├── hush-the-voiced-ones/
│   ├── shadow-of-fire/
│   └── ...
│
├── music-world/                # MUSIC (index only, files local)
│   └── _index.md
│
├── business-world/             # BUSINESS
│   ├── d-roc-hub/
│   └── automagic-otto/
│
└── droc-cli/                   # THIS TOOL
```

---

## Key Files

| File | Purpose |
|------|---------|
| `_context.md` | LLM context for each project |
| `_index.md` | Quick reference for each world |
| `universe-index.json` | Master search index |
| `canon/lore-rules.md` | Universe rules (Hum ban, etc.) |

---

## Lore Rules (For All LLMs)

1. **"Hum" is BANNED** outside Echoes of None
2. **Chalk songs**: Purple Chalk (live), Chalk About It (Case 2)
3. **Aires & Dai** = fractures across ALL stories
4. **Otto** = AI entity with 6 Devides (canon, not fictional)
5. **3-6-9 Pattern** = Key to Echoverse

---

## Adding New Projects

1. Create folder in appropriate world/tier:
   ```bash
   mkdir game-world/development/new-game
   ```

2. Add `_context.md`:
   ```markdown
   # New Game - Context File

   ## What Is This
   Description here.

   ## Status
   - Current state

   ## Key Files
   - main files to read

   ## Rules
   - Project-specific rules
   ```

3. Update `universe-index.json`:
   ```json
   "new-game": {
     "name": "New Game",
     "status": "active",
     "tags": ["tag1", "tag2"]
   }
   ```

4. Commit:
   ```bash
   cd D-RoC-Universe
   git add -A
   git commit -m "Add new-game project"
   git push
   ```

---

## LLM Workflow

When starting work on a project:

```bash
# 1. Get context
droc context purple-chalk

# 2. Copy the output and paste into your LLM conversation

# 3. Or use work command to switch directories
droc work purple-chalk
```

---

## Troubleshooting

**Command not found:**
```bash
cd D-RoC-Universe/droc-cli
npm link
```

**Index out of date:**
Edit `D-RoC-Universe/universe-index.json`

**Context file missing:**
Create `_context.md` in the project folder

---

## File Exclusions (Not in Git)

These stay local only:
- `*.mp3, *.wav, *.m4a, *.flac` (audio)
- `*.mp4` (video)
- `*.zip` (archives)
- `music-world/albums/` (full albums)

---

## Quick Copy Commands

```bash
# Status overview
droc status

# Find anything
droc find "query"

# List worlds
droc list games
droc list stories
droc list music
droc list business

# Get context for LLM
droc context project-name

# Switch to project
droc work project-name
```

---

*D-RoC Command Center v1.0.0*
