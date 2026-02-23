#!/usr/bin/env python3
"""
Parser to extract gcloud compute commands and their expected outputs
from the gcp_commands.json test file.
"""

import json
import re
from pathlib import Path


def has_id_parameter(command):
    """Check if command contains any ID-related flags."""
    id_patterns = [
        r"--[\w-]*-id\b",
        r"--id\b",
        r"--[\w-]*-ids\b",
    ]
    for pattern in id_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def has_file_parameter(command):
    """Check if command contains any file:// parameters."""
    return bool(re.search(r"file://", command, re.IGNORECASE))


def load_commands(json_file, include_id=False, include_file=False):
    """
    Load gcloud compute commands from gcp_commands.json.

    Args:
        json_file: Path to gcp_commands.json
        include_id: Include commands that reference resource IDs
        include_file: Include commands that use file:// parameters

    Returns:
        List of dicts with 'cmd', 'use_id', 'use_file', 'output' keys
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for resource_path, commands in data.items():
        for entry in commands:
            use_id = entry.get("use_id", False)
            use_file = entry.get("use_file", False)

            if use_id and not include_id:
                continue
            if use_file and not include_file:
                continue

            results.append(
                {
                    "resource": resource_path,
                    "cmd": entry["cmd"],
                    "use_id": use_id,
                    "use_file": use_file,
                    "output": entry.get("output", ""),
                }
            )

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse gcloud compute commands from gcp_commands.json"
    )
    parser.add_argument(
        "json_file",
        nargs="?",
        default="../cli/gcp_commands.json",
        help="Path to gcp_commands.json (default: ../cli/gcp_commands.json)",
    )
    parser.add_argument("--include-id", action="store_true")
    parser.add_argument("--include-file", action="store_true")
    args = parser.parse_args()

    commands = load_commands(args.json_file, args.include_id, args.include_file)
    for c in commands:
        print(c["cmd"])


if __name__ == "__main__":
    main()
