const chalk = require('chalk');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const UNIVERSE_ROOT = path.resolve(__dirname, '../../..');
const INDEX_PATH = path.join(UNIVERSE_ROOT, 'universe-index.json');

function loadIndex() {
  try {
    return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));
  } catch (e) {
    return null;
  }
}

function findProject(index, query) {
  const q = query.toLowerCase();

  // Check aliases first
  if (index.searchAliases) {
    for (const [alias, target] of Object.entries(index.searchAliases)) {
      if (alias.toLowerCase().includes(q)) {
        return { name: alias, path: target };
      }
    }
  }

  // Search all worlds
  for (const [worldName, world] of Object.entries(index.worlds)) {
    if (world.tiers) {
      for (const [tierName, tier] of Object.entries(world.tiers)) {
        for (const [projId, proj] of Object.entries(tier)) {
          if (projId.includes(q) || proj.name.toLowerCase().includes(q)) {
            return { name: proj.name, path: `${world.path}${tierName}/${projId}` };
          }
        }
      }
    }
    if (world.projects) {
      for (const [projId, proj] of Object.entries(world.projects)) {
        if (projId.includes(q) || proj.name.toLowerCase().includes(q)) {
          return { name: proj.name, path: `${world.path}${projId}` };
        }
      }
    }
  }

  return null;
}

function loadContext(projectPath) {
  const contextPath = path.join(projectPath, '_context.md');
  if (fs.existsSync(contextPath)) {
    return fs.readFileSync(contextPath, 'utf8');
  }
  return null;
}

module.exports = function work(project) {
  console.log(chalk.cyan(`\nSwitching to: "${project}"\n`));

  const index = loadIndex();
  if (!index) {
    console.log(chalk.red('Error loading universe index'));
    return;
  }

  const found = findProject(index, project);

  if (!found) {
    console.log(chalk.red(`Project "${project}" not found.`));
    console.log(chalk.gray('Try: droc find <query>'));
    return;
  }

  const fullPath = path.join(UNIVERSE_ROOT, found.path);

  console.log(chalk.green(`Found: ${found.name}`));
  console.log(chalk.gray(`Path: ${fullPath}\n`));

  // Load and display context
  const context = loadContext(fullPath);
  if (context) {
    console.log(chalk.yellow('━━━ Context ━━━━━━━━━━━━━━━━━━━━━━━━━━━'));
    console.log(context.slice(0, 1000));
    if (context.length > 1000) {
      console.log(chalk.gray('\n... (truncated, see _context.md for full)'));
    }
    console.log(chalk.yellow('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'));
  }

  // Output the cd command for shell integration
  console.log(chalk.cyan('To navigate to this project, run:'));
  console.log(chalk.white(`  cd "${fullPath}"`));

  // Save current context to a file for LLM integration
  const contextFile = path.join(UNIVERSE_ROOT, '.current-context');
  fs.writeFileSync(contextFile, JSON.stringify({
    project: found.name,
    path: fullPath,
    context: context,
    timestamp: new Date().toISOString()
  }, null, 2));

  console.log(chalk.gray(`\nContext saved to .current-context for LLM integration`));
};
