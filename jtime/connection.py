import base64
import requests

import configuration
import jira_ext


# Global to re-use opened JIRA connection
_jira_connection = None


def jira_connection(config):
    """
    Gets a JIRA API connection.  If a connection has already been created the existing connection
    will be returned.
    """
    global _jira_connection
    if _jira_connection:
        return _jira_connection
    else:
        jira_options = {'server': config.get('jira').get('url')}

        cookies = configuration._get_cookies_as_dict()
        jira_connection = jira_ext.JIRA(options=jira_options)
        session = jira_connection._session

        reused_session = False

        if cookies:
            requests.utils.add_dict_to_cookiejar(session.cookies, cookies)
            try:
                jira_connection.session()
                reused_session = True
            except Exception:
                pass

        if not reused_session:
            session.auth = (config['jira']['username'], base64.b64decode(config['jira']['password']))
            jira_connection.session()
            session.auth = None

            cookie_jar_hash = requests.utils.dict_from_cookiejar(session.cookies)
            for key, value in cookie_jar_hash.iteritems():
                configuration._save_cookie(key, value)

        _jira_connection = jira_connection
        return _jira_connection
