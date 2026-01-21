#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const UNIVERSE_ROOT = path.resolve(__dirname, "..");
const INDEX_PATH = path.join(UNIVERSE_ROOT, "universe-index.json");

// Load universe index
function loadIndex() {
  try {
    return JSON.parse(fs.readFileSync(INDEX_PATH, "utf8"));
  } catch (e) {
    return null;
  }
}

// Load context file for a project
function loadContext(projectPath) {
  const contextPath = path.join(UNIVERSE_ROOT, projectPath, "_context.md");
  try {
    return fs.readFileSync(contextPath, "utf8");
  } catch (e) {
    return null;
  }
}

// Get all projects as flat list
function getAllProjects(index) {
  const projects = [];

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
          status: proj.status,
          tags: proj.tags || [],
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

// Create MCP server
const server = new Server(
  { name: "droc-mcp", version: "1.0.0" },
  { capabilities: { tools: {}, resources: {} } }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "droc_status",
        description: "Get the status of all projects in the D-RoC Universe. Shows games, stories, music, and business projects with their current status (deployed, ready, active, placeholder, concept).",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      },
      {
        name: "droc_find",
        description: "Search for projects, files, or concepts in the D-RoC Universe. Uses fuzzy matching on project names and tags.",
        inputSchema: {
          type: "object",
          properties: {
            query: {
              type: "string",
              description: "Search query (project name, tag, or concept)"
            }
          },
          required: ["query"]
        }
      },
      {
        name: "droc_context",
        description: "Get the full context file for a project. This contains everything an LLM needs to know: what the project is, current status, key files, rules, and related projects.",
        inputSchema: {
          type: "object",
          properties: {
            project: {
              type: "string",
              description: "Project ID (e.g., 'purple-chalk', 'echoverse', 'automagic-otto')"
            }
          },
          required: ["project"]
        }
      },
      {
        name: "droc_list",
        description: "List all projects in a specific world (game-world, story-world, music-world, business-world).",
        inputSchema: {
          type: "object",
          properties: {
            world: {
              type: "string",
              enum: ["games", "stories", "music", "business"],
              description: "Which world to list"
            }
          },
          required: ["world"]
        }
      },
      {
        name: "droc_lore_rules",
        description: "Get the canonical lore rules for the D-RoC Universe. Important for maintaining consistency across projects.",
        inputSchema: {
          type: "object",
          properties: {},
          required: []
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const index = loadIndex();

  if (!index) {
    return { content: [{ type: "text", text: "Error: Could not load universe index" }] };
  }

  switch (name) {
    case "droc_status": {
      const projects = getAllProjects(index);
      const statusCounts = { deployed: 0, ready: 0, active: 0, placeholder: 0, concept: 0 };

      let output = "# D-RoC Universe Status\n\n";

      // Game World
      output += "## Game World\n";
      const gameWorld = index.worlds["game-world"];
      if (gameWorld?.tiers) {
        for (const [tier, games] of Object.entries(gameWorld.tiers)) {
          output += `\n### ${tier.toUpperCase()}\n`;
          for (const [id, game] of Object.entries(games)) {
            const icon = game.status === "deployed" ? "●" : game.status === "ready" ? "◐" : "○";
            output += `- ${icon} ${game.name}\n`;
            if (statusCounts[game.status] !== undefined) statusCounts[game.status]++;
          }
        }
      }

      // Story World
      output += "\n## Story World\n";
      const storyWorld = index.worlds["story-world"];
      if (storyWorld?.projects) {
        for (const [id, proj] of Object.entries(storyWorld.projects)) {
          output += `- ${proj.name}${proj.type === "series" ? " (4 books)" : ""}\n`;
          if (statusCounts[proj.status] !== undefined) statusCounts[proj.status]++;
        }
      }

      // Music World
      output += "\n## Music World\n";
      const musicWorld = index.worlds["music-world"];
      if (musicWorld?.albums) {
        for (const [id, album] of Object.entries(musicWorld.albums)) {
          output += `- ${album.name}\n`;
        }
      }

      // Business World
      output += "\n## Business World\n";
      const bizWorld = index.worlds["business-world"];
      if (bizWorld?.projects) {
        for (const [id, proj] of Object.entries(bizWorld.projects)) {
          output += `- ${proj.name}\n`;
          if (statusCounts[proj.status] !== undefined) statusCounts[proj.status]++;
        }
      }

      output += `\n---\nTotal: ${projects.length} projects | ${statusCounts.deployed} deployed | ${statusCounts.ready} ready | ${statusCounts.active} active`;

      return { content: [{ type: "text", text: output }] };
    }

    case "droc_find": {
      const query = (args.query || "").toLowerCase();
      const projects = getAllProjects(index);

      // Check aliases first
      if (index.searchAliases && index.searchAliases[query]) {
        return {
          content: [{
            type: "text",
            text: `**Alias Match:** ${query} → ${index.searchAliases[query]}\n\nFull path: ${path.join(UNIVERSE_ROOT, index.searchAliases[query])}`
          }]
        };
      }

      // Fuzzy search projects
      const matches = projects.filter(p =>
        p.name.toLowerCase().includes(query) ||
        p.id.toLowerCase().includes(query) ||
        (p.tags && p.tags.some(t => t.toLowerCase().includes(query)))
      );

      if (matches.length === 0) {
        return { content: [{ type: "text", text: `No matches found for "${query}"` }] };
      }

      let output = `# Search Results for "${query}"\n\n`;
      for (const match of matches) {
        output += `## ${match.name}\n`;
        output += `- **ID:** ${match.id}\n`;
        output += `- **World:** ${match.world}\n`;
        output += `- **Status:** ${match.status}\n`;
        if (match.tags?.length) output += `- **Tags:** ${match.tags.join(", ")}\n`;
        output += `- **Path:** ${match.path}\n\n`;
      }

      return { content: [{ type: "text", text: output }] };
    }

    case "droc_context": {
      const projectId = args.project;
      const projects = getAllProjects(index);
      const project = projects.find(p => p.id === projectId || p.name.toLowerCase() === projectId.toLowerCase());

      if (!project) {
        return { content: [{ type: "text", text: `Project not found: ${projectId}` }] };
      }

      const context = loadContext(project.path);

      if (!context) {
        return {
          content: [{
            type: "text",
            text: `# ${project.name}\n\n**Status:** ${project.status}\n**Path:** ${project.path}\n\n_No _context.md file found for this project._`
          }]
        };
      }

      return { content: [{ type: "text", text: context }] };
    }

    case "droc_list": {
      const worldMap = {
        games: "game-world",
        stories: "story-world",
        music: "music-world",
        business: "business-world"
      };

      const worldKey = worldMap[args.world];
      const world = index.worlds[worldKey];

      if (!world) {
        return { content: [{ type: "text", text: `Unknown world: ${args.world}` }] };
      }

      let output = `# ${args.world.toUpperCase()}\n\n`;

      if (world.tiers) {
        for (const [tier, items] of Object.entries(world.tiers)) {
          output += `## ${tier.toUpperCase()}\n`;
          for (const [id, item] of Object.entries(items)) {
            output += `- **${item.name}** [${(item.tags || []).join(", ")}]`;
            if (item.url) output += ` → ${item.url}`;
            output += `\n`;
          }
          output += "\n";
        }
      }

      if (world.projects) {
        for (const [id, item] of Object.entries(world.projects)) {
          output += `- **${item.name}**`;
          if (item.type) output += ` (${item.type})`;
          output += `\n`;
        }
      }

      if (world.albums) {
        for (const [id, item] of Object.entries(world.albums)) {
          output += `- **${item.name}**\n`;
        }
      }

      return { content: [{ type: "text", text: output }] };
    }

    case "droc_lore_rules": {
      const loreRulesPath = path.join(UNIVERSE_ROOT, "canon", "lore-rules.md");
      try {
        const rules = fs.readFileSync(loreRulesPath, "utf8");
        return { content: [{ type: "text", text: rules }] };
      } catch (e) {
        // Fallback to index lore rules
        const rules = index.loreRules;
        let output = "# D-RoC Universe Lore Rules\n\n";
        output += `1. **Hum Ban:** ${rules.humBan}\n`;
        output += `2. **Cross-Story Characters:** ${rules.crossCharacters.join(", ")}\n`;
        output += `3. **Otto Canon:** ${rules.ottoCanon}\n`;
        output += `4. **Key Pattern:** ${rules.keyPattern}\n`;
        return { content: [{ type: "text", text: output }] };
      }
    }

    default:
      return { content: [{ type: "text", text: `Unknown tool: ${name}` }] };
  }
});

// List resources (context files)
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  const index = loadIndex();
  const resources = [];

  // Add main index
  resources.push({
    uri: "droc://universe-index",
    name: "Universe Index",
    description: "Master index of all D-RoC Universe projects",
    mimeType: "application/json"
  });

  // Add lore rules
  resources.push({
    uri: "droc://lore-rules",
    name: "Lore Rules",
    description: "Canonical rules for the D-RoC Universe",
    mimeType: "text/markdown"
  });

  return { resources };
});

// Read resources
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === "droc://universe-index") {
    const index = loadIndex();
    return {
      contents: [{
        uri,
        mimeType: "application/json",
        text: JSON.stringify(index, null, 2)
      }]
    };
  }

  if (uri === "droc://lore-rules") {
    const loreRulesPath = path.join(UNIVERSE_ROOT, "canon", "lore-rules.md");
    try {
      const rules = fs.readFileSync(loreRulesPath, "utf8");
      return {
        contents: [{
          uri,
          mimeType: "text/markdown",
          text: rules
        }]
      };
    } catch (e) {
      return { contents: [{ uri, mimeType: "text/plain", text: "Lore rules not found" }] };
    }
  }

  return { contents: [{ uri, mimeType: "text/plain", text: "Resource not found" }] };
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("D-RoC MCP Server running");
}

main().catch(console.error);
