const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

const UNIVERSE_ROOT = path.resolve(__dirname, '../../..');
const CONTEXT_FILE = path.join(UNIVERSE_ROOT, '.current-context');
const INDEX_PATH = path.join(UNIVERSE_ROOT, 'universe-index.json');

function loadIndex() {
  try {
    return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));
  } catch (e) {
    return null;
  }
}

function findProjectPath(index, query) {
  const q = query.toLowerCase();

  for (const [worldName, world] of Object.entries(index.worlds)) {
    if (world.tiers) {
      for (const [tierName, tier] of Object.entries(world.tiers)) {
        for (const [projId, proj] of Object.entries(tier)) {
          if (projId.includes(q) || proj.name.toLowerCase().includes(q)) {
            return path.join(UNIVERSE_ROOT, world.path, tierName, projId);
          }
        }
      }
    }
    if (world.projects) {
      for (const [projId, proj] of Object.entries(world.projects)) {
        if (projId.includes(q) || proj.name.toLowerCase().includes(q)) {
          return path.join(UNIVERSE_ROOT, world.path, projId);
        }
      }
    }
  }
  return null;
}

module.exports = function context(project) {
  // If project specified, show that project's context
  if (project) {
    const index = loadIndex();
    if (!index) {
      console.log(chalk.red('Error loading universe index'));
      return;
    }

    const projectPath = findProjectPath(index, project);
    if (!projectPath) {
      console.log(chalk.red(`Project "${project}" not found`));
      return;
    }

    const contextPath = path.join(projectPath, '_context.md');
    if (fs.existsSync(contextPath)) {
      console.log(chalk.cyan.bold(`\nContext for: ${project}\n`));
      console.log(fs.readFileSync(contextPath, 'utf8'));
    } else {
      console.log(chalk.yellow(`No _context.md found for ${project}`));
      console.log(chalk.gray(`Expected at: ${contextPath}`));
    }
    return;
  }

  // Otherwise show current context
  if (!fs.existsSync(CONTEXT_FILE)) {
    console.log(chalk.yellow('No current context set.'));
    console.log(chalk.gray('Use: droc work <project> to set context'));
    return;
  }

  try {
    const current = JSON.parse(fs.readFileSync(CONTEXT_FILE, 'utf8'));

    console.log(chalk.cyan.bold('\n━━━ Current Context ━━━━━━━━━━━━━━━━━━━━\n'));
    console.log(chalk.white(`Project: ${current.project}`));
    console.log(chalk.gray(`Path: ${current.path}`));
    console.log(chalk.gray(`Set at: ${current.timestamp}\n`));

    if (current.context) {
      console.log(chalk.yellow('Context:'));
      console.log(current.context);
    }

    console.log(chalk.cyan('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'));
  } catch (e) {
    console.log(chalk.red('Error reading current context'));
  }
};
