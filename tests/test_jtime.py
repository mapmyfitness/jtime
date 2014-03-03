"""Tests for jtime."""
import httpretty
import os
import unittest
#from nose.tools import ok_, eq_, raises
#from nose import SkipTest

from jtime import jtime
from jtime import configuration
import utils

    
class JtimeTestCase(unittest.TestCase):
    def setUp(self):
        self.config_file_path = utils.config_filepath
        self._config_patch = utils.config_path_patcher
        self._config_patch.start()
        
    def tearDown(self):
        self._config_patch.stop()

        # Delete the configuration file if we've created it
        if os.path.exists(self.config_file_path):
            os.remove(self.config_file_path)
        
    @httpretty.activate
    def test_jtime_init(self):
        utils.httpretty_connection_process()
        configuration._save_config('jira.atlassian.com', '', '')
        jtime.init()

        self.assertNotEquals(jtime.configured, None)
        self.assertNotEquals(jtime.jira, None)
        self.assertNotEquals(jtime.git, None)
