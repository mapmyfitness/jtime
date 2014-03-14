"""Tests for jtime."""
import httpretty
import mock
import os
import unittest
#from nose.tools import ok_, eq_, raises
#from nose import SkipTest

from jtime import jtime
from jtime import configuration
import utils

    
class JtimeTestCase(unittest.TestCase):
    @httpretty.activate
    def setUp(self):
        self.config_file_path = utils.config_filepath
        self._config_patch = utils.config_path_patcher
        self._config_patch.start()

        utils.httpretty_connection_process()
        configuration._save_config('jira.atlassian.com', '', '', True)
        jtime.init()

        utils.httpretty_get_issue('jira_issue.json')
        self.issue = jtime.jira.get_issue('ARCHIVE-1')
        
    def tearDown(self):
        self._config_patch.stop()

        # Delete the configuration file if we've created it
        if os.path.exists(self.config_file_path):
            os.remove(self.config_file_path)
        
    def test_jtime_init(self):
        self.assertNotEquals(jtime.configured, None)
        self.assertNotEquals(jtime.jira, None)
        self.assertNotEquals(jtime.git, None)

    def test_jtime_log(self):
        with mock.patch('jtime.git_ext.GIT') as mock_git:
            type(mock_git).branch = mock.PropertyMock(return_value='ARCHIVE-1')
            jtime.status()
