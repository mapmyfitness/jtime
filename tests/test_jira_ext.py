""" Tests around the jira extension module. """
import httpretty
import unittest

from jtime import jira_ext
from jtime import connection
import utils


class JtimeJiraExtTestCase(unittest.TestCase):
    @httpretty.activate
    def setUp(self):
        utils.httpretty_connection_process()
        self.jira = connection.jira_connection(utils.config)

    def tearDown(self):
        pass

    def test_JIRA(self):
        self.assertNotEquals(self.jira, None)
