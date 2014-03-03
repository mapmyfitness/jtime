""" A set of utilities for the tests. """
import base64
import httpretty


def httpretty_connection_process():
    httpretty.register_uri(httpretty.GET, 'http://jira.atlassian.com/rest/api/2/serverInfo', body='{"baseUrl":"https://jira.atlassian.com","version":"6.2-OD-10-004-WN","versionNumbers":[6,2,0],"buildNumber":6253,"buildDate":"2014-02-24T00:00:00.000-0600","scmInfo":"0f638781a9eb90c00e546dda3da3aa1c24cb2738","serverTitle":"JIRA"}')
    httpretty.register_uri(httpretty.GET, 'http://jira.atlassian.com/rest/auth/1/session', body='{ "self": "https://jira.atlassian.com/rest/api/latest/user?username=testuser", "name": "testuser", "loginInfo": { "failedLoginCount": 16, "loginCount": 6698, "lastFailedLoginTime": "2014-02-26T00:00:53.464-0600", "previousLoginTime": "2014-03-02T23:29:11.812-0600" } }')

config = {
    'jira': {
        'url': 'http://jira.atlassian.com',
        'username': 'testuser',
        'password': base64.b64encode('pass'),
    }
}
