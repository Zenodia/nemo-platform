#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Script to help identify and add markers to test files based on their location.

This script scans the repository for test files and suggests markers based on:
- Directory structure (e2e/, integration/, etc.)
- Existing markers in the file
- Test patterns

Usage:
    python add_test_markers.py --check      # Check which files need markers
    python add_test_markers.py --apply      # Apply markers (dry-run mode)
    python add_test_markers.py --fix        # Actually apply the markers
"""

import argparse
import re
from pathlib import Path
from typing import List, Set, Tuple


def find_test_files(root_dir: Path) -> List[Path]:
    """Find all Python test files in the repository."""
    test_files = []

    # Search in packages and services
    for pattern in [
        "packages/**/test_*.py",
        "packages/**/*_test.py",
        "services/**/test_*.py",
        "services/**/*_test.py",
        "tests/**/test_*.py",
        "tests/**/*_test.py",
    ]:
        test_files.extend(root_dir.glob(pattern))

    return sorted(set(test_files))


def get_directory_marker(file_path: Path) -> str | None:
    """Determine the marker based on the directory structure."""
    path_str = str(file_path)

    if "/e2e/" in path_str or "/tests/e2e/" in path_str:
        return "e2e"
    elif "/integration/" in path_str or "/tests/integration/" in path_str:
        return "integration"
    elif "/regression/" in path_str or "/tests/regression/" in path_str:
        return "regression"
    elif "/infrastructure/" in path_str or "/tests/infrastructure/" in path_str:
        return "infrastructure"
    elif "/canary/" in path_str or "/tests/canary/" in path_str:
        return "canary"

    return None


def get_existing_markers(file_path: Path) -> Set[str]:
    """Extract existing pytest markers from a file."""
    markers = set()
    content = file_path.read_text()

    # Find @pytest.mark.<marker> patterns
    marker_pattern = r"@pytest\.mark\.(\w+)"
    for match in re.finditer(marker_pattern, content):
        markers.add(match.group(1))

    return markers


def check_file(file_path: Path) -> Tuple[bool, str, Set[str], str | None]:
    """
    Check if a file needs markers.

    Returns:
        (needs_marker, reason, existing_markers, suggested_marker)
    """
    suggested_marker = get_directory_marker(file_path)
    existing_markers = get_existing_markers(file_path)

    # Check if suggested marker is already present
    if suggested_marker and suggested_marker not in existing_markers:
        # Skip if it's a unit test (no marker needed)
        if suggested_marker == "unit":
            return False, "Unit tests don't need markers", existing_markers, None

        return True, f"Missing {suggested_marker} marker", existing_markers, suggested_marker

    return False, "OK", existing_markers, None


def main():
    parser = argparse.ArgumentParser(description="Help manage test markers")
    parser.add_argument("--check", action="store_true", help="Check which files need markers")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent

    # Find all test files
    test_files = find_test_files(repo_root)

    print(f"Found {len(test_files)} test files")
    print()

    if args.stats:
        # Show statistics
        marker_counts = {}
        needs_marker_count = 0

        for file_path in test_files:
            needs_marker, reason, existing, suggested = check_file(file_path)

            if needs_marker:
                needs_marker_count += 1

            for marker in existing:
                marker_counts[marker] = marker_counts.get(marker, 0) + 1

        print("=== Test Marker Statistics ===")
        print(f"Total test files: {len(test_files)}")
        print(f"Files needing markers: {needs_marker_count}")
        print()
        print("Existing markers:")
        for marker, count in sorted(marker_counts.items(), key=lambda x: -x[1]):
            print(f"  {marker}: {count}")
        print()

    if args.check:
        print("=== Files Needing Markers ===")
        needs_markers = []

        for file_path in test_files:
            needs_marker, reason, existing, suggested = check_file(file_path)

            if needs_marker:
                rel_path = file_path.relative_to(repo_root)
                needs_markers.append((rel_path, suggested, existing))

        if needs_markers:
            for rel_path, suggested, existing in needs_markers:
                existing_str = f" (has: {', '.join(existing)})" if existing else ""
                print(f"  {rel_path}")
                print(f"    → Suggest adding: @pytest.mark.{suggested}{existing_str}")
            print()
            print(f"Total: {len(needs_markers)} files need markers")
        else:
            print("All files have appropriate markers!")
        print()

        # Show note about auto-marking
        print("Note: Tests in e2e/ and integration/ directories are automatically")
        print("      marked by conftest.py hooks, but explicit markers are recommended")
        print("      for clarity.")

    if not args.check and not args.stats:
        parser.print_help()


if __name__ == "__main__":
    main()
