const fs = require('fs');
const path = require('path');

/**
 * Context Loader - Loads and parses _context.md files for LLM integration
 */

class ContextLoader {
  constructor(universeRoot) {
    this.universeRoot = universeRoot;
  }

  /**
   * Load context from a project path
   */
  loadContext(projectPath) {
    const contextPath = path.join(projectPath, '_context.md');

    if (!fs.existsSync(contextPath)) {
      return null;
    }

    const content = fs.readFileSync(contextPath, 'utf8');
    return this.parseContext(content);
  }

  /**
   * Parse a _context.md file into structured data
   */
  parseContext(content) {
    const context = {
      raw: content,
      sections: {},
      rules: [],
      related: [],
      keyFiles: []
    };

    // Split by ## headers
    const sections = content.split(/^## /gm);

    sections.forEach(section => {
      if (!section.trim()) return;

      const lines = section.split('\n');
      const title = lines[0].trim();
      const body = lines.slice(1).join('\n').trim();

      context.sections[title] = body;

      // Extract special sections
      if (title.toLowerCase() === 'rules') {
        context.rules = body.split('\n')
          .filter(l => l.startsWith('-'))
          .map(l => l.replace(/^-\s*/, ''));
      }

      if (title.toLowerCase() === 'related' || title.toLowerCase() === 'related projects') {
        context.related = body.split('\n')
          .filter(l => l.startsWith('-'))
          .map(l => l.replace(/^-\s*/, '').replace(/`/g, ''));
      }

      if (title.toLowerCase() === 'key files') {
        context.keyFiles = body.split('\n')
          .filter(l => l.startsWith('-'))
          .map(l => l.replace(/^-\s*/, '').replace(/`/g, '').split(' - ')[0]);
      }
    });

    return context;
  }

  /**
   * Generate a prompt injection for LLM sessions
   */
  generateLLMContext(projectPath) {
    const context = this.loadContext(projectPath);

    if (!context) {
      return null;
    }

    let prompt = `
=== PROJECT CONTEXT ===
You are working on a D-RoC Universe project.

${context.raw}

=== RULES TO FOLLOW ===
${context.rules.map(r => `- ${r}`).join('\n')}

=== END CONTEXT ===
`;

    return prompt;
  }
}

module.exports = ContextLoader;
