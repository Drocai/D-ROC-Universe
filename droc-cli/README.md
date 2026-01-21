# D-RoC Command Center (droc-cli)

A CLI tool for navigating and managing the D-RoC Universe.

## Installation

```bash
cd droc-cli
npm install
npm link  # Makes 'droc' available globally
```

## Commands

### `droc find <query>`
Fuzzy search for any project, file, or concept.

```bash
droc find "echoes chapter 5"
droc find "purple chalk"
droc find "music"
```

### `droc work <project>`
Switch to a project and load its context.

```bash
droc work "purple chalk"
droc work "echoes"
droc work "otto"
```

### `droc status`
Show status of all projects across all worlds.

```bash
droc status
```

### `droc list <world>`
List all projects in a specific world.

```bash
droc list games
droc list stories
droc list music
droc list business
```

### `droc context [project]`
Show current context or a specific project's context.

```bash
droc context           # Show current context
droc context "echoes"  # Show Echoes context
```

## LLM Integration

The CLI saves context to `.current-context` when you run `droc work`.
This can be read by LLMs to understand what you're working on.

## Project Structure

```
droc-cli/
├── bin/droc.js           # CLI entry point
├── src/
│   ├── commands/         # Command implementations
│   ├── context/          # Context loading utilities
│   └── integrations/     # GitHub, LLM integrations
└── config/               # Configuration
```

## Configuration

Edit `config/droc.config.json` to customize:
- Default editor
- Integration settings (GitHub, Cloudinary, Vercel, Netlify)
- LLM provider settings
