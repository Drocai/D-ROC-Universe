const { execSync } = require('child_process');
const chalk = require('chalk');
const path = require('path');

/**
 * GitHub Integration for D-RoC CLI
 */

class GitHubIntegration {
  constructor(universeRoot) {
    this.universeRoot = universeRoot;
  }

  /**
   * Check git status
   */
  status() {
    try {
      const result = execSync('git status --short', {
        cwd: this.universeRoot,
        encoding: 'utf8'
      });
      return result || 'Clean - no changes';
    } catch (e) {
      return 'Not a git repository';
    }
  }

  /**
   * Sync (pull then push)
   */
  sync() {
    try {
      console.log(chalk.cyan('Pulling latest changes...'));
      execSync('git pull', { cwd: this.universeRoot, stdio: 'inherit' });

      console.log(chalk.cyan('Pushing local changes...'));
      execSync('git push', { cwd: this.universeRoot, stdio: 'inherit' });

      console.log(chalk.green('Sync complete!'));
      return true;
    } catch (e) {
      console.log(chalk.red('Sync failed:', e.message));
      return false;
    }
  }

  /**
   * Quick commit and push
   */
  quickCommit(message) {
    try {
      execSync('git add -A', { cwd: this.universeRoot });
      execSync(`git commit -m "${message}"`, { cwd: this.universeRoot });
      execSync('git push', { cwd: this.universeRoot });
      console.log(chalk.green('Committed and pushed!'));
      return true;
    } catch (e) {
      console.log(chalk.red('Commit failed:', e.message));
      return false;
    }
  }

  /**
   * Get current branch
   */
  currentBranch() {
    try {
      return execSync('git branch --show-current', {
        cwd: this.universeRoot,
        encoding: 'utf8'
      }).trim();
    } catch (e) {
      return null;
    }
  }
}

module.exports = GitHubIntegration;
