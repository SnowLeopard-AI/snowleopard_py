import sys
import argparse
from typing import List, Optional

from snowleopard import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="snowy", description="SnowLeopard.ai client library CLI"
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add a simple 'hello' command as an example
    hello_parser = subparsers.add_parser("hello", help="Print a greeting")
    hello_parser.add_argument("--name", type=str, default="World", help="Name to greet")

    return parser


def main(args: Optional[List[str]] = None) -> None:
    """CLI entry point for snowleopard."""
    parser = create_parser()
    parsed_args = parser.parse_args(args=args)

    if parsed_args.command == "hello":
        print(f"Hello from snowleopard, {parsed_args.name}!")
    elif parsed_args.command is None:
        parser.print_help()
        sys.exit(1)
