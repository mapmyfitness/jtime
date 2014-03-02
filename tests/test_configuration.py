""" Tests for jtime configuration module. """
import base64
import mock
import os
import unittest

from jtime import configuration
from jtime import custom_exceptions
from jtime import jtime


class JtimeConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        self.config_file_path = os.path.abspath('.jtime.ini')
        self._config_patch = mock.patch('jtime.configuration._config',
                                        self.config_file_path)
        self._config_patch.start()

    def tearDown(self):
        self._config_patch.stop()

        # Delete the configuration file if we've created it
        if os.path.exists(self.config_file_path):
            os.remove(self.config_file_path)

    def test__save_config(self):
        configuration._save_config('', '')

        assert os.path.exists(self.config_file_path)

    def test_load_config(self):
        username = 'test_user'
        password = 'test_pass'
        configuration._save_config(username, password)
        config_dict = configuration.load_config()

        assert username == config_dict.get('jira').get('username')
        assert base64.b64encode(password) == config_dict.get('jira').get('password')

    def test_load_config__NotConfigured(self):
        with self.assertRaises(custom_exceptions.NotConfigured):
            configuration.load_config()

    @mock.patch('jtime.utils.get_input', side_effect=['user', 'pass'])
    def test_jtime_configure(self, input):
        jtime.configure()
