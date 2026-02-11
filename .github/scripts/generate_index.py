#!/usr/bin/env python3

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

"""
libhal API Index Data Generator

Scans the api repository directory for library subdirectories and their
versions, then outputs a libraries.json file. This file is consumed by
the index.html front page to render the library directory.

Usage:
    python3 generate_index.py /path/to/api/repo
    python3 generate_index.py /path/to/api/repo --output /path/to/libraries.json
"""

import argparse
import json
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".github"}


def discover_libraries(repo_dir: Path) -> list[dict]:
    """
    Scan the repo directory for library subdirectories and read their
    switcher.json to determine available versions.

    Returns a sorted list of dicts with keys: name, versions, latest_url
    """
    libraries = []

    for entry in sorted(repo_dir.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in SKIP_DIRS or entry.name.startswith("."):
            continue

        switcher_path = entry / "switcher.json"
        switcher_versions = []
        if switcher_path.exists():
            try:
                with open(switcher_path) as f:
                    switcher_versions = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        # Determine version subdirectories
        version_dirs = sorted(
            [d.name for d in entry.iterdir()
             if d.is_dir() and d.name != ".git"],
        )

        if not version_dirs:
            continue

        # Build version list with URLs
        versions = []
        for v in version_dirs:
            match = next(
                (sv for sv in switcher_versions if sv["version"] == v),
                None,
            )
            url = match["url"] if match else f"{entry.name}/{v}"
            versions.append({"version": v, "url": url})

        # Latest is the last entry (highest semver or last branch)
        latest_url = versions[-1]["url"]

        libraries.append({
            "name": entry.name,
            "versions": versions,
            "latest_url": latest_url,
        })

    return libraries


def main():
    parser = argparse.ArgumentParser(
        description="Generate libraries.json for the libhal API docs site")
    parser.add_argument(
        "repo_dir",
        help="Path to the root of the api repository")
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: <repo_dir>/libraries.json)")

    args = parser.parse_args()

    repo_dir = Path(args.repo_dir)
    if not repo_dir.is_dir():
        print(f"Error: {repo_dir} is not a directory")
        return 1

    libraries = discover_libraries(repo_dir)

    if not libraries:
        print("Warning: No library directories found")

    output_path = (
        Path(args.output) if args.output else repo_dir / "libraries.json"
    )
    with open(output_path, "w") as f:
        json.dump(libraries, f, indent=2)

    print(f"Generated {output_path} with {len(libraries)} libraries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
