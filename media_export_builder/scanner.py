from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MediaFile:
    category: str
    filename: str
    source_path: Path


@dataclass
class CategoryScanResult:
    category: str
    files: list[MediaFile]
    duplicates: dict[str, list[Path]]


def scan_category(
    source_directory: Path,
    supported_extensions: frozenset[str],
) -> CategoryScanResult:
    category = source_directory.name
    by_filename: dict[str, list[Path]] = {}

    for path in source_directory.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in supported_extensions:
            continue
        by_filename.setdefault(path.name, []).append(path)

    duplicates = {
        filename: sorted(paths) for filename, paths in by_filename.items() if len(paths) > 1
    }

    files: list[MediaFile] = []
    for filename, paths in sorted(by_filename.items()):
        representative = sorted(paths)[0]
        files.append(
            MediaFile(
                category=category,
                filename=filename,
                source_path=representative,
            )
        )

    return CategoryScanResult(category=category, files=files, duplicates=duplicates)
