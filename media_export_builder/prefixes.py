from __future__ import annotations

import random

PREFIX_WEIGHTS: list[tuple[str, float]] = [
    ("00", 0.10),
    ("02", 0.30),
    ("04", 0.30),
    ("06", 0.30),
]


def allocate_prefixes(count: int) -> list[str]:
    if count == 0:
        return []

    raw = [(prefix, count * weight) for prefix, weight in PREFIX_WEIGHTS]
    floors = [(prefix, int(quota)) for prefix, quota in raw]
    assigned = sum(floor for _, floor in floors)
    remainders = sorted(
        ((quota - floor, prefix) for (prefix, quota), (_, floor) in zip(raw, floors)),
        reverse=True,
    )

    result: dict[str, int] = {prefix: floor for prefix, floor in floors}
    for _, prefix in remainders:
        if assigned >= count:
            break
        result[prefix] += 1
        assigned += 1

    prefixes: list[str] = []
    for prefix, _ in PREFIX_WEIGHTS:
        prefixes.extend([prefix] * result[prefix])
    return prefixes


def assign_prefixes(files: list, count: int) -> list[tuple]:
    shuffled = files.copy()
    random.shuffle(shuffled)
    prefixes = allocate_prefixes(count)
    random.shuffle(prefixes)
    return list(zip(shuffled, prefixes))
