#!/bin/bash
#
# ZenMarket AI - Git Branch Cleanup Script
#
# This script helps clean up merged and stale branches to keep the repository organized.
# Run this monthly or after major releases.
#
# Usage:
#   ./scripts/cleanup_branches.sh          # Dry run (shows what would be deleted)
#   ./scripts/cleanup_branches.sh --execute  # Actually delete branches
#   ./scripts/cleanup_branches.sh --help     # Show help

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default mode: dry run
DRY_RUN=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --execute|-e)
            DRY_RUN=false
            shift
            ;;
        --help|-h)
            echo "ZenMarket AI - Branch Cleanup Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --execute, -e    Actually delete branches (default: dry run)"
            echo "  --help, -h       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Show what would be deleted"
            echo "  $0 --execute        # Delete merged branches"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ZenMarket AI - Branch Cleanup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}DRY RUN MODE${NC} - No branches will be deleted"
    echo -e "Run with --execute to actually delete branches"
    echo ""
fi

# Fetch latest from remote
echo -e "${BLUE}Fetching latest from remote...${NC}"
git fetch --all --prune

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -e "Current branch: ${GREEN}${CURRENT_BRANCH}${NC}"
echo ""

# Get main branch name (could be 'main' or 'master')
if git show-ref --verify --quiet refs/heads/main; then
    MAIN_BRANCH="main"
elif git show-ref --verify --quiet refs/heads/master; then
    MAIN_BRANCH="master"
else
    echo -e "${RED}Error: Could not find main/master branch${NC}"
    exit 1
fi

echo -e "Main branch: ${GREEN}${MAIN_BRANCH}${NC}"
echo ""

# Function to check if a branch is merged
is_merged() {
    local branch=$1
    git merge-base --is-ancestor "$branch" "$MAIN_BRANCH" 2>/dev/null
    return $?
}

# Function to get last commit date of a branch
get_last_commit_date() {
    local branch=$1
    git log -1 --format=%ci "$branch" 2>/dev/null | cut -d' ' -f1
}

# Function to get days since last commit
get_days_since_commit() {
    local branch=$1
    local last_commit=$(get_last_commit_date "$branch")
    local current_date=$(date +%s)
    local commit_date=$(date -d "$last_commit" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$last_commit" +%s 2>/dev/null)

    if [ -n "$commit_date" ]; then
        echo $(( (current_date - commit_date) / 86400 ))
    else
        echo "unknown"
    fi
}

# Arrays to track branches
declare -a MERGED_BRANCHES
declare -a STALE_BRANCHES
declare -a SAFE_BRANCHES

# Safe branches that should never be deleted
PROTECTED_BRANCHES=("$MAIN_BRANCH" "develop" "staging" "production")

echo -e "${BLUE}Analyzing local branches...${NC}"
echo ""

# Analyze local branches
for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
    # Skip current branch
    if [ "$branch" = "$CURRENT_BRANCH" ]; then
        continue
    fi

    # Skip protected branches
    if [[ " ${PROTECTED_BRANCHES[@]} " =~ " ${branch} " ]]; then
        SAFE_BRANCHES+=("$branch (protected)")
        continue
    fi

    # Check if merged
    if is_merged "$branch"; then
        MERGED_BRANCHES+=("$branch")
        continue
    fi

    # Check if stale (no commits in last 60 days)
    days_old=$(get_days_since_commit "$branch")
    if [ "$days_old" != "unknown" ] && [ "$days_old" -gt 60 ]; then
        STALE_BRANCHES+=("$branch (${days_old} days old)")
    else
        SAFE_BRANCHES+=("$branch")
    fi
done

# Display results
echo -e "${GREEN}✓ MERGED BRANCHES (safe to delete):${NC}"
if [ ${#MERGED_BRANCHES[@]} -eq 0 ]; then
    echo "  None found"
else
    for branch in "${MERGED_BRANCHES[@]}"; do
        echo "  - $branch"
    done
fi
echo ""

echo -e "${YELLOW}⚠ STALE BRANCHES (no commits in 60+ days):${NC}"
if [ ${#STALE_BRANCHES[@]} -eq 0 ]; then
    echo "  None found"
else
    for branch in "${STALE_BRANCHES[@]}"; do
        echo "  - $branch"
    done
fi
echo ""

echo -e "${BLUE}ℹ ACTIVE BRANCHES (keeping):${NC}"
if [ ${#SAFE_BRANCHES[@]} -eq 0 ]; then
    echo "  None found"
else
    for branch in "${SAFE_BRANCHES[@]}"; do
        echo "  - $branch"
    done
fi
echo ""

# Remote branches
echo -e "${BLUE}Analyzing remote branches...${NC}"
echo ""

declare -a REMOTE_MERGED
declare -a REMOTE_STALE

for branch in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/ | grep -v '/HEAD'); do
    local_branch=${branch#origin/}

    # Skip protected branches
    if [[ " ${PROTECTED_BRANCHES[@]} " =~ " ${local_branch} " ]]; then
        continue
    fi

    # Check if merged into origin/main
    if git merge-base --is-ancestor "$branch" "origin/$MAIN_BRANCH" 2>/dev/null; then
        REMOTE_MERGED+=("$local_branch")
    fi
done

echo -e "${GREEN}✓ MERGED REMOTE BRANCHES:${NC}"
if [ ${#REMOTE_MERGED[@]} -eq 0 ]; then
    echo "  None found"
else
    for branch in "${REMOTE_MERGED[@]}"; do
        echo "  - origin/$branch"
    done
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SUMMARY${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Local branches:"
echo "  - Merged: ${#MERGED_BRANCHES[@]}"
echo "  - Stale: ${#STALE_BRANCHES[@]}"
echo "  - Active: ${#SAFE_BRANCHES[@]}"
echo ""
echo "Remote branches:"
echo "  - Merged: ${#REMOTE_MERGED[@]}"
echo ""

# Execution
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}This was a DRY RUN - no branches were deleted${NC}"
    echo -e "To actually delete branches, run: $0 --execute"
    exit 0
fi

# Confirm before deleting
echo -e "${YELLOW}WARNING: About to delete branches!${NC}"
echo ""
read -p "Delete ${#MERGED_BRANCHES[@]} merged local branches? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    for branch in "${MERGED_BRANCHES[@]}"; do
        echo -e "${GREEN}Deleting local branch: $branch${NC}"
        git branch -d "$branch"
    done
fi

if [ ${#REMOTE_MERGED[@]} -gt 0 ]; then
    echo ""
    read -p "Delete ${#REMOTE_MERGED[@]} merged remote branches? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for branch in "${REMOTE_MERGED[@]}"; do
            echo -e "${GREEN}Deleting remote branch: origin/$branch${NC}"
            git push origin --delete "$branch"
        done
    fi
fi

if [ ${#STALE_BRANCHES[@]} -gt 0 ]; then
    echo ""
    read -p "Delete ${#STALE_BRANCHES[@]} stale local branches? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for branch_info in "${STALE_BRANCHES[@]}"; do
            branch=$(echo "$branch_info" | cut -d' ' -f1)
            echo -e "${YELLOW}Deleting stale branch: $branch${NC}"
            git branch -D "$branch"  # Force delete since not merged
        done
    fi
fi

echo ""
echo -e "${GREEN}✓ Branch cleanup complete${NC}"
