from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from media_export_builder.scanner import CategoryScanResult


@dataclass
class CategoryReport:
    category: str
    added: int
    watched: int
    remaining: int


def print_report(
    category_reports: list[CategoryReport],
    duplicate_results: list[CategoryScanResult],
) -> None:
    print("Export Summary")
    print()
    for report in category_reports:
        print(f"Category: {report.category}")
        print(f"Added: {report.added}")
        print(f"Watched: {report.watched}")
        print(f"Remaining: {report.remaining}")
        print()

    duplicates = [result for result in duplicate_results if result.duplicates]
    if not duplicates:
        return

    print("Duplicate Filenames")
    print()
    for result in duplicates:
        print(f"Category: {result.category}")
        for filename, paths in sorted(result.duplicates.items()):
            print(filename)
            for path in paths:
                print(f"    {path}")
        print()
