#!/usr/bin/env python3
"""
Script to print AWS CLI commands using the awscli wrapper.
Reads parsed commands from aws_commands.json and outputs them
as awscli wrapper calls (one per line) suitable for test.sh.
"""

import json
import sys
from pathlib import Path


def to_awscli_command(cmd):
    """
    Convert an 'aws ...' command to use the awscli wrapper.

    Example:
        Input:  "aws ec2 describe-instances --region us-east-1"
        Output: "awscli ec2 describe-instances --region us-east-1"
    """
    if not cmd.startswith('aws '):
        return cmd
    return f"awscli {cmd[4:]}"


def print_commands(json_file, include_id=None, include_file=None):
    """
    Load commands from JSON and print them as awscli wrapper calls.

    Args:
        json_file: Path to the JSON file
        include_id: Include commands that require ID parameters
        include_file: Include commands that require file:// parameters
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_commands = 0
    printed_commands = 0

    for file_path, commands in data.items():
        for cmd_data in commands:
            total_commands += 1

            # Apply include filters if specified
            if cmd_data['use_id'] and not include_id:
                continue
            if cmd_data['use_file'] and not include_file:
                continue

            print(to_awscli_command(cmd_data['cmd']))
            printed_commands += 1

    # Print summary to stderr so it doesn't interfere with command output
    print(f"\n# Total commands: {total_commands}", file=sys.stderr)
    print(f"# Printed: {printed_commands}", file=sys.stderr)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Print AWS CLI commands using the awscli wrapper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Print all commands
  python print_commands_with_endpoint.py

  # Print only commands without ID parameters
  python print_commands_with_endpoint.py

  # Print commands with ID parameters too
  python print_commands_with_endpoint.py --include-id

  # Save to test.sh
  python print_commands_with_endpoint.py > test.sh
        """
    )

    parser.add_argument(
        '--json-file',
        '-j',
        default='aws_commands.json',
        help='Path to JSON file (default: aws_commands.json)'
    )

    parser.add_argument(
        '--include-file',
        action='store_true',
        help='Include commands that use file parameters'
    )

    parser.add_argument(
        '--include-id',
        action='store_true',
        help='Include commands that use ID parameters'
    )

    args = parser.parse_args()

    # Check if JSON file exists
    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    print_commands(json_path, args.include_id, args.include_file)


if __name__ == "__main__":
    main()
