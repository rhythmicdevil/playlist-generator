from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    source_directories: list[Path]
    target_root_directory: Path
    files_per_export: int
    watched_file_path: Path
    supported_extensions: frozenset[str]


def _normalize_extension(ext: str) -> str:
    ext = ext.strip().lower()
    if not ext.startswith("."):
        ext = f".{ext}"
    return ext


def load_config(path: Path) -> Config:
    if not path.is_file():
        raise ConfigError(f"Configuration file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        raise ConfigError(f"Failed to parse configuration file: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("Configuration file must contain a YAML mapping")

    source_directories = raw.get("source_directories")
    if not source_directories or not isinstance(source_directories, list):
        raise ConfigError("source_directories must be a non-empty list")

    source_paths: list[Path] = []
    for entry in source_directories:
        if not isinstance(entry, str):
            raise ConfigError("Each source directory must be a string path")
        source_paths.append(Path(entry))

    target_root = raw.get("target_root_directory")
    if not target_root or not isinstance(target_root, str):
        raise ConfigError("target_root_directory must be a string path")

    files_per_export = raw.get("files_per_export")
    if not isinstance(files_per_export, int) or files_per_export < 1:
        raise ConfigError("files_per_export must be a positive integer")

    watched_file_path = raw.get("watched_file_path")
    if not watched_file_path or not isinstance(watched_file_path, str):
        raise ConfigError("watched_file_path must be a string path")

    supported_extensions = raw.get("supported_extensions")
    if not supported_extensions or not isinstance(supported_extensions, list):
        raise ConfigError("supported_extensions must be a non-empty list")

    extensions: set[str] = set()
    for ext in supported_extensions:
        if not isinstance(ext, str) or not ext.strip():
            raise ConfigError("Each supported extension must be a non-empty string")
        extensions.add(_normalize_extension(ext))

    return Config(
        source_directories=source_paths,
        target_root_directory=Path(target_root),
        files_per_export=files_per_export,
        watched_file_path=Path(watched_file_path),
        supported_extensions=frozenset(extensions),
    )
