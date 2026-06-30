from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import NoReturn

from peerpath import __version__


class PeerPathParser(argparse.ArgumentParser):
    """ArgumentParser that returns control to tests instead of exiting."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        raise SystemExit(f"peerpath: error: {message}")


def build_parser() -> argparse.ArgumentParser:
    parser = PeerPathParser(
        prog="peerpath",
        description="Read-only reachability doctor for Dockerized wg-easy setups.",
    )
    parser.add_argument("--version", action="version", version=f"peerpath {__version__}")

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    doctor = subparsers.add_parser(
        "doctor",
        help="run read-only diagnostics from a fixture or future live collector",
        description="Run PeerPath diagnostics. v0.1 only supports fixture input.",
    )
    doctor.add_argument(
        "--fixture",
        help="path to a synthetic fixture directory to diagnose",
    )
    doctor.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="report format (default: markdown)",
    )

    fixture = subparsers.add_parser(
        "fixture",
        help="inspect or generate synthetic fixtures",
        description="Work with public-safe synthetic fixtures.",
    )
    fixture.add_argument(
        "action",
        nargs="?",
        choices=("list",),
        default="list",
        help="fixture action (default: list)",
    )
    fixture.add_argument(
        "--fixtures-dir",
        default="tests/fixtures",
        help="directory containing fixture folders",
    )

    explain = subparsers.add_parser(
        "explain",
        help="explain a PeerPath finding id",
        description=(
            "Explain a diagnostic finding id. "
            "Detailed explanations land after rules exist."
        ),
    )
    explain.add_argument("finding_id", nargs="?", help="finding id to explain")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 2

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "doctor":
        if not args.fixture:
            print(
                "peerpath doctor is read-only in v0.1 and requires --fixture until "
                "live collection is implemented.",
                file=sys.stderr,
            )
            return 2
        print(
            "fixture-backed diagnostics are not implemented yet; "
            "this command surface is reserved for the next task.",
            file=sys.stderr,
        )
        return 2

    if args.command == "fixture":
        print(f"fixture {args.action}: {args.fixtures_dir}")
        return 0

    if args.command == "explain":
        if not args.finding_id:
            print("peerpath explain requires a finding id", file=sys.stderr)
            return 2
        print(f"No explanation is available yet for {args.finding_id}.")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
