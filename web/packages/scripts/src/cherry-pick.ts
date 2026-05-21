// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

import { execSync } from 'child_process';
import * as readline from 'readline';
import * as process from 'process';
import { openBrowser, getBaseUrl } from './git-utils.js';

// Helper to prompt the user for input.
function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  return new Promise((resolve) =>
    rl.question(question, (ans) => {
      rl.close();
      resolve(ans);
    })
  );
}

async function handleMergeConflicts() {
  let resolved = false;
  while (!resolved) {
    const response = (await prompt('Have you resolved the conflicts? (yes/no/abort): '))
      .trim()
      .toLowerCase();
    if (response === 'yes') {
      try {
        console.log('Staging resolved changes...');
        execSync('git add .', { stdio: 'inherit' });
        console.log('Attempting to continue cherry-pick...');
        execSync('git cherry-pick --continue', { stdio: 'inherit' });
        console.log('Cherry-pick completed successfully after resolving conflicts.');
        resolved = true;
      } catch {
        console.error(
          'There are still unresolved conflicts or issues. Please resolve them and try again.'
        );
      }
    } else if (response === 'no') {
      await prompt('Waiting for you to resolve conflicts. Press enter to check again...');
    } else if (response === 'abort') {
      console.log('Aborting cherry-pick...');
      execSync('git cherry-pick --abort', { stdio: 'inherit' });
      process.exit(1);
    } else {
      console.log("Please answer 'yes', 'no', or 'abort'.");
    }
  }
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: tsx cherry_pick.ts <commit_hash> <release_branch>');
    process.exit(1);
  }

  const commitHash = args[0];
  const releaseBranch = args[1];

  try {
    console.log('Fetching latest changes from origin...');
    execSync('git fetch origin', { stdio: 'inherit' });

    console.log(`Checking out the release branch: ${releaseBranch}`);
    execSync(`git checkout ${releaseBranch}`, { stdio: 'inherit' });
    execSync(`git pull origin ${releaseBranch}`, { stdio: 'inherit' });

    // Create a new branch based on the release branch.
    const newBranchName = `cherry-pick-${commitHash.substring(0, 7)}`;
    console.log(`Creating and switching to new branch: ${newBranchName}`);
    execSync(`git checkout -b ${newBranchName}`, { stdio: 'inherit' });

    console.log(`Attempting to cherry-pick commit: ${commitHash}`);
    try {
      execSync(`git cherry-pick ${commitHash}`, { stdio: 'inherit' });
      console.log('Cherry-pick completed successfully without conflicts.');
    } catch {
      console.error('Merge conflicts detected during cherry-pick!');
      await handleMergeConflicts();
    }

    // Push the new branch to origin.
    console.log(`Pushing branch ${newBranchName} to origin...`);
    execSync(`git push origin ${newBranchName}`, { stdio: 'inherit' });

    // Retrieve the remote URL to construct the merge request URL.
    const remoteUrlRaw = execSync('git remote get-url origin').toString().trim();
    const baseUrl = getBaseUrl(remoteUrlRaw);
    const mergeRequestUrl = `${baseUrl}/-/merge_requests/new?merge_request[source_branch]=${newBranchName}&merge_request[target_branch]=${releaseBranch}`;

    console.log('Opening merge request page in your browser...');
    console.log(`URL: ${mergeRequestUrl}`);
    openBrowser(mergeRequestUrl);
  } catch (error) {
    console.error('An error occurred:', error);
    process.exit(1);
  }
}

main();
