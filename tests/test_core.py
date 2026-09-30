import contextlib
import io
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

    def test_write_add_keeps_existing_value_and_grows_a_list(self):
        """write_add() must never drop a value, it appends to a list instead."""
        self.write_json({"city": "Paris"})

        core.write_add(self.path, "city", "Lyon")

        self.assertEqual(self.read_json(), {"city": ["Paris", "Lyon"]})

    def test_write_add_can_be_called_several_times_on_one_key(self):
        """Successive calls on the same key must accumulate in call order."""
        self.write_json({})

        core.write_add(self.path, "ville", "Nimes")
        core.write_add(self.path, "ville", "Lyon")
        core.write_add(self.path, "ville", "Paris")

        self.assertEqual(self.read_json(), {"ville": ["Nimes", "Lyon", "Paris"]})

    def test_write_add_ignores_duplicate_value(self):
        """write_add() must not add the same value twice."""
        self.write_json({})

        core.write_add(self.path, "ville", "Lyon")
        core.write_add(self.path, "ville", "Lyon")

        self.assertEqual(self.read_json(), {"ville": ["Lyon"]})

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

    def test_write_add_returns_path_true_and_content_when_key_is_added(self):
        """write_add() must return True as second element when the key is added."""
        self.write_json({})

        result = core.write_add(self.path, "city", "Lyon")

        self.assertEqual(result, (self.path, True, "Lyon"))

    def test_write_add_raises_oserror_if_directory_missing(self):
        """write_add() must let the error bubble up if the folder does not exist."""
        missing = os.path.join(self.tmpdir.name, "absent", "data.json")

        with self.assertRaises(OSError):
            core.write_add(missing, "city", "Lyon")

    def test_write_add_with_empty_key_does_nothing(self):
        """With an empty key, write_add() is a no-op and leaves the file untouched."""
        self.write_json({})

        result = core.write_add(self.path, "", "Lyon")

        self.assertEqual(result, (self.path, False, "Lyon"))
        self.assertEqual(self.read_json(), {})


class ReadChaineTests(TempFileTestCase):
    """Tests for easyjson.read_chaine()."""

    def test_read_chaine_returns_value(self):
        """read_chaine() must return the value stored under the key."""
        self.write_json({"city": "Nimes"})

        self.assertEqual(core.read_chaine(self.path, "city"), "Nimes")

    def test_read_chaine_keeps_value_type(self):
        """read_chaine() must not convert the stored value."""
        self.write_json({"number": 42, "flag": True, "nothing": None})

        self.assertEqual(core.read_chaine(self.path, "number"), 42)
        self.assertEqual(core.read_chaine(self.path, "flag"), True)
        self.assertIsNone(core.read_chaine(self.path, "nothing"))

    def test_read_chaine_reads_nested_value(self):
        """read_chaine() must return a nested object or list as is."""
        self.write_json({"account": {"user": "sionukk"}, "cities": ["Nimes"]})

        self.assertEqual(core.read_chaine(self.path, "account"), {"user": "sionukk"})
        self.assertEqual(core.read_chaine(self.path, "cities"), ["Nimes"])

    def test_read_chaine_prints_value(self):
        """read_chaine() must also print the value it reads."""
        self.write_json({"city": "Nimes"})
        buffer = io.StringIO()

        with contextlib.redirect_stdout(buffer):
            core.read_chaine(self.path, "city")

        self.assertEqual(buffer.getvalue(), "Nimes\n")

    def test_read_chaine_does_not_modify_file(self):
        """read_chaine() must leave the file byte for byte untouched."""
        self.write_json({"city": "Nimes"})

        with open(self.path, encoding="utf-8") as f:
            before = f.read()

        core.read_chaine(self.path, "city")

        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), before)

    def test_read_chaine_raises_keyerror_on_missing_key(self):
        """read_chaine() must raise KeyError when the key is absent."""
        self.write_json({"city": "Nimes"})

        with self.assertRaises(KeyError):
            core.read_chaine(self.path, "absent")

    def test_read_chaine_raises_oserror_if_directory_missing(self):
        """read_chaine() must let the error bubble up if the folder does not exist."""
        missing = os.path.join(self.tmpdir.name, "absent", "data.json")

        with self.assertRaises(OSError):
            core.read_chaine(missing, "city")

    def test_read_chaine_raises_valueerror_on_invalid_json(self):
        """read_chaine() must re-raise the decoding error on a malformed file."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("not json")

        with self.assertRaises(ValueError):
            core.read_chaine(self.path, "city")

    def test_read_chaine_raises_typeerror_on_json_list(self):
        """Known limitation: read_chaine() only works on a JSON object, not a list."""
        self.write_json(["Nimes"])

        with self.assertRaises(TypeError):
            core.read_chaine(self.path, "0")

class DeleteTests(TempFileTestCase):
    """Tests for easyjson.delete()."""

    def test_delete_removes_key(self):
        """delete() must remove the key from the object."""
        self.write_json({"city": "Nimes", "code": "30"})

        core.delete(self.path, "city")

        self.assertEqual(self.read_json(), {"code": "30"})

    def test_delete_keeps_other_keys(self):
        """delete() must preserve the keys that are not deleted."""
        self.write_json({"a": "1", "b": "2", "c": "3"})

        core.delete(self.path, "b")

        self.assertEqual(self.read_json(), {"a": "1", "c": "3"})

    def test_delete_returns_path_and_key(self):
        """delete() must return the (path, key) pair."""
        self.write_json({"city": "Nimes"})

        result = core.delete(self.path, "city")

        self.assertEqual(result, (self.path, "city"))

    def test_delete_empties_object_but_keeps_file(self):
        """delete() must leave an empty object, not delete the file."""
        self.write_json({"city": "Nimes"})

        core.delete(self.path, "city")

        self.assertTrue(os.path.exists(self.path))
        self.assertEqual(self.read_json(), {})

    def test_delete_does_not_escape_non_ascii(self):
        """delete() must keep accented characters without Unicode escaping."""
        self.write_json({"city": "Nîmes", "code": "30"})

        core.delete(self.path, "code")

        with open(self.path, encoding="utf-8") as f:
            self.assertIn("Nîmes", f.read())

    def test_delete_indents_output_with_four_spaces(self):
        """delete() must rewrite the file with an indent of 4."""
        self.write_json({"a": "1", "b": "2"})

        core.delete(self.path, "b")

        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), '{\n    "a": "1"\n}')

    def test_delete_raises_keyerror_on_missing_key(self):
        """delete() must raise KeyError when the key is absent."""
        self.write_json({"city": "Nimes"})

        with self.assertRaises(KeyError):
            core.delete(self.path, "absent")

    def test_delete_leaves_file_untouched_on_missing_key(self):
        """A KeyError must not overwrite the file."""
        self.write_json({"city": "Nimes"})

        with self.assertRaises(KeyError):
            core.delete(self.path, "absent")

        self.assertEqual(self.read_json(), {"city": "Nimes"})

    def test_delete_raises_oserror_if_directory_missing(self):
        """delete() must let the error bubble up if the folder does not exist."""
        missing = os.path.join(self.tmpdir.name, "absent", "data.json")

        with self.assertRaises(OSError):
            core.delete(missing, "city")

    def test_delete_raises_valueerror_on_invalid_json(self):
        """delete() must re-raise the decoding error on a malformed file."""
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("not json")

        with self.assertRaises(ValueError):
            core.delete(self.path, "city")

    def test_delete_raises_typeerror_on_json_list(self):
        """Known limitation: delete() only works on a JSON object, not a list."""
        self.write_json(["Nimes"])

        with self.assertRaises(TypeError):
            core.delete(self.path, "0")


class BaseJsonTests(TempFileTestCase):
    """Tests for easyjson.base_json()."""

    def setUp(self):
        """Also isolate the current directory, base_json writes data.json there."""
        super().setUp()
        previous = os.getcwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(self.tmpdir.name)

    def test_base_json_returns_the_account_skeleton(self):
        """base_json() must return the account dict that was written."""
        result = core.base_json()

        self.assertEqual(
            result,
            {"Account": {"user": "username", "password": "password"}},
        )

    def test_base_json_targets_data_json_in_current_directory(self):
        """base_json() must target data.json in the current directory."""
        cwd_data = os.path.join(self.tmpdir.name, "data.json")

        core.base_json()

        self.assertTrue(os.path.exists(cwd_data))
        self.assertEqual(
            self.read_json(cwd_data),
            {"Account": {"user": "username", "password": "password"}},
        )

    def test_base_json_writes_valid_json_with_indent_four(self):
        """base_json() must serialise the dict through json.dump, not f.write."""
        core.base_json()

        with open(os.path.join(self.tmpdir.name, "data.json"), encoding="utf-8") as f:
            content = f.read()

        self.assertIn("\n    ", content)
        self.assertIn('"Account"', content)


if __name__ == "__main__":
    unittest.main()
