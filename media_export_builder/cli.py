from __future__ import annotations

import argparse
import sys
from pathlib import Path

from media_export_builder.config import ConfigError, load_config
from media_export_builder.pipeline import DestinationValidationError, run_and_report
from media_export_builder.watched import reset_all, reset_category

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.yaml"


def default_config_path() -> Path:
    return DEFAULT_CONFIG_PATH


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate media exports from a media library.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to the YAML configuration file.",
    )
    parser.add_argument(
        "--reset-category",
        metavar="CATEGORY",
        help="Remove all watched entries for the specified category.",
    )
    parser.add_argument(
        "--reset-all",
        action="store_true",
        help="Remove all entries from the watched file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_path = args.config if args.config is not None else default_config_path()

    try:
        config = load_config(config_path)
    except ConfigError as exc:
        print(f"ERROR\n{exc}", file=sys.stderr)
        return 1

    if args.reset_category is not None and args.reset_all:
        print(
            "ERROR\n--reset-category and --reset-all cannot be used together.",
            file=sys.stderr,
        )
        return 3

    if args.reset_category is not None:
        category = args.reset_category.strip()
        if not category:
            print("ERROR\n--reset-category requires a non-empty category name.", file=sys.stderr)
            return 3
        try:
            reset_category(config.watched_file_path, category)
        except OSError as exc:
            print(f"ERROR\n{exc}", file=sys.stderr)
            return 4

    if args.reset_all:
        try:
            reset_all(config.watched_file_path)
        except OSError as exc:
            print(f"ERROR\n{exc}", file=sys.stderr)
            return 4

    if args.reset_category is not None or args.reset_all:
        return 0

    try:
        run_and_report(config)
    except ConfigError as exc:
        print(f"ERROR\n{exc}", file=sys.stderr)
        return 1
    except DestinationValidationError as exc:
        print(f"ERROR\n{exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR\n{exc}", file=sys.stderr)
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
