""" A set of utilities for the tests. """
import base64
import httpretty
import mock
import os


def httpretty_get_issue(fname):
    json_file_path = os.path.join(os.path.dirname(__file__), fname)

    with open(json_file_path) as json_file:
        jira_issue_json_str = json_file.read()

    httpretty.register_uri(httpretty.GET,
                           'http://jira.atlassian.com/rest/api/2/issue/ARCHIVE-1',
                           body=jira_issue_json_str)


def httpretty_connection_process():
    httpretty.register_uri(httpretty.GET, 'http://jira.atlassian.com')

    httpretty.register_uri(httpretty.GET, 'http://jira.atlassian.com/rest/api/2/serverInfo', body='{"baseUrl":"https://jira.atlassian.com","version":"6.2-OD-10-004-WN","versionNumbers":[6,2,0],"buildNumber":6253,"buildDate":"2014-02-24T00:00:00.000-0600","scmInfo":"0f638781a9eb90c00e546dda3da3aa1c24cb2738","serverTitle":"JIRA"}')

    httpretty.register_uri(httpretty.GET, 'http://jira.atlassian.com/rest/auth/1/session', body='{ "self": "https://jira.atlassian.com/rest/api/latest/user?username=testuser", "name": "testuser", "loginInfo": { "failedLoginCount": 16, "loginCount": 6698, "lastFailedLoginTime": "2014-02-26T00:00:53.464-0600", "previousLoginTime": "2014-03-02T23:29:11.812-0600" } }')


config = {
    'jira': {
        'url': 'http://jira.atlassian.com',
        'username': 'testuser',
        'password': base64.b64encode('pass'),
    }
}



config_filepath = os.path.abspath('.jtime.ini')
config_path_patcher = mock.patch('jtime.configuration._config',
                                 config_filepath)
