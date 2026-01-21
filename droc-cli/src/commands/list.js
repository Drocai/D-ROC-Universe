const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

const UNIVERSE_ROOT = path.resolve(__dirname, '../../..');
const INDEX_PATH = path.join(UNIVERSE_ROOT, 'universe-index.json');

function loadIndex() {
  try {
    return JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));
  } catch (e) {
    return null;
  }
}

module.exports = function list(world) {
  const index = loadIndex();
  if (!index) {
    console.log(chalk.red('Error loading universe index'));
    return;
  }

  const worldKey = world.toLowerCase();
  const worldMap = {
    'games': 'game-world',
    'game': 'game-world',
    'game-world': 'game-world',
    'stories': 'story-world',
    'story': 'story-world',
    'story-world': 'story-world',
    'music': 'music-world',
    'music-world': 'music-world',
    'business': 'business-world',
    'business-world': 'business-world'
  };

  const targetWorld = worldMap[worldKey];

  if (!targetWorld) {
    console.log(chalk.red(`Unknown world: "${world}"`));
    console.log(chalk.gray('Available worlds: games, stories, music, business'));
    return;
  }

  const worldData = index.worlds[targetWorld];
  if (!worldData) {
    console.log(chalk.red(`World "${targetWorld}" not found in index`));
    return;
  }

  console.log(chalk.cyan.bold(`\n${targetWorld.toUpperCase()}\n`));

  // Handle different world structures
  if (worldData.tiers) {
    for (const [tierName, tier] of Object.entries(worldData.tiers)) {
      console.log(chalk.yellow(`${tierName.toUpperCase()}:`));
      for (const [projId, proj] of Object.entries(tier)) {
        const tags = proj.tags ? chalk.gray(` [${proj.tags.join(', ')}]`) : '';
        const url = proj.url ? chalk.blue(` → ${proj.url}`) : '';
        console.log(`  • ${proj.name}${tags}${url}`);
      }
      console.log();
    }
  }

  if (worldData.projects) {
    for (const [projId, proj] of Object.entries(worldData.projects)) {
      const tags = proj.tags ? chalk.gray(` [${proj.tags.join(', ')}]`) : '';
      const status = chalk.gray(` (${proj.status})`);
      console.log(`  • ${proj.name}${tags}${status}`);
    }
  }

  if (worldData.albums) {
    console.log(chalk.yellow('ALBUMS:'));
    for (const [albumId, album] of Object.entries(worldData.albums)) {
      const status = chalk.gray(` (${album.status})`);
      console.log(`  • ${album.name}${status}`);
    }
  }
};
