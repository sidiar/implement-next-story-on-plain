#!/usr/bin/env python3
"""A tiny todo list kept in a JSON file — the throwaway project the `plain` adapter of
implement-next-story is demonstrated on. Stdlib only.

    python3 todo.py add "buy milk"
"""
import json
import os
import sys

TODO_FILE = os.environ.get("TODO_FILE", "todo.json")


def load() -> list[dict]:
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE) as fh:
        return json.load(fh)


def save(items: list[dict]) -> None:
    with open(TODO_FILE, "w") as fh:
        json.dump(items, fh, indent=2)
        fh.write("\n")


def add(text: str) -> dict:
    """Append an item with the next free id and return it."""
    items = load()
    item = {"id": (max((i["id"] for i in items), default=0) + 1), "text": text, "done": False}
    items.append(item)
    save(items)
    return item


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "add":
        item = add(" ".join(argv[1:]))
        print(f"added #{item['id']}: {item['text']}")
        return 0
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
