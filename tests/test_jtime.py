"""Tests for jtime."""
import httpretty
import unittest
#from nose.tools import ok_, eq_, raises
#from nose import SkipTest

from jtime import jtime
import utils

    
class JtimeTestCase(unittest.TestCase):
    @httpretty.activate
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_jtime_init(self):
        utils.httpretty_connection_process()
        jtime.init()

        self.assertNotEquals(jtime.configured, None)
        self.assertNotEquals(jtime.jira, None)
        self.assertNotEquals(jtime.git, None)
