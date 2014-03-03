""" Tests for jtime connection module. """
import httpretty
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from jtime import connection
import utils


class JtimeConnectionTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @httpretty.activate
    def test_connect(self):
        utils.httpretty_connection_process()
        connection.jira_connection(utils.config)
