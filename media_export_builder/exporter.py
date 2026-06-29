from __future__ import annotations

import random
import shutil
from dataclasses import dataclass
from pathlib import Path

from media_export_builder.prefixes import assign_prefixes
from media_export_builder.scanner import MediaFile


@dataclass(frozen=True)
class ExportedFile:
    media_file: MediaFile
    prefix: str
    destination_path: Path


def export_category(
    files: list[MediaFile],
    target_root: Path,
    files_per_export: int,
) -> list[ExportedFile]:
    if not files:
        return []

    selected = files.copy()
    random.shuffle(selected)
    selected = selected[:files_per_export]

    category_dir = target_root / files[0].category
    category_dir.mkdir(parents=True, exist_ok=True)

    exported: list[ExportedFile] = []
    for media_file, prefix in assign_prefixes(selected, len(selected)):
        destination = category_dir / f"{prefix}-{media_file.filename}"
        shutil.copy2(media_file.source_path, destination)
        exported.append(
            ExportedFile(
                media_file=media_file,
                prefix=prefix,
                destination_path=destination,
            )
        )
    return exported
