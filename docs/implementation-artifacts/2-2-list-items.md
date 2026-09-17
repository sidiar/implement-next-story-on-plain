# Story 2.2: list-items

Status: done

## Story

Someone using the todo CLI can `add` items (story 2-1) but has no way to see them back
short of opening `todo.json`. `list` prints one line per item, `#<id> [ ] <text>` or
`#<id> [x] <text>` when done, in id order, and prints nothing (exit 0) when the list is
empty. It is the second command on the `main(argv)` dispatcher and the read-side
counterpart of `add`; stories 2-3 (`done`) and 2-4 (`remove`) will be verified through it,
so it comes now.

## Acceptance Criteria

1. `python3 todo.py list` prints one line per item in the JSON file named by `TODO_FILE`,
   in ascending id order, and exits 0.
2. An item with `"done": false` prints as `#<id> [ ] <text>`; an item with `"done": true`
   prints as `#<id> [x] <text>`.
3. When `TODO_FILE` does not exist, or holds an empty list, `list` prints nothing to stdout
   and exits 0.
4. `list` does not modify the JSON file.
5. Existing behaviour is unchanged: `add` still works as in story 2-1, and an unknown or
   missing command still prints usage on stderr and exits 2.

## Tasks / Subtasks

- [x] Task 1 — add a `list_items()` function to `todo.py` beside `add()` that calls
  `load()` and returns the items sorted by `id` (AC: 1, 4)
- [x] Task 2 — add a `list` branch to `main(argv)` in `todo.py`, before the usage
  fallthrough, that prints each item as `#<id> [ ] <text>` / `#<id> [x] <text>` and
  returns 0 (AC: 1, 2, 3, 5)
  - [x] Update the module docstring's usage example so `list` appears next to `add`
    (the docstring is what the usage message prints; `test_no_command_prints_usage_and_exits_2`
    asserts `"todo.py add"` is in it, so keep that line)
- [x] Task 3 — add a `ListTests` class to `test_todo.py`, with the same `setUp` as
  `AddTests`, covering: empty (no file) prints nothing and exits 0; two added items print
  two `[ ]` lines in id order; a file written directly with a done item and out-of-order
  ids prints `[x]` and sorts by id; the file is byte-identical after `list` (AC: 1–4)
- [x] Task 4 — run `python3 -m unittest` and confirm every test passes (AC: 5)

### Review Findings

- [x] [Review][Patch] AC 3's "holds an empty list" case had no test — only the missing-file
  case was covered; added `test_empty_list_file_prints_nothing_and_exits_0` [test_todo.py:51]
- [x] [Review][Defer] `tempfile.mkdtemp()` in `setUp` is never removed, so every test run
  leaks a temp dir [test_todo.py:18, test_todo.py:42] — deferred: pre-existing pattern from
  `AddTests` (story 2-1) that Task 3 told the dev to copy; a `tearDown` / `TemporaryDirectory`
  cleanup belongs to a test-hygiene change across both classes, not this story

## Dev Notes

### What exists — read these before writing a line

- `todo.py` line 11 — `TODO_FILE = os.environ.get("TODO_FILE", "todo.json")`; `load()`
  (line 14) returns `[]` when the file is missing, so the empty case in AC 3 needs no
  special-casing beyond iterating an empty list.
- `todo.py` line 27 — `add(text)`: the shape of a command function (calls `load()`,
  does the work, returns data); the print lives in `main`, not in the function. Follow
  the same split for `list`.
- `todo.py` line 36 — `main(argv)`: a single `if` for `add` followed by the usage
  fallthrough (`print(__doc__.strip(), file=sys.stderr); return 2`). Add the `list`
  branch as a second `if` on `argv[0]`; `list` takes no arguments, so match
  `argv == ["list"]` or `argv[0] == "list"` — either is fine, but keep the usage
  fallthrough last.
- Item shape, from `add()` and `test_add_creates_the_file_with_one_item`:
  `{"id": int, "text": str, "done": bool}`. `add` assigns the next free id as
  `max(ids) + 1`, so ids are unique but a hand-edited file may be unordered — sort.
- `test_todo.py` line 12 — `run(*args, env=)` runs the CLI as a subprocess and returns
  the `CompletedProcess`; `AddTests.setUp` (line 17) builds a temp dir and an `env`
  with `TODO_FILE` pointing into it. Reuse both; assert on `result.stdout`,
  `result.returncode` and the file's contents, as the existing tests do.
- `implement-next-story.toml` — `check = ["python3 -m unittest"]`; CI
  (`.github/workflows/ci.yml`) runs `python3 -m unittest -v` on Python 3.12. Stdlib only.

### What NOT to build

- `done <id>` / `remove <id>` — stories 2-3 and 2-4. `list` only reads the `done` flag;
  nothing in this story sets it. Tests that need a done item write the JSON file directly.
- `--file PATH` — story 3-1. `list` reads `TODO_FILE` from the environment like `add`.
- `clear` — story 3-2.
- No filtering flags (`--done`, `--pending`), no counts or summary line, no colour, no
  argparse. The epic entry says one line per item and nothing else.

### References

- `docs/planning-artifacts/epics.md`, `## Epic 2: Core commands`, entry
  **2-2-list-items**: "`list`: prints one line per item, `#<id> [ ] <text>` or
  `#<id> [x] <text>` when done, in id order; prints nothing and exits 0 when the list is
  empty."
- `docs/planning-artifacts/epics.md`, entry **2-1-add-item** — the item shape `list`
  renders: `{id, text, done}`.

## Dev Agent Record

### File List

- `todo.py` — added `list_items()`; added the `list` branch to `main(argv)`; added
  `python3 todo.py list` to the module docstring's usage example.
- `test_todo.py` — added `ListTests` (empty, two pending items in id order, a
  done item with out-of-order ids, and a byte-identical-file check).

### Completion Notes

- `list_items()` calls `load()` and returns `sorted(items, key=lambda item: item["id"])`;
  it does no writing, so AC 4 holds by construction (also covered by
  `test_list_does_not_modify_the_file`, which compares the file's raw bytes before/after).
- The `list` branch in `main` matches `argv[0] == "list"` with `len(argv) >= 1`,
  placed after the `add` branch and before the usage fallthrough, per the dev notes.
- All 7 tests pass (`python3 -m unittest`), including the 3 pre-existing `AddTests` and
  the usage-message test, confirming AC 5 (no regression).
- No new dependencies; stdlib only, matching the adapter's `check`.

---

The two lines below are the orchestrator's; Create writes them, Implement and Review leave
them as they are, and the run stats are appended after them.

Dev Model: sonnet   # follows the add() / main() pattern already in todo.py; a read-only command with a fixed output format
Proposed lane gate: none
