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

function statusIcon(status) {
  switch (status) {
    case 'deployed': return chalk.green('●');
    case 'ready': return chalk.yellow('◐');
    case 'active': return chalk.blue('○');
    case 'placeholder': return chalk.gray('○');
    case 'concept': return chalk.magenta('◌');
    default: return chalk.gray('?');
  }
}

module.exports = function status() {
  const index = loadIndex();
  if (!index) {
    console.log(chalk.red('Error loading universe index'));
    return;
  }

  console.log(chalk.magenta('\n╔═══════════════════════════════════════╗'));
  console.log(chalk.magenta('║') + chalk.white.bold('      D-RoC Universe Status            ') + chalk.magenta('║'));
  console.log(chalk.magenta('╚═══════════════════════════════════════╝\n'));

  // Legend
  console.log(chalk.gray('Legend: ') +
    chalk.green('● deployed ') +
    chalk.yellow('◐ ready ') +
    chalk.blue('○ active ') +
    chalk.gray('○ placeholder ') +
    chalk.magenta('◌ concept\n'));

  // Game World
  console.log(chalk.cyan.bold('🎮 GAME WORLD'));
  const gameWorld = index.worlds['game-world'];
  if (gameWorld?.tiers) {
    for (const [tierName, tier] of Object.entries(gameWorld.tiers)) {
      console.log(chalk.yellow(`  ${tierName.toUpperCase()}`));
      for (const [projId, proj] of Object.entries(tier)) {
        console.log(`    ${statusIcon(proj.status)} ${proj.name}`);
      }
    }
  }
  console.log();

  // Story World
  console.log(chalk.cyan.bold('📚 STORY WORLD'));
  const storyWorld = index.worlds['story-world'];
  if (storyWorld?.projects) {
    for (const [projId, proj] of Object.entries(storyWorld.projects)) {
      const extra = proj.type === 'series' ? chalk.gray(' (4 books)') : '';
      console.log(`  ${statusIcon(proj.status)} ${proj.name}${extra}`);
    }
  }
  console.log();

  // Music World
  console.log(chalk.cyan.bold('🎵 MUSIC WORLD'));
  const musicWorld = index.worlds['music-world'];
  if (musicWorld?.albums) {
    for (const [albumId, album] of Object.entries(musicWorld.albums)) {
      console.log(`  ${statusIcon(album.status)} ${album.name}`);
    }
  }
  console.log();

  // Business World
  console.log(chalk.cyan.bold('💼 BUSINESS WORLD'));
  const bizWorld = index.worlds['business-world'];
  if (bizWorld?.projects) {
    for (const [projId, proj] of Object.entries(bizWorld.projects)) {
      console.log(`  ${statusIcon(proj.status)} ${proj.name}`);
    }
  }
  console.log();

  // Summary
  let total = 0, deployed = 0, ready = 0, active = 0;
  for (const world of Object.values(index.worlds)) {
    if (world.tiers) {
      for (const tier of Object.values(world.tiers)) {
        for (const proj of Object.values(tier)) {
          total++;
          if (proj.status === 'deployed') deployed++;
          if (proj.status === 'ready') ready++;
          if (proj.status === 'active') active++;
        }
      }
    }
    if (world.projects) {
      for (const proj of Object.values(world.projects)) {
        total++;
        if (proj.status === 'deployed') deployed++;
        if (proj.status === 'ready') ready++;
        if (proj.status === 'active') active++;
      }
    }
    if (world.albums) {
      for (const album of Object.values(world.albums)) {
        total++;
        if (album.status === 'active') active++;
      }
    }
  }

  console.log(chalk.gray('─'.repeat(40)));
  console.log(chalk.white(`Total: ${total} projects | `) +
    chalk.green(`${deployed} deployed | `) +
    chalk.yellow(`${ready} ready | `) +
    chalk.blue(`${active} active`));
};
