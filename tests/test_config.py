import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ytap import config


class ConfigTests(unittest.TestCase):
    def test_environment_key_takes_precedence(self):
        with tempfile.TemporaryDirectory() as directory:
            key_file = Path(directory) / "API_KEY"
            key_file.write_text("file-key", encoding="utf-8")
            with (
                patch.dict(os.environ, {"YTAP_API_KEY": " environment-key "}),
                patch.object(config, "API_KEY_FILE", key_file),
            ):
                self.assertEqual(config.load_api_key(), "environment-key")

    def test_key_loads_from_platform_config_file(self):
        with tempfile.TemporaryDirectory() as directory:
            key_file = Path(directory) / "API_KEY"
            key_file.write_text(" saved-key \n", encoding="utf-8")
            with (
                patch.dict(os.environ, {"YTAP_API_KEY": ""}),
                patch.object(config, "API_KEY_FILE", key_file),
            ):
                self.assertEqual(config.load_api_key(), "saved-key")

    def test_save_api_key_creates_directory_and_rejects_empty_value(self):
        with tempfile.TemporaryDirectory() as directory:
            key_file = Path(directory) / "config" / "API_KEY"
            with patch.object(config, "API_KEY_FILE", key_file):
                config.save_api_key(" api-key ")
                self.assertEqual(key_file.read_text(encoding="utf-8"), "api-key\n")
                with self.assertRaises(ValueError):
                    config.save_api_key(" ")


if __name__ == "__main__":
    unittest.main()
