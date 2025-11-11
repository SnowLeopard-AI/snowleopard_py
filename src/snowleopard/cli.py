import dataclasses
import json
import sys
import argparse
from typing import List, Optional

from httpx import HTTPStatusError
from snowleopard import __version__, SnowLeopardClient
from snowleopard.models import RetrieveResponseError


def _create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="snowy", description="SnowLeopard.ai client library CLI"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument("--loc", "-l", required=False, help="Snowleopard location")
    parser.add_argument("--token", "-t", required=False, help="Snowleopard token")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    retrieve = subparsers.add_parser(
        "retrieve", help="Retrieve data from natural language"
    )
    retrieve.add_argument("datafile", type=str, help="Datafile to query")
    retrieve.add_argument("question", type=str, help="Natural language query")

    return parser


def _get_client(parsed_args):
    try:
        client = SnowLeopardClient(parsed_args.loc, parsed_args.token)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    return client


def main(args: Optional[List[str]] = None) -> None:
    """CLI entry point for snowleopard."""
    parser = _create_parser()
    parsed_args = parser.parse_args(args=args)

    if parsed_args.command == "retrieve":
        try:
            with _get_client(parsed_args) as client:
                resp = client.retrieve(parsed_args.datafile, parsed_args.question)
                print(json.dumps(dataclasses.asdict(resp)))
                if isinstance(resp, RetrieveResponseError):
                    sys.exit(1)
        except HTTPStatusError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
    elif parsed_args.command is None:
        parser.print_help(file=sys.stderr)
        sys.exit(1)
