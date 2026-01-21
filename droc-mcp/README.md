# D-RoC MCP Server

MCP (Model Context Protocol) server for Claude integration with the D-RoC Universe.

## What is MCP?

MCP allows Claude to access external tools and data sources. This server gives Claude direct access to your D-RoC Universe data.

## Installation

### 1. Install dependencies

```bash
cd D-RoC-Universe/droc-mcp
npm install
```

### 2. Configure Claude Desktop

Add to your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "droc": {
      "command": "node",
      "args": ["C:/Users/djmc1/D-RoC-Universe/droc-mcp/index.js"]
    }
  }
}
```

### 3. Restart Claude Desktop

The D-RoC tools will now be available in Claude Desktop.

## Available Tools

| Tool | Description |
|------|-------------|
| `droc_status` | Get status of all projects in the universe |
| `droc_find` | Search for projects by name or tags |
| `droc_context` | Get full context file for a project |
| `droc_list` | List projects in a world (games, stories, etc.) |
| `droc_lore_rules` | Get canonical lore rules |

## Usage in Claude

Once configured, you can ask Claude things like:

- "Use droc_status to show me all my projects"
- "Find projects related to music"
- "Get the context for Purple Chalk"
- "What are the lore rules for my universe?"

## For Claude Code

Add to your Claude Code settings or use the `--mcp` flag:

```bash
claude --mcp droc-mcp
```

Or add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "droc": {
      "command": "node",
      "args": ["/path/to/D-RoC-Universe/droc-mcp/index.js"]
    }
  }
}
```
