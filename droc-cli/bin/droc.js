#!/usr/bin/env node

const { program } = require('commander');
const chalk = require('chalk');
const path = require('path');

// Commands
const find = require('../src/commands/find');
const work = require('../src/commands/work');
const status = require('../src/commands/status');
const list = require('../src/commands/list');
const context = require('../src/commands/context');

// ASCII Art Banner
const banner = `
${chalk.magenta('╔═══════════════════════════════════════╗')}
${chalk.magenta('║')}  ${chalk.yellow('D-RoC')} ${chalk.white('Command Center')}               ${chalk.magenta('║')}
${chalk.magenta('║')}  ${chalk.gray('Navigate your creative universe')}     ${chalk.magenta('║')}
${chalk.magenta('╚═══════════════════════════════════════╝')}
`;

program
  .name('droc')
  .description('D-RoC Universe Command Center')
  .version('1.0.0');

program
  .command('find <query>')
  .description('Find any project, file, or concept in the universe')
  .action(find);

program
  .command('work <project>')
  .description('Switch to a project and load its context')
  .action(work);

program
  .command('status')
  .description('Show status of all projects across all worlds')
  .action(status);

program
  .command('list <world>')
  .description('List all projects in a world (games, stories, music, business)')
  .action(list);

program
  .command('context [project]')
  .description('Show current or specified project context')
  .action(context);

// Show banner on help
program.on('--help', () => {
  console.log(banner);
});

// If no args, show help with banner
if (process.argv.length === 2) {
  console.log(banner);
  program.help();
}

program.parse();
