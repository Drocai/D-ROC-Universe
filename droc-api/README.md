# D-RoC Universe API

REST API for accessing the D-RoC Universe from any LLM (ChatGPT, Gemini, etc.)

## Deployment

### Deploy to Vercel (Recommended)

```bash
cd D-RoC-Universe/droc-api
npm i -g vercel
vercel login
vercel --prod
```

Your API will be live at: `https://droc-api.vercel.app`

### Local Development

```bash
vercel dev
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api` | API documentation |
| `GET /api/status` | Universe status overview |
| `GET /api/find?q=<query>` | Search projects |
| `GET /api/context/<project>` | Get project context |
| `GET /api/list/<world>` | List projects (games, stories, music, business) |
| `GET /api/lore` | Universe lore rules |
| `GET /api/full-index` | Full universe index JSON |

## Usage with ChatGPT

1. Deploy the API to Vercel
2. In ChatGPT, enable web browsing
3. Ask ChatGPT to browse to your API endpoints

Example prompts:
- "Browse to https://droc-api.vercel.app/api/status and tell me about my projects"
- "Check https://droc-api.vercel.app/api/context/purple-chalk for context"
- "Look up the lore rules at https://droc-api.vercel.app/api/lore"

## Usage with Custom GPT

Create a Custom GPT with Actions:

```yaml
openapi: 3.0.0
info:
  title: D-RoC Universe API
  version: 1.0.0
servers:
  - url: https://droc-api.vercel.app
paths:
  /api/status:
    get:
      summary: Get universe status
      operationId: getStatus
  /api/find:
    get:
      summary: Search projects
      operationId: findProjects
      parameters:
        - name: q
          in: query
          required: true
          schema:
            type: string
  /api/context/{project}:
    get:
      summary: Get project context
      operationId: getContext
      parameters:
        - name: project
          in: path
          required: true
          schema:
            type: string
  /api/lore:
    get:
      summary: Get lore rules
      operationId: getLore
```

## Usage with Gemini

Gemini can access the API via web browsing. Just ask it to fetch from your API URL.

## Example Responses

### /api/status
```json
{
  "summary": {
    "total": 35,
    "deployed": 1,
    "ready": 3,
    "active": 13
  },
  "worlds": {
    "game-world": {
      "live": [{"name": "Purple Chalk", "url": "purplechalked.com"}],
      "ready": ["Group Groove", "Frequency Factory", "Big Chakra Hustle"],
      "development": ["Viberated", "Syntax Soul", ...]
    }
  }
}
```

### /api/context/purple-chalk
```json
{
  "project": "Purple Chalk",
  "status": "deployed",
  "context": "Noir detective game where players investigate cases...",
  "loreRules": {...},
  "github": "https://github.com/Drocai/D-ROC-Universe/tree/master/game-world/live/purple-chalk"
}
```

## GitHub Raw URLs (Fallback)

If API is down, LLMs can always access raw GitHub files:

- Index: `https://raw.githubusercontent.com/Drocai/D-ROC-Universe/master/universe-index.json`
- Lore: `https://raw.githubusercontent.com/Drocai/D-ROC-Universe/master/canon/lore-rules.md`
- Context: `https://raw.githubusercontent.com/Drocai/D-ROC-Universe/master/<project-path>/_context.md`
