#!/usr/bin/env python3

"""This module tests backing up Notification Templates."""

import json
import yaml
import unittest

from pathlib import Path
from unittest.mock import patch
from testfixtures import TempDirectory
from src.IntuneCD.backup_notificationTemplate import savebackup


class TestBackupNotificationTemplate(unittest.TestCase):
    """Test class for backup_notificationTemplate."""

    def setUp(self):
        self.directory = TempDirectory()
        self.directory.create()
        self.token = "token"
        self.append_id = False
        self.saved_path = f"{self.directory.path}/Compliance Policies/Message Templates/test."
        self.expected_data = {
            "brandingOptions": "includeCompanyLogo,includeCompanyName,includeContactInformation",
            "defaultLocale": "da-dk",
            "displayName": "test",
            "localizedNotificationMessages": [
                {
                    "isDefault": True,
                    "locale": "da-dk",
                    "messageTemplate": "Danish locale demo new",
                    "subject": "test",
                }
            ],
            "roleScopeTagIds": ["0"],
        }
        self.message_template = {
            "value": [
                {
                    "id": "0",
                    "displayName": "test",
                    "defaultLocale": "da-dk",
                    "brandingOptions": "includeCompanyLogo,includeCompanyName,includeContactInformation",
                    "roleScopeTagIds": ["0"],
                    "localizedNotificationMessages": [
                        {
                            "id": "0",
                            "lastModifiedDateTime": "2022-07-16T00:01:14.8680508Z",
                            "locale": "da-dk",
                            "subject": "test",
                            "messageTemplate": "Danish locale demo new",
                            "isDefault": True,
                        }
                    ],
                }
            ]
        }

        self.localized_messages = {
            "id": "0",
            "displayName": "test",
            "defaultLocale": "da-dk",
            "brandingOptions": "includeCompanyLogo,includeCompanyName,includeContactInformation",
            "roleScopeTagIds": ["0"],
            "localizedNotificationMessages": [
                {
                    "id": "0",
                    "lastModifiedDateTime": "2022-07-16T00:03:39.8347438Z",
                    "locale": "da-dk",
                    "subject": "test",
                    "messageTemplate": "Danish locale demo new",
                    "isDefault": True,
                }
            ],
        }

        self.patch_makeapirequest = patch(
            "src.IntuneCD.backup_notificationTemplate.makeapirequest",
            side_effect=[self.message_template, self.localized_messages],
        )
        self.makeapirequest = self.patch_makeapirequest.start()

    def tearDown(self):
        self.directory.cleanup()
        self.makeapirequest.stop()

    def test_backup_yml(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "yaml", self.token, "", self.append_id)

        with open(self.saved_path + "yaml", "r") as f:
            data = json.dumps(yaml.safe_load(f))
            saved_data = json.loads(data)

        self.assertTrue(Path(f"{self.directory.path}/Compliance Policies/Message Templates").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_json(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token, "", self.append_id)

        with open(self.saved_path + "json", "r") as f:
            saved_data = json.load(f)

        self.assertTrue(Path(f"{self.directory.path}/Compliance Policies/Message Templates").exists())
        self.assertEqual(self.expected_data, saved_data)
        self.assertEqual(1, self.count["config_count"])

    def test_backup_with_no_return_data(self):
        """The count should be 0 if no data is returned."""

        self.makeapirequest.side_effect = [{"value": []}]
        self.count = savebackup(self.directory.path, "json", self.token, "", self.append_id)
        self.assertEqual(0, self.count["config_count"])

    def test_backup_with_prefix(self):
        """The count should be 0 if no data is returned."""

        self.count = savebackup(self.directory.path, "json", self.token, "test1", self.append_id)
        self.assertEqual(0, self.count["config_count"])

    def test_backup_append_id(self):
        """The folder should be created, the file should have the expected contents, and the count should be 1."""

        self.count = savebackup(self.directory.path, "json", self.token, "", True)

        self.assertTrue(Path(f"{self.directory.path}/Compliance Policies/Message Templates/test__0.json").exists())


if __name__ == "__main__":
    unittest.main()
