#!/usr/bin/env python3
"""
Script to print gcloud compute commands using the gcpcli wrapper.
Reads parsed commands from gcp_commands.json and outputs them
as gcpcli wrapper calls (one per line) suitable for test.sh.
"""

import json
import sys
from pathlib import Path


def to_gcpcli_command(cmd):
    """
    Convert a 'gcloud compute ...' command to use the gcpcli wrapper.

    Example:
        Input:  "gcloud compute instances list --format=json"
        Output: "gcpcli instances list --format=json"
    """
    if cmd.startswith("gcloud compute "):
        return f"gcpcli {cmd[len('gcloud compute '):]}"
    return cmd


def print_commands(json_file, include_id=None, include_file=None):
    """
    Load commands from JSON and print them as gcpcli wrapper calls.

    Args:
        json_file: Path to gcp_commands.json
        include_id: Include commands that use resource IDs (True/False/None=all)
        include_file: Include commands that use file:// parameters (True/False/None=all)
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_commands = 0
    printed_commands = 0

    for resource_path, commands in data.items():
        for cmd_data in commands:
            total_commands += 1

            if cmd_data["use_id"] and not include_id:
                continue
            if cmd_data["use_file"] and not include_file:
                continue

            print(to_gcpcli_command(cmd_data["cmd"]))
            printed_commands += 1

    print(f"\n# Total commands: {total_commands}", file=sys.stderr)
    print(f"# Printed: {printed_commands}", file=sys.stderr)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Print gcloud compute commands using the gcpcli wrapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Print all commands
  python print_commands_with_endpoint.py

  # Print only commands without ID parameters
  python print_commands_with_endpoint.py

  # Include commands with ID parameters
  python print_commands_with_endpoint.py --include-id

  # Save to test.sh
  python print_commands_with_endpoint.py > test.sh
        """,
    )

    parser.add_argument(
        "--json-file",
        "-j",
        default="cli/gcp_commands.json",
        help="Path to JSON file (default: cli/gcp_commands.json)",
    )

    parser.add_argument(
        "--include-file",
        action="store_true",
        help="Include commands that use file parameters",
    )

    parser.add_argument(
        "--include-id",
        action="store_true",
        help="Include commands that use ID parameters",
    )

    args = parser.parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    print_commands(json_path, args.include_id, args.include_file)


if __name__ == "__main__":
    main()
