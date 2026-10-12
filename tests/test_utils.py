import json
import tempfile
import unittest
from pathlib import Path

from primitive_db.constants import VALID_TYPES
from primitive_db.utils import load_metadata, save_metadata


class MetadataStorageTests(unittest.TestCase):
    def test_load_missing_metadata_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_metadata(Path(directory) / "metadata.json"), {})

    def test_save_and_load_metadata_at_given_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metadata.json"
            metadata = {"users": {"ID": "int", "name": "str"}}

            save_metadata(path, metadata)

            self.assertEqual(load_metadata(path), metadata)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), metadata)

    def test_only_assignment_types_are_supported(self):
        self.assertEqual(set(VALID_TYPES), {"int", "str", "bool"})


if __name__ == "__main__":
    unittest.main()
