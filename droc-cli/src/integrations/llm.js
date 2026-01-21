const fs = require('fs');
const path = require('path');
const ContextLoader = require('../context/loader');

/**
 * LLM Integration for D-RoC CLI
 * Prepares context for injection into Claude/GPT sessions
 */

class LLMIntegration {
  constructor(universeRoot) {
    this.universeRoot = universeRoot;
    this.contextLoader = new ContextLoader(universeRoot);
  }

  /**
   * Generate a system prompt for LLM sessions based on current project
   */
  generateSystemPrompt(projectPath) {
    const context = this.contextLoader.loadContext(projectPath);
    const loreRules = this.loadLoreRules();

    let prompt = `You are assisting with a D-RoC Universe project.

## Universe Lore Rules (ALWAYS FOLLOW)
${loreRules}

`;

    if (context) {
      prompt += `## Current Project Context
${context.raw}
`;
    }

    return prompt;
  }

  /**
   * Load universal lore rules
   */
  loadLoreRules() {
    const loreRulesPath = path.join(this.universeRoot, 'canon', 'lore-rules.md');

    if (fs.existsSync(loreRulesPath)) {
      const content = fs.readFileSync(loreRulesPath, 'utf8');
      // Extract just the absolute rules section
      const match = content.match(/## Absolute Rules[\s\S]*?(?=##|$)/);
      return match ? match[0] : content.slice(0, 500);
    }

    return `
- "Hum" is BANNED outside Echoes of None
- Aires & Dai = fractures across ALL stories
- Otto = AI entity with 6 Devides (canon)
- 3-6-9 Pattern = Key to Echoverse
`;
  }

  /**
   * Save context to clipboard-friendly format
   */
  exportContextForClipboard(projectPath) {
    const prompt = this.generateSystemPrompt(projectPath);
    return `
[PASTE THIS AT START OF LLM SESSION]
---
${prompt}
---
[END CONTEXT]
`;
  }
}

module.exports = LLMIntegration;
