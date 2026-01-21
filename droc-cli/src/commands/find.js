const chalk = require('chalk');
const fs = require('fs');
const path = require('path');
const fuzzy = require('fuzzy');

const UNIVERSE_ROOT = path.resolve(__dirname, '../../..');
const INDEX_PATH = path.join(UNIVERSE_ROOT, 'universe-index.json');

function loadIndex() {
  try {
    return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));
  } catch (e) {
    console.log(chalk.red('Error loading universe index'));
    return null;
  }
}

function getAllSearchableItems(index) {
  const items = [];

  // Add aliases
  if (index.searchAliases) {
    for (const [alias, target] of Object.entries(index.searchAliases)) {
      items.push({ name: alias, path: target, type: 'alias' });
    }
  }

  // Add all projects from worlds
  for (const [worldName, world] of Object.entries(index.worlds)) {
    if (world.tiers) {
      for (const [tierName, tier] of Object.entries(world.tiers)) {
        for (const [projId, proj] of Object.entries(tier)) {
          items.push({
            name: proj.name,
            path: `${world.path}${tierName}/${projId}`,
            type: 'game',
            status: proj.status,
            tags: proj.tags || []
          });
        }
      }
    }
    if (world.projects) {
      for (const [projId, proj] of Object.entries(world.projects)) {
        items.push({
          name: proj.name,
          path: `${world.path}${projId}`,
          type: proj.type || 'project',
          status: proj.status,
          tags: proj.tags || []
        });
      }
    }
    if (world.albums) {
      for (const [albumId, album] of Object.entries(world.albums)) {
        items.push({
          name: album.name,
          path: `${world.path}albums/${albumId}`,
          type: 'album',
          status: album.status
        });
      }
    }
  }

  return items;
}

module.exports = function find(query) {
  console.log(chalk.cyan(`\nSearching for: "${query}"\n`));

  const index = loadIndex();
  if (!index) return;

  const items = getAllSearchableItems(index);
  const searchStrings = items.map(i => `${i.name} ${i.tags?.join(' ') || ''}`);

  const results = fuzzy.filter(query, searchStrings);

  if (results.length === 0) {
    console.log(chalk.yellow('No matches found.'));
    return;
  }

  console.log(chalk.green(`Found ${results.length} match(es):\n`));

  results.slice(0, 10).forEach((result, idx) => {
    const item = items[result.index];
    const statusColor = item.status === 'deployed' ? 'green' :
                       item.status === 'active' ? 'yellow' : 'gray';

    console.log(
      chalk.white(`${idx + 1}. `) +
      chalk.bold(item.name) +
      chalk.gray(` [${item.type}]`) +
      chalk[statusColor](` (${item.status || 'unknown'})`)
    );
    console.log(chalk.gray(`   ${path.join(UNIVERSE_ROOT, item.path)}`));
    console.log();
  });
};
