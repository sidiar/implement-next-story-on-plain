# Epics — todo CLI

A todo list kept in a JSON file, driven from the command line, standard library only.
`todo.py` holds the commands; `test_todo.py` drives it as a subprocess and asserts on
stdout, exit code and the JSON file.

## Epic 1: Scaffold

- **1-1-cli-scaffold** — `todo.py` with a `main(argv)` dispatcher, `load()` / `save()`
  around a JSON file named by `TODO_FILE`, usage on stderr with exit 2 for an unknown
  command, and a test file that runs the CLI as a subprocess.

## Epic 2: Core commands

- **2-1-add-item** — `add <text>`: appends `{id, text, done}` with the next free id,
  prints `added #<id>: <text>`.
- **2-2-list-items** — `list`: prints one line per item, `#<id> [ ] <text>` or
  `#<id> [x] <text>` when done, in id order; prints nothing and exits 0 when the list is
  empty.
- **2-3-done-item** — `done <id>`: marks the item done and prints `done #<id>: <text>`;
  an unknown id prints `no item #<id>` on stderr and exits 1.
- **2-4-remove-item** — `remove <id>`: deletes the item and prints
  `removed #<id>: <text>`; an unknown id behaves as in 2-3.

## Epic 3: Quality of life

- **3-1-file-flag** — `--file PATH` before the command overrides `TODO_FILE` for that
  invocation.
- **3-2-clear-done** — `clear`: removes every done item and prints how many were removed.
