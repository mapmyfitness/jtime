import base64
import ConfigParser
import os
import sys
import urllib
import urlparse

import custom_exceptions


_config = os.path.expanduser('~/.jtime.ini')


def load_config():
    """
    Validate the config
    """
    configuration = MyParser()
    configuration.read(_config)

    d = configuration.as_dict()

    if 'jira' not in d:
        raise custom_exceptions.NotConfigured

    return d


def _save_config(jira_url, username, password):
    """
    Saves the username and password to the config
    """
    # Delete what is there before we re-write. New user means new everything
    os.path.exists(_config) and os.remove(_config)

    config = ConfigParser.SafeConfigParser()
    config.read(_config)
    if not config.has_section('jira'):
        config.add_section('jira')

    if 'http' not in jira_url:
        jira_url = 'http://' + jira_url

    try:
        resp = urllib.urlopen(jira_url)
        url = urlparse.urlparse(resp.url)
        jira_url = url.scheme + "://" + url.netloc
    except IOError, e:
        print "It doesn't appear that {0} is responding to a request.\
               Please make sure that you typed the hostname, \
               i.e. jira.atlassian.com.\n{1}".format(jira_url, e)
        sys.exit(1)

    config.set('jira', 'url', jira_url)
    config.set('jira', 'username', username)
    config.set('jira', 'password', base64.b64encode(password))

    with open(_config, 'w') as ini:
        os.chmod(_config, 0600)
        config.write(ini)


def _get_cookies_as_dict():
    """
    Get cookies as a dict
    """
    config = ConfigParser.SafeConfigParser()
    config.read(_config)

    if config.has_section('cookies'):
        cookie_dict = {}
        for option in config.options('cookies'):
            option_key = option.upper() if option == 'jsessionid' else option
            cookie_dict[option_key] = config.get('cookies', option)

        return cookie_dict


def _save_cookie(cookie_name, cookie_value):
    """
    Save cookie
    """
    config = ConfigParser.SafeConfigParser()
    config.read(_config)
    if not config.has_section('cookies'):
        config.add_section('cookies')

    config.set('cookies', cookie_name, cookie_value)

    with open(_config, 'w') as ini:
        config.write(ini)


class MyParser(ConfigParser.SafeConfigParser):
    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d
