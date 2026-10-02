# Story 2.3: done-item

Status: in-progress

## Story

Someone using the todo CLI can `add` items (story 2-1) and see them with `list`
(story 2-2), which already renders `[x]` for a done item — but nothing can set the `done`
flag short of editing `todo.json` by hand. `done <id>` marks the item with that id done,
saves the file, and prints `done #<id>: <text>`; an id that matches no item prints
`no item #<id>` on stderr and exits 1. It is the first command that changes an existing
item and the first with an error exit other than usage; story 2-4 (`remove`) reuses its
unknown-id behaviour, so it comes now.

## Acceptance Criteria

1. `python3 todo.py done <id>` where `<id>` matches an item in the file named by
   `TODO_FILE` sets that item's `"done"` to `true` in the file, prints
   `done #<id>: <text>` on stdout, and exits 0.
2. Only the matched item changes: every other item, the item's `id` and `text`, and the
   order of items in the file are unchanged.
3. Marking an item that is already done succeeds the same way (prints
   `done #<id>: <text>`, exits 0, item stays `"done": true`).
4. When `<id>` matches no item — including when `TODO_FILE` does not exist or holds an
   empty list — `done` prints `no item #<id>` on stderr, prints nothing on stdout, exits 1,
   and does not create or modify the file.
5. A `<id>` that is not an integer (e.g. `done abc`) is treated as an unknown id: it
   prints `no item #abc` on stderr and exits 1, with no traceback.
6. `done` with no id prints usage on stderr and exits 2, like any other malformed command.
7. Existing behaviour is unchanged: `add` and `list` work as in stories 2-1 and 2-2, and an
   unknown or missing command still prints usage on stderr and exits 2. After
   `done <id>`, `list` shows that item as `#<id> [x] <text>`.

## Tasks / Subtasks

- [x] Task 1 — add a `done(item_id)` function to `todo.py` beside `add()` / `list_items()`
  that calls `load()`, finds the item whose `id` equals `item_id`, sets `"done": True`,
  calls `save()`, and returns the item; return `None` (and do not call `save()`) when no
  item matches (AC: 1, 2, 3, 4)
- [x] Task 2 — add a `done` branch to `main(argv)` in `todo.py`, after `list` and before
  the usage fallthrough, matching `len(argv) >= 2 and argv[0] == "done"` (AC: 1, 4, 5, 6)
  - [x] Parse `argv[1]` with `int()`; on `ValueError`, or when `done()` returns `None`,
    `print(f"no item #{argv[1]}", file=sys.stderr)` and return 1; otherwise print
    `done #<id>: <text>` and return 0
  - [x] Add `python3 todo.py done 1` to the module docstring's usage example (keep the
    `todo.py add` line — `test_no_command_prints_usage_and_exits_2` asserts on it)
- [x] Task 3 — add a `DoneTests` class to `test_todo.py`, with the same `setUp` as
  `AddTests` / `ListTests`, covering: done on an added item prints the line, exits 0 and
  the file shows `"done": true`; with two items only the target changes; done twice
  succeeds; unknown id on a populated file → stderr `no item #9`, exit 1, empty stdout,
  file byte-identical; unknown id with no file → exit 1 and the file is still absent;
  `done abc` → `no item #abc`, exit 1; `done` alone → exit 2; `list` after `done` shows
  `[x]` (AC: 1–7)
- [x] Task 4 — run `python3 -m unittest` and confirm every test passes (AC: 7)

### Review Findings

- [ ] [Review][Decision] Non-integer id exit code (AC 5, Create-step addition not in the epic; inherited by 2-4 "unknown id behaves as in 2-3") — options: (a) keep as is: `done abc` → `no item #abc` on stderr, exit 1 (same as an unknown id); (b) treat a non-integer id as a malformed command: print usage on stderr, exit 2, so exit 1 means only "well-formed id, no such item"; (c) a distinct message such as `invalid id: abc` on stderr with exit 1 or 2
- [x] [Review][Patch] AC 4 "holds an empty list" case untested, and AC 5 test does not assert empty stdout — added `test_unknown_id_with_empty_list_leaves_file_alone` and a stdout assertion [test_todo.py:140]

## Dev Notes

### What exists — read these before writing a line

- `todo.py` line 15 — `load()` returns `[]` when `TODO_FILE` is missing, so the no-file
  case in AC 4 falls out of "no item matched"; just do not call `save()` on that path, or
  the file gets created.
- `todo.py` line 22 — `save(items)` rewrites the whole file (`indent=2` plus a trailing
  newline). Mutating the matched dict in the loaded list and saving that list keeps the
  other items and their order as they were (AC 2).
- `todo.py` line 28 — `add(text)`: the shape of a command function (load, do the work,
  save, return data); printing lives in `main`, not in the function. `list_items()` at
  line 37 follows the same split. Do the same for `done`.
- `todo.py` line 42 — `main(argv)`: one `if` per command (`add` at 43, `list` at 47), then
  the usage fallthrough at 52 (`print(__doc__.strip(), file=sys.stderr); return 2`). The
  `done` branch requires `len(argv) >= 2` so that bare `done` falls through to usage
  (AC 6), the same way bare `add` does today. Keep the fallthrough last.
- Item shape, from `add()` line 31: `{"id": int, "text": str, "done": bool}`. Ids are ints
  in the file, so compare against `int(argv[1])`, not the raw string.
- `test_todo.py` line 12 — `run(*args, env=)` runs the CLI as a subprocess;
  `ListTests.setUp` (line 41) builds a temp dir and an `env` with `TODO_FILE` in it.
  `test_list_does_not_modify_the_file` (line 78) is the byte-identical-file pattern to
  reuse for AC 4; `test_done_item_and_out_of_order_ids_print_marked_and_sorted` (line 65)
  shows writing the JSON file directly when a test needs a specific starting state.
- `implement-next-story.toml` — `check = ["python3 -m unittest"]`; CI
  (`.github/workflows/ci.yml`) runs `python3 -m unittest -v`. Stdlib only.

### What NOT to build

- `remove <id>` — story 2-4. It will reuse the same unknown-id message and exit code; a
  small shared lookup is welcome if it falls out naturally, but do not add `remove` here.
- `undone` / toggling back to pending — not in any epic entry. `done` only ever sets true.
- Multiple ids in one call (`done 1 2`) — the epic says `done <id>`; extra arguments after
  the id may be ignored, they need no handling or test.
- `--file PATH` — story 3-1; `done` reads `TODO_FILE` from the environment like `add`.
- `clear` — story 3-2.
- No argparse, no colour, no changes to `list` output.

### References

- `docs/planning-artifacts/epics.md`, `## Epic 2: Core commands`, entry
  **2-3-done-item**: "`done <id>`: marks the item done and prints `done #<id>: <text>`;
  an unknown id prints `no item #<id>` on stderr and exits 1."
- Same section, entry **2-4-remove-item**: "an unknown id behaves as in 2-3" — why the
  error path must be exact.
- Same section, entry **2-2-list-items** — the `[x]` rendering AC 7 checks through.
- AC 3 (re-marking a done item succeeds) and AC 5 (non-integer id is an unknown id) are not
  spelled out in the epic entry; they are the least-surprising reading of it and are
  pinned here so the dev does not have to choose.

## Dev Agent Record

### File List

- todo.py
- test_todo.py
- docs/implementation-artifacts/2-3-done-item.md
- docs/implementation-artifacts/sprint-status.yaml

### Completion Notes

`done(item_id)` mirrors `add()`; main() maps ValueError and None to the shared `no item #<arg>` / exit 1 path. `save()` is only called on a match, so a missing file is never created. 8 DoneTests added; `python3 -m unittest` passes.

---

The two lines below are the orchestrator's; Create writes them, Implement and Review leave
them as they are, and the run stats are appended after them.

Dev Model: sonnet   # follows the add()/list_items()/main() pattern in todo.py; one mutating command plus a fixed stderr/exit-1 path
Proposed lane gate: none
