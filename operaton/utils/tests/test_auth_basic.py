from unittest import TestCase

from operaton.utils.auth_basic import AuthBasic, obfuscate_secrets

import copy


class TestAuthBasic(TestCase):
    def test_auth_basic(self):
        auth_basic = AuthBasic(**{
            "username": "test",
            "password": "test",
        })
        self.assertEqual(auth_basic.token, 'Basic dGVzdDp0ZXN0')

    def test_obfuscate_password(self):
        default_config = {
            "auth_basic": {"username": "demo", "password": "demo"},
            "maxTasks": 1,
            "lockDuration": 10000,
            "asyncResponseTimeout": 0,
            "isDebug": True,
        }
        obfuscate_config = {
            "auth_basic": {"username": "demo", "password": "***"},
            "maxTasks": 1,
            "lockDuration": 10000,
            "asyncResponseTimeout": 0,
            "isDebug": True,
        }
        self.assertEqual(obfuscate_secrets(default_config), obfuscate_config)

    def test_obfuscate_secrets_does_not_mutate_original_config(self):
        config = {"auth_basic": {"username": "demo", "password": "demo"}}
        original = copy.deepcopy(config)
        obfuscate_secrets(config)
        self.assertEqual(original, config)

    def test_obfuscate_secrets_redacts_nested_dict(self):
        config = {"auth_oauth": {"client_id": "abc", "client_secret": "shh"}}
        expected = {"auth_oauth": {"client_id": "abc", "client_secret": "***"}}
        self.assertEqual(expected, obfuscate_secrets(config))

    def test_obfuscate_secrets_redacts_dicts_inside_list(self):
        config = {"accounts": [{"username": "a", "password": "pw1"},
                               {"username": "b", "password": "pw2"}]}
        expected = {"accounts": [{"username": "a", "password": "***"},
                                 {"username": "b", "password": "***"}]}
        self.assertEqual(expected, obfuscate_secrets(config))

    def test_obfuscate_secrets_is_case_insensitive(self):
        config = {"auth_basic": {"username": "demo", "Password": "demo"}}
        expected = {"auth_basic": {"username": "demo", "Password": "***"}}
        self.assertEqual(expected, obfuscate_secrets(config))

    def test_obfuscate_secrets_leaves_config_unchanged_without_match(self):
        config = {"maxTasks": 1, "isDebug": True}
        self.assertEqual(config, obfuscate_secrets(config))

    def test_obfuscate_secrets_with_custom_sensitive_keys(self):
        config = {"auth_basic": {"username": "demo", "password": "demo"},
                   "my_field": "secret_value"}
        expected = {"auth_basic": {"username": "demo", "password": "demo"},
                    "my_field": "***"}
        self.assertEqual(expected, obfuscate_secrets(config, sensitive_keys={"my_field"}))

    def test_obfuscate_secrets_with_extra_key_extends_default(self):
        config = {"auth_basic": {"username": "demo", "password": "demo"},
                   "db_dsn": "user:pw@host"}
        expected = {"auth_basic": {"username": "demo", "password": "***"},
                    "db_dsn": "***"}
        self.assertEqual(expected, obfuscate_secrets(config, extra_key="db_dsn"))