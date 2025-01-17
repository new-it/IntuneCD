#!/usr/bin/env python3

"""This module tests backing up Managed Google Play."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_managedGPlay import savebackup


class TestBackupManagedGPlay(unittest.TestCase):
    """Test class for backup_managedGPlay."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Managed Google Play/awesome@gmail.com."
        self.expected_data = {
            "bindStatus": "boundAndValidated",
            "lastAppSyncDateTime": "2022-01-28T12:28:48.975089Z",
            "lastAppSyncStatus": "success",
            "ownerUserPrincipalName": "awesome@gmail.com",
        }
        self.managed_gplay = {
            "id": "0",
            "bindStatus": "boundAndValidated",
            "lastAppSyncDateTime": "2022-01-28T12:28:48.975089Z",
            "lastAppSyncStatus": "success",
            "ownerUserPrincipalName": "awesome@gmail.com",
        }

        self.patch_makeapirequest = patch(
            "src.IntuneCD.backup_managedGPlay.makeapirequest",
            return_value=self.managed_gplay,
        )
        self.makeapirequest = self.patch_makeapirequest.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "yaml", self.token, self.append_id)

        with open(self.saved_path + "yaml", "r") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Managed Google Play").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token, self.append_id)

        with open(self.saved_path + "json", "r") as f:
            saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Managed Google Play").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.return_value = None
        self.count = savebackup(self.directory.path, "json", self.token, self.append_id)
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token, True)

        self.assertTrue(Path(f"{self.directory.path}/Managed Google Play/awesome@gmail.com__0.json").exists())


if __name__ == "__main__":
    unittest.main()
