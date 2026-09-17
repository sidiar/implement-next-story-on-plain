import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TODO = os.path.join(HERE, "todo.py")


def run(*args: str, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, TODO, *args], capture_output=True, text=True, env=env)


class AddTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.file = os.path.join(self.dir, "todo.json")
        self.env = {**os.environ, "TODO_FILE": self.file}

    def test_add_creates_the_file_with_one_item(self):
        result = run("add", "buy milk", env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "added #1: buy milk")
        with open(self.file) as fh:
            self.assertEqual(json.load(fh), [{"id": 1, "text": "buy milk", "done": False}])

    def test_ids_increase(self):
        run("add", "one", env=self.env)
        result = run("add", "two", env=self.env)
        self.assertEqual(result.stdout.strip(), "added #2: two")

    def test_no_command_prints_usage_and_exits_2(self):
        result = run(env=self.env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("todo.py add", result.stderr)


class ListTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.file = os.path.join(self.dir, "todo.json")
        self.env = {**os.environ, "TODO_FILE": self.file}

    def test_empty_prints_nothing_and_exits_0(self):
        result = run("list", env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_two_added_items_print_two_pending_lines_in_id_order(self):
        run("add", "one", env=self.env)
        run("add", "two", env=self.env)
        result = run("list", env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["#1 [ ] one", "#2 [ ] two"])

    def test_done_item_and_out_of_order_ids_print_marked_and_sorted(self):
        with open(self.file, "w") as fh:
            json.dump(
                [
                    {"id": 2, "text": "two", "done": False},
                    {"id": 1, "text": "one", "done": True},
                ],
                fh,
            )
        result = run("list", env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["#1 [x] one", "#2 [ ] two"])

    def test_list_does_not_modify_the_file(self):
        run("add", "one", env=self.env)
        with open(self.file, "rb") as fh:
            before = fh.read()
        result = run("list", env=self.env)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(self.file, "rb") as fh:
            after = fh.read()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
