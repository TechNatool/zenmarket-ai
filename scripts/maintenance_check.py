#!/usr/bin/env python
"""
ZenMarket AI - Repository Maintenance Check Script

This script performs comprehensive health checks on the repository.
Run this weekly or monthly to maintain code quality and catch issues early.

Usage:
    python scripts/maintenance_check.py
    python scripts/maintenance_check.py --verbose
    python scripts/maintenance_check.py --output report.md
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class Color:
    """Terminal colors for output formatting."""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def run_command(cmd: str, capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a shell command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=300,  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def check_test_coverage() -> Dict[str, any]:
    """Check test coverage percentage."""
    print(f"{Color.BLUE}Checking test coverage...{Color.RESET}")

    code, stdout, stderr = run_command(
        "pytest --cov=src --cov-report=term-missing -q 2>&1 | grep 'TOTAL'"
    )

    if code == 0 and stdout:
        # Parse coverage from output (e.g., "TOTAL    1234    567    54%")
        try:
            parts = stdout.split()
            coverage_str = parts[-1].replace("%", "")
            coverage = float(coverage_str)

            status = "✅" if coverage >= 70 else "⚠️" if coverage >= 60 else "❌"
            return {
                "name": "Test Coverage",
                "status": status,
                "value": f"{coverage}%",
                "details": f"Target: ≥70%, Current: {coverage}%",
                "passed": coverage >= 60,
            }
        except Exception:
            pass

    return {
        "name": "Test Coverage",
        "status": "❌",
        "value": "Unknown",
        "details": "Failed to determine coverage",
        "passed": False,
    }


def check_code_quality() -> List[Dict]:
    """Run code quality checks (black, isort, ruff)."""
    print(f"{Color.BLUE}Checking code quality...{Color.RESET}")

    checks = []

    # Black formatting
    code, _, _ = run_command("black --check . --quiet")
    checks.append(
        {
            "name": "Black Formatting",
            "status": "✅" if code == 0 else "❌",
            "value": "Compliant" if code == 0 else "Issues found",
            "details": "Run 'black .' to fix" if code != 0 else "All files formatted correctly",
            "passed": code == 0,
        }
    )

    # isort
    code, _, _ = run_command("isort --check-only . --quiet")
    checks.append(
        {
            "name": "Import Sorting (isort)",
            "status": "✅" if code == 0 else "❌",
            "value": "Compliant" if code == 0 else "Issues found",
            "details": "Run 'isort .' to fix" if code != 0 else "Imports sorted correctly",
            "passed": code == 0,
        }
    )

    # Ruff linting
    code, stdout, _ = run_command("ruff check . --quiet")
    issue_count = len(stdout.strip().split("\n")) if stdout.strip() else 0
    checks.append(
        {
            "name": "Ruff Linting",
            "status": "✅" if code == 0 else "⚠️",
            "value": f"{issue_count} issues" if issue_count > 0 else "Clean",
            "details": f"Found {issue_count} linting issues" if issue_count > 0 else "No linting issues",
            "passed": code == 0 or issue_count < 10,
        }
    )

    return checks


def check_security() -> List[Dict]:
    """Run security scans (bandit)."""
    print(f"{Color.BLUE}Checking security...{Color.RESET}")

    checks = []

    # Bandit security scan
    code, stdout, _ = run_command("bandit -r src/ -q -f json")
    if code == 0 or code == 1:  # 0 = no issues, 1 = issues found
        try:
            import json

            data = json.loads(stdout) if stdout else {}
            high_severity = len(
                [r for r in data.get("results", []) if r.get("issue_severity") == "HIGH"]
            )
            medium_severity = len(
                [
                    r
                    for r in data.get("results", [])
                    if r.get("issue_severity") == "MEDIUM"
                ]
            )

            status = "✅" if high_severity == 0 else "❌"
            checks.append(
                {
                    "name": "Bandit Security Scan",
                    "status": status,
                    "value": f"{high_severity} high, {medium_severity} medium",
                    "details": f"High severity: {high_severity}, Medium: {medium_severity}",
                    "passed": high_severity == 0,
                }
            )
        except Exception:
            checks.append(
                {
                    "name": "Bandit Security Scan",
                    "status": "⚠️",
                    "value": "Completed with warnings",
                    "details": "Manual review recommended",
                    "passed": True,
                }
            )
    else:
        checks.append(
            {
                "name": "Bandit Security Scan",
                "status": "❌",
                "value": "Failed",
                "details": "Security scan could not complete",
                "passed": False,
            }
        )

    return checks


def check_dependencies() -> Dict:
    """Check for outdated or vulnerable dependencies."""
    print(f"{Color.BLUE}Checking dependencies...{Color.RESET}")

    code, stdout, _ = run_command("pip list --outdated --format=freeze")
    outdated_count = len(stdout.strip().split("\n")) if stdout.strip() else 0

    status = "✅" if outdated_count == 0 else "⚠️" if outdated_count < 5 else "❌"

    return {
        "name": "Dependency Updates",
        "status": status,
        "value": f"{outdated_count} outdated",
        "details": f"{outdated_count} packages have updates available"
        if outdated_count > 0
        else "All dependencies up to date",
        "passed": outdated_count < 10,
    }


def check_git_status() -> List[Dict]:
    """Check git repository status."""
    print(f"{Color.BLUE}Checking git status...{Color.RESET}")

    checks = []

    # Uncommitted changes
    code, stdout, _ = run_command("git status --porcelain")
    uncommitted = len(stdout.strip().split("\n")) if stdout.strip() else 0
    checks.append(
        {
            "name": "Uncommitted Changes",
            "status": "⚠️" if uncommitted > 0 else "✅",
            "value": f"{uncommitted} files" if uncommitted > 0 else "Clean",
            "details": f"{uncommitted} files with uncommitted changes"
            if uncommitted > 0
            else "Working tree clean",
            "passed": True,  # Not a failure, just informational
        }
    )

    # Branch count
    code, stdout, _ = run_command("git branch -a | wc -l")
    branch_count = int(stdout.strip()) if stdout.strip() else 0
    checks.append(
        {
            "name": "Git Branches",
            "status": "⚠️" if branch_count > 10 else "✅",
            "value": f"{branch_count} branches",
            "details": f"{branch_count} total branches (consider cleanup if >10)"
            if branch_count > 10
            else f"{branch_count} branches",
            "passed": True,
        }
    )

    # Unpushed commits
    code, stdout, _ = run_command("git log @{u}.. --oneline 2>/dev/null | wc -l")
    unpushed = int(stdout.strip()) if stdout.strip() and code == 0 else 0
    checks.append(
        {
            "name": "Unpushed Commits",
            "status": "⚠️" if unpushed > 0 else "✅",
            "value": f"{unpushed} commits" if unpushed > 0 else "Synced",
            "details": f"{unpushed} commits not pushed to remote"
            if unpushed > 0
            else "All commits pushed",
            "passed": True,
        }
    )

    return checks


def check_code_metrics() -> List[Dict]:
    """Check code size and complexity metrics."""
    print(f"{Color.BLUE}Checking code metrics...{Color.RESET}")

    checks = []

    # Total Python files
    code, stdout, _ = run_command("find src/ -name '*.py' | wc -l")
    py_files = int(stdout.strip()) if stdout.strip() else 0

    # Total lines of code
    code, stdout, _ = run_command("find src/ -name '*.py' -exec wc -l {} + | tail -1")
    loc = int(stdout.strip().split()[0]) if stdout.strip() else 0

    # Test files
    code, stdout, _ = run_command("find tests/ -name 'test_*.py' | wc -l")
    test_files = int(stdout.strip()) if stdout.strip() else 0

    checks.append(
        {
            "name": "Code Size",
            "status": "ℹ️",
            "value": f"{py_files} files, {loc:,} LOC",
            "details": f"{py_files} Python files with {loc:,} lines of code",
            "passed": True,
        }
    )

    checks.append(
        {
            "name": "Test Files",
            "status": "ℹ️",
            "value": f"{test_files} files",
            "details": f"{test_files} test files",
            "passed": True,
        }
    )

    return checks


def check_documentation() -> List[Dict]:
    """Check documentation completeness."""
    print(f"{Color.BLUE}Checking documentation...{Color.RESET}")

    checks = []

    # Documentation files
    code, stdout, _ = run_command("find docs/ -name '*.md' | wc -l")
    doc_files = int(stdout.strip()) if stdout.strip() else 0

    # Check for key documentation files
    key_docs = [
        "README.md",
        "context.md",
        "CONTRIBUTING.md",
        "docs/index.md",
        "docs/architecture.md",
        "docs/DEVELOPER_HANDBOOK.md",
    ]
    missing_docs = [doc for doc in key_docs if not Path(doc).exists()]

    checks.append(
        {
            "name": "Documentation Files",
            "status": "✅" if missing_docs == [] else "⚠️",
            "value": f"{doc_files} files",
            "details": f"Missing: {', '.join(missing_docs)}"
            if missing_docs
            else f"{doc_files} documentation files present",
            "passed": len(missing_docs) == 0,
        }
    )

    return checks


def generate_report(results: Dict, output_file: str = None, verbose: bool = False):
    """Generate and display maintenance report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Count passed/failed checks
    all_checks = []
    for category in results.values():
        if isinstance(category, list):
            all_checks.extend(category)
        else:
            all_checks.append(category)

    passed = sum(1 for c in all_checks if c.get("passed", False))
    total = len(all_checks)
    health_score = int((passed / total) * 100) if total > 0 else 0

    # Console output
    print(f"\n{Color.BOLD}{'=' * 70}{Color.RESET}")
    print(f"{Color.BOLD}ZenMarket AI - Maintenance Report{Color.RESET}")
    print(f"Generated: {timestamp}")
    print(f"{'=' * 70}\n")

    print(f"{Color.BOLD}Overall Health Score: {health_score}%{Color.RESET}")
    print(f"Passed: {passed}/{total} checks\n")

    for category_name, category_checks in results.items():
        print(f"{Color.BOLD}{category_name}:{Color.RESET}")

        if isinstance(category_checks, list):
            for check in category_checks:
                status_color = (
                    Color.GREEN
                    if "✅" in check["status"]
                    else Color.YELLOW
                    if "⚠️" in check["status"]
                    else Color.RED
                )
                print(
                    f"  {status_color}{check['status']}{Color.RESET} {check['name']}: {check['value']}"
                )
                if verbose:
                    print(f"      {check['details']}")
        else:
            check = category_checks
            status_color = (
                Color.GREEN
                if "✅" in check["status"]
                else Color.YELLOW
                if "⚠️" in check["status"]
                else Color.RED
            )
            print(
                f"  {status_color}{check['status']}{Color.RESET} {check['name']}: {check['value']}"
            )
            if verbose:
                print(f"      {check['details']}")

        print()

    # Recommendations
    print(f"{Color.BOLD}Recommendations:{Color.RESET}")
    failed_checks = [c for c in all_checks if not c.get("passed", False)]

    if not failed_checks:
        print(f"  {Color.GREEN}✅ All checks passed! Repository in good health.{Color.RESET}")
    else:
        for i, check in enumerate(failed_checks, 1):
            print(f"  {i}. {check['name']}: {check['details']}")

    print(f"\n{Color.BOLD}{'=' * 70}{Color.RESET}\n")

    # Markdown output
    if output_file:
        with open(output_file, "w") as f:
            f.write(f"# ZenMarket AI - Maintenance Report\n\n")
            f.write(f"**Generated:** {timestamp}\n\n")
            f.write(f"## Overall Health Score: {health_score}%\n\n")
            f.write(f"**Passed:** {passed}/{total} checks\n\n")
            f.write("---\n\n")

            for category_name, category_checks in results.items():
                f.write(f"## {category_name}\n\n")

                if isinstance(category_checks, list):
                    for check in category_checks:
                        f.write(
                            f"- {check['status']} **{check['name']}**: {check['value']}\n"
                        )
                        f.write(f"  - {check['details']}\n")
                else:
                    check = category_checks
                    f.write(f"- {check['status']} **{check['name']}**: {check['value']}\n")
                    f.write(f"  - {check['details']}\n")

                f.write("\n")

            f.write("## Recommendations\n\n")
            if not failed_checks:
                f.write("✅ All checks passed! Repository in good health.\n")
            else:
                for i, check in enumerate(failed_checks, 1):
                    f.write(f"{i}. **{check['name']}**: {check['details']}\n")

        print(f"Report saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ZenMarket AI Repository Maintenance Check"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed information"
    )
    parser.add_argument(
        "--output", "-o", type=str, help="Save report to markdown file"
    )

    args = parser.parse_args()

    print(f"{Color.BOLD}ZenMarket AI - Running Maintenance Checks...{Color.RESET}\n")

    results = {
        "Test Coverage": check_test_coverage(),
        "Code Quality": check_code_quality(),
        "Security": check_security(),
        "Dependencies": check_dependencies(),
        "Git Status": check_git_status(),
        "Code Metrics": check_code_metrics(),
        "Documentation": check_documentation(),
    }

    generate_report(results, args.output, args.verbose)

    # Exit with non-zero if critical checks failed
    all_checks = []
    for category in results.values():
        if isinstance(category, list):
            all_checks.extend(category)
        else:
            all_checks.append(category)

    critical_failed = any(
        not c.get("passed", False)
        for c in all_checks
        if c["name"] in ["Test Coverage", "Bandit Security Scan"]
    )

    sys.exit(1 if critical_failed else 0)


if __name__ == "__main__":
    main()
