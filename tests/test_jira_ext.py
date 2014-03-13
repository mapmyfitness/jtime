""" Tests around the jira extension module. """
import datetime
import httpretty
import jira
import mock
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from jtime import jira_ext
from jtime import connection
import utils


class JtimeJiraExtTestCase(unittest.TestCase):
    @httpretty.activate
    def setUp(self):
        utils.httpretty_connection_process()
        self.jira = connection.jira_connection(utils.config)

        utils.httpretty_get_issue('jira_issue.json')
        self.issue = self.jira.get_issue('ARCHIVE-1')

    def tearDown(self):
        pass

    def test_JIRA(self):
        self.assertNotEquals(self.jira, None)

    def test_get_issue(self):
        self.assertNotEquals(self.issue, None)

    @httpretty.activate
    def test_get_issue_404(self):
        httpretty.register_uri(httpretty.GET,
                               'http://jira.atlassian.com/rest/api/2/issue/ARCHIVE-1',
                               status=404)

        self.jira.get_issue('ARCHIVE-1')

    @mock.patch('jira.client.JIRA.issue', side_effect=jira.exceptions.JIRAError)
    def test_get_issue_JIRAError(self, patch):
        self.jira.get_issue('BAD-ISSUE')

    def test_get_worklog(self):
        worklogs = self.jira.get_worklog(self.issue)
        self.assertIsInstance(worklogs, list)

    def test_get_elapsed_time(self):
        elapsed_time = self.jira.get_elapsed_time(self.issue)
        self.assertIsInstance(elapsed_time, basestring)

    def test_get_datetime_issue_in_progress(self):
        inprogress_time = self.jira.get_datetime_issue_in_progress(self.issue)
        self.assertIsInstance(inprogress_time, datetime.datetime)

    def test_get_cycle_time(self):
        cycletime = self.jira.get_cycle_time(self.issue)
        self.assertIsInstance(cycletime, float)

    @httpretty.activate
    def test_get_cycle_time_from_string(self):
        utils.httpretty_get_issue('jira_issue.json')
        cycletime = self.jira.get_cycle_time('ARCHIVE-1')
        self.assertIsInstance(cycletime, float)

    def test_get_cycle_time_from_start(self):
        cycletime = self.jira.get_cycle_time(self.jira.get_datetime_issue_in_progress(self.issue))
        self.assertIsInstance(cycletime, float)
