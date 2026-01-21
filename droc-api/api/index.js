// D-RoC Universe API - Main endpoint
// Returns API documentation

export default function handler(req, res) {
  res.status(200).json({
    name: "D-RoC Universe API",
    version: "1.0.0",
    description: "Access the D-RoC creative universe from any LLM",
    endpoints: {
      "/api/status": "Get status of all projects",
      "/api/find?q=<query>": "Search for projects",
      "/api/context/<project>": "Get project context for LLM",
      "/api/list/<world>": "List projects (games, stories, music, business)",
      "/api/lore": "Get universe lore rules",
      "/api/index": "Get full universe index JSON"
    },
    github: "https://github.com/Drocai/D-ROC-Universe",
    usage: "For ChatGPT/Gemini: Browse to any endpoint to get data"
  });
}
