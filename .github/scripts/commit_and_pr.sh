#!/usr/bin/env bash

# Copyright 2024 - 2025 Khalil Estell and the libhal contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e

# Get the branch name from the commit SHA
BRANCH_NAME="generate-index-${GITHUB_SHA:0:8}"

# Create and switch to a new branch
git checkout -b "$BRANCH_NAME"

# Configure git user
git config --local user.name 'libhal-bot'
git config --local user.email 'libhal-bot@users.noreply.github.com'

# Add and commit changes
git add libraries.json
git commit -m "Update libraries.json from CI"

# Push to remote with force (to update existing PRs)
git push origin "$BRANCH_NAME" --force-with-lease

# Check if PR already exists for this branch and update it if needed
PR_NUMBER=$(gh pr list --state open --head "$BRANCH_NAME" --json number --jq '.[].number' 2>/dev/null || echo "")

if [ -z "$PR_NUMBER" ]; then
  # Create new PR using GitHub CLI with proper token handling
  gh pr create --title "Update libraries.json from CI" --body "Automated update from CI workflow" --head "$BRANCH_NAME" --base "main"
else
  echo "PR $PR_NUMBER already exists and is updated"
fi