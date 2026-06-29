from __future__ import annotations

from pathlib import Path


WatchedEntry = tuple[str, str]


def load_watched(path: Path) -> set[WatchedEntry]:
    if not path.is_file():
        return set()

    entries: set[WatchedEntry] = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if "/" not in line:
            continue
        category, filename = line.split("/", 1)
        entries.add((category, filename))
    return entries


def save_watched(path: Path, entries: set[WatchedEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = sorted(f"{category}/{filename}" for category, filename in entries)
    path.write_text("\n".join(lines) + ("\n" if lines else ""))


def reset_category(path: Path, category: str) -> None:
    entries = load_watched(path)
    entries = {entry for entry in entries if entry[0] != category}
    save_watched(path, entries)


def reset_all(path: Path) -> None:
    save_watched(path, set())


def is_watched(entries: set[WatchedEntry], category: str, filename: str) -> bool:
    return (category, filename) in entries


def add_entries(entries: set[WatchedEntry], new_entries: set[WatchedEntry]) -> None:
    entries.update(new_entries)
