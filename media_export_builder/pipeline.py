from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from media_export_builder.config import Config, ConfigError
from media_export_builder.exporter import export_category
from media_export_builder.report import CategoryReport, print_report
from media_export_builder.scanner import CategoryScanResult, scan_category
from media_export_builder.watched import (
    WatchedEntry,
    add_entries,
    is_watched,
    load_watched,
    save_watched,
)


class DestinationValidationError(Exception):
    pass


@dataclass
class PipelineResult:
    category_reports: list[CategoryReport]
    duplicate_results: list[CategoryScanResult]


def validate_destination(target_root: Path) -> None:
    if not target_root.exists():
        raise DestinationValidationError(
            f"Target root directory does not exist:\n{target_root}"
        )
    if not target_root.is_dir():
        raise DestinationValidationError(
            f"Target root directory is not a directory:\n{target_root}"
        )
    contents = list(target_root.iterdir())
    if contents:
        raise DestinationValidationError(
            "Target root directory is not empty:\n"
            f"{target_root}\n"
            "Please remove the existing export before running the application."
        )


def validate_source_directories(config: Config) -> None:
    for source_directory in config.source_directories:
        if not source_directory.is_dir():
            raise ConfigError(f"Source directory does not exist: {source_directory}")


def run_export(config: Config) -> PipelineResult:
    validate_source_directories(config)
    validate_destination(config.target_root_directory)

    watched_entries = load_watched(config.watched_file_path)
    category_reports: list[CategoryReport] = []
    duplicate_results: list[CategoryScanResult] = []

    for source_directory in config.source_directories:
        scan_result = scan_category(source_directory, config.supported_extensions)
        duplicate_results.append(scan_result)

        unwatched = [
            media_file
            for media_file in scan_result.files
            if not is_watched(watched_entries, media_file.category, media_file.filename)
        ]

        exported = export_category(
            unwatched,
            config.target_root_directory,
            config.files_per_export,
        )

        new_entries: set[WatchedEntry] = {
            (item.media_file.category, item.media_file.filename) for item in exported
        }
        add_entries(watched_entries, new_entries)
        save_watched(config.watched_file_path, watched_entries)

        watched_count = sum(
            1 for category, _ in watched_entries if category == scan_result.category
        )
        remaining = len(unwatched) - len(exported)

        category_reports.append(
            CategoryReport(
                category=scan_result.category,
                added=len(exported),
                watched=watched_count,
                remaining=remaining,
            )
        )

    return PipelineResult(
        category_reports=category_reports,
        duplicate_results=duplicate_results,
    )


def run_and_report(config: Config) -> PipelineResult:
    result = run_export(config)
    print_report(result.category_reports, result.duplicate_results)
    return result
