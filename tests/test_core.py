import json
import os
import tempfile
import unittest

import easyjson
from easyjson import core


class TempFileTestCase(unittest.TestCase):
    """Base class providing an isolated temp folder and JSON file."""

    def setUp(self):
        """Create a temp folder and a file path isolated for each test."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.path = os.path.join(self.tmpdir.name, "data.json")

    def read_json(self, path=None):
        """Read and deserialize the JSON file at the given path."""
        with open(path or self.path, encoding="utf-8") as f:
            return json.load(f)

    def write_json(self, data, path=None):
        """Write `data` to a JSON file inside the temp folder."""
        with open(path or self.path, "w", encoding="utf-8") as f:
            json.dump(data, f)


class WriteTests(TempFileTestCase):
    """Tests for easyjson.write()."""

    def test_write_creates_file_with_content(self):
        """write() must create the file and write the received content."""
        easyjson.write(self.path, '{"a": 1}')

        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), '{"a": 1}')

    def test_write_overwrites_existing_file(self):
        """write() must overwrite the content of an existing file."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("old content")

        easyjson.write(self.path, "new")

        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "new")

    def test_write_returns_path_and_content(self):
        """write() must return the (path, content) pair."""
        result = easyjson.write(self.path, '{"b": 2}')

        self.assertEqual(result, (self.path, '{"b": 2}'))

    def test_write_raises_oserror_if_directory_missing(self):
        """write() must let the error bubble up if the folder does not exist."""
        missing = os.path.join(self.tmpdir.name, "absent", "data.json")

        with self.assertRaises(OSError):
            easyjson.write(missing, "content")

    def test_write_accepts_non_ascii_content(self):
        """write() must preserve non-ASCII characters thanks to UTF-8."""
        easyjson.write(self.path, '{"city": "Nimes"}')

        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["city"], "Nimes")


class AppendTests(TempFileTestCase):
    """Tests for easyjson.append()."""

    def test_append_adds_item_to_empty_list(self):
        """append() must add the content to an empty JSON list."""
        self.write_json([])

        core.append(self.path, "first")

        self.assertEqual(self.read_json(), ["first"])

    def test_append_keeps_existing_items(self):
        """append() must keep the items already present in the list."""
        self.write_json(["a", "b"])

        core.append(self.path, "c")

        self.assertEqual(self.read_json(), ["a", "b", "c"])

    def test_append_can_be_called_several_times(self):
        """Successive calls must grow the list in call order."""
        self.write_json([])

        core.append(self.path, 1)
        core.append(self.path, 2)
        core.append(self.path, 3)

        self.assertEqual(self.read_json(), [1, 2, 3])

    def test_append_accepts_any_json_value(self):
        """append() must keep the type of the appended value untouched."""
        self.write_json([])

        core.append(self.path, {"a": 1})
        core.append(self.path, None)
        core.append(self.path, True)
        core.append(self.path, 4.5)

        self.assertEqual(
            self.read_json(), [{"a": 1}, None, True, 4.5]
        )

    def test_append_indents_output_with_four_spaces(self):
        """append() must rewrite the file with an indent of 4."""
        self.write_json(["a"])

        core.append(self.path, "b")

        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), '[\n    "a",\n    "b"\n]')

    def test_append_returns_path_and_content(self):
        """append() must return the (path, content) pair."""
        self.write_json([])

        result = core.append(self.path, "Lyon")

        self.assertEqual(result, (self.path, "Lyon"))

    def test_append_raises_oserror_if_directory_missing(self):
        """append() must let the error bubble up if the folder does not exist."""
        missing = os.path.join(self.tmpdir.name, "absent", "data.json")

        with self.assertRaises(OSError):
            core.append(missing, "Lyon")

    def test_append_raises_valueerror_on_invalid_json(self):
        """append() must re-raise the JSON decoding error on a malformed file."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("not json")

        with self.assertRaises(ValueError):
            core.append(self.path, "Lyon")

    def test_append_leaves_file_untouched_on_invalid_json(self):
        """A malformed file must not be overwritten by a failed append()."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("not json")

        with self.assertRaises(ValueError):
            core.append(self.path, "Lyon")

        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "not json")

    def test_append_raises_valueerror_on_empty_file(self):
        """append() must fail on an existing but empty file."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("")

        with self.assertRaises(ValueError):
            core.append(self.path, "Lyon")

    def test_append_raises_attributeerror_on_json_object(self):
        """Known limitation: append() only works on a JSON list, not an object."""
        self.write_json({"a": 1})

        with self.assertRaises(AttributeError):
            core.append(self.path, "Lyon")


class WriteAddTests(TempFileTestCase):
    """Tests for easyjson.write_add()."""

    def test_write_add_creates_key(self):
        """write_add() must add the key with the given value."""
        self.write_json({})

        core.write_add(self.path, "city", "Nimes")

        self.assertEqual(self.read_json(), {"city": "Nimes"})

    def test_write_add_replaces_existing_key(self):
        """write_add() must replace the value of an already present key."""
        self.write_json({"city": "Paris"})

        core.write_add(self.path, "city", "Lyon")

        self.assertEqual(self.read_json(), {"city": "Lyon"})

    def test_write_add_converts_content_to_string(self):
        """write_add() must store the value as a string."""
        self.write_json({})

        core.write_add(self.path, "number", 42)

        self.assertEqual(self.read_json(), {"number": "42"})

    def test_write_add_does_not_escape_non_ascii(self):
        """write_add() must keep accented characters without Unicode escaping."""
        self.write_json({})

        core.write_add(self.path, "city", "Nîmes")

        with open(self.path, encoding="utf-8") as f:
            self.assertIn("Nîmes", f.read())

    def test_write_add_keeps_existing_keys(self):
        """write_add() must preserve the other keys of the object."""
        self.write_json({"a": "1"})

        core.write_add(self.path, "b", "2")

        self.assertEqual(self.read_json(), {"a": "1", "b": "2"})

    def test_write_add_returns_path_key_and_content(self):
        """write_add() must return the (path, key, content) tuple."""
        self.write_json({})

        result = core.write_add(self.path, "city", "Lyon")

        self.assertEqual(result, (self.path, "city", "Lyon"))

    def test_write_add_raises_oserror_if_directory_missing(self):
        """write_add() must let the error bubble up if the folder does not exist."""
        missing = os.path.join(self.tmpdir.name, "absent", "data.json")

        with self.assertRaises(OSError):
            core.write_add(missing, "city", "Lyon")

    def test_write_add_with_empty_key_does_nothing(self):
        """With an empty key, write_add() is a no-op and leaves the file untouched."""
        self.write_json({})

        result = core.write_add(self.path, "", "Lyon")

        self.assertEqual(result, (self.path, "", "Lyon"))
        self.assertEqual(self.read_json(), {})


class BaseJsonTests(TempFileTestCase):
    """Tests for easyjson.base_json()."""

    def setUp(self):
        """Also isolate the current directory, base_json writes data.json there."""
        super().setUp()
        previous = os.getcwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(self.tmpdir.name)

    def test_base_json_raises_typeerror_writing_dict(self):
        """Known bug: a dict is passed to f.write, which expects a string."""
        with self.assertRaises(TypeError):
            core.base_json()

    def test_base_json_targets_data_json_in_current_directory(self):
        """base_json() must target data.json in the current directory."""
        cwd_data = os.path.join(self.tmpdir.name, "data.json")

        with self.assertRaises(TypeError):
            core.base_json()

        self.assertTrue(os.path.exists(cwd_data))
        with open(cwd_data, encoding="utf-8") as f:
            self.assertEqual(f.read(), "")


if __name__ == "__main__":
    unittest.main()
