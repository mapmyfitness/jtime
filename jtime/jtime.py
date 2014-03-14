#!/usr/bin/env python
import argh
import argparse
import ConfigParser
import dateutil.parser
from dateutil.tz import tzlocal
import datetime
import logging
import getpass
import os
import sys

import configuration
import connection
import custom_exceptions
import git_ext
import utils


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR)


configured = None
jira = None
git = None


def init():
    global configured, jira, git
    # Initialize the connectors
    configured = configuration.load_config()
    jira = connection.jira_connection(configured)
    git = git_ext.GIT()


def configure():
    """
    Update config
    """
    jira_url = utils.get_input(raw_input, "Jira url")
    username = utils.get_input(raw_input, "username")
    password = utils.get_input(getpass.getpass, "password")
    error_reporting = True \
        if 'n' not in raw_input("Would you like to automatically report errors to help improve the software? [y]/N: ").lower() \
        else False
    configuration._save_config(jira_url, username, password, error_reporting)


def status():
    """
    Gets the worklog status for the current branch
    """
    branch = git.branch
    issue = jira.get_issue(branch)
    if not issue:
        return

    # Print the title
    title = issue.fields.summary
    print "(%s) %s" % (branch, title)

    # Print the status
    status = issue.fields.status.name
    assignee = issue.fields.assignee.name
    in_progress = jira.get_datetime_issue_in_progress(issue)

    if in_progress:
        in_progress_string = in_progress.strftime("%a %x %I:%M %p")
        print '  Status: %s as of %s' % (status, in_progress_string)
    else:
        print '  Status: %s' % status

    print '  Assignee: %s' % assignee

    # Print the worklogs

    # Get the timespent and return 0m if it does not exist
    time_spent = '0m'
    try:
        time_spent = issue.fields.timetracking.timeSpent
    except:
        pass

    worklogs = jira.get_worklog(issue)
    print "\nTime logged (%s):" % time_spent
    if worklogs:
        for worklog in worklogs:
            worklog_hash = worklog.raw

            author = worklog_hash['author']['name']

            time_spent = worklog_hash.get('timeSpent', '0m')

            created = dateutil.parser.parse(worklog_hash['started'])
            created_pattern = '%a %x         '  # Adding extra space for formatting
            if not created.hour == created.minute == created.second == 0:
                created = created.astimezone(tzlocal())
                created_pattern = '%a %x %I:%M %p'
            comment = worklog_hash.get('comment', '<no comment>')

            updated_string = created.strftime(created_pattern)
            print "  %s - %s (%s): %s" % (updated_string, author, time_spent, comment)
    else:
        print "  No worklogs"

    cycle_time = jira.get_cycle_time(issue)
    if cycle_time:
        print '\nCycle Time: %.1f days' % cycle_time

    # Print the time elapsed since the last mark
    elapsed_time = jira.get_elapsed_time(issue)
    if elapsed_time:
        print '\n\033[0;32m%s elapsed\033[00m (use "jtime log ." to log elapsed time or "jtime log <duration> (ex. 30m, 1h etc.)" to log a specific amount of time)' % (elapsed_time)
    else:
        print '\n\033[0;32m0m elapsed\033[00m'


@argh.arg('duration', help='Use . to log all time elapsed since the last mark or provide a specific amount of time to log (ex. 30m, 1h)')
@argh.arg('-m', '--message', help='A message to add to this work log')
@argh.arg('-c', '--commit', dest='use_last_commit_message', help='Use last commit message for the work log message')
def log(duration, message=None, use_last_commit_message=False):
    """
    Log time against the current active issue
    """
    branch = git.branch
    issue = jira.get_issue(branch)
    # Create the comment
    comment = "Working on issue %s" % branch
    if message:
        comment = message
    elif use_last_commit_message:
        comment = git.get_last_commit_message()

    if issue:

        # If the duration is provided use it, otherwise use the elapsed time since the last mark
        duration = jira.get_elapsed_time(issue) if duration == '.' else duration

        if duration:
            # Add the worklog
            jira.add_worklog(issue, timeSpent=duration, adjustEstimate=None, newEstimate=None, reduceBy=None,
                             comment=comment)

            print "Logged %s against issue %s (%s)" % (duration, branch, comment)
        else:
            print "No time logged, less than 0m elapsed."


def mark():
    """
    Mark the start time for active work on an issue
    """
    branch = git.branch
    issue = jira.get_issue(branch)
    worklogs = jira.get_worklog(issue)

    marked = False
    if worklogs:
        # If we have worklogs, change the updated time of the last log to the mark
        marked = jira.touch_last_worklog(issue)
        mark_time = datetime.datetime.now(dateutil.tz.tzlocal()).strftime("%I:%M %p")
        print "Set mark at %s on %s by touching last work log" % (mark_time, branch)
    else:
        # If we don't have worklogs, mark the issue as in progress if that is an available transition
        jira.workflow_transition(issue, 'Open')
        marked = jira.workflow_transition(issue, 'In Progress')
        mark_time = datetime.datetime.now(dateutil.tz.tzlocal()).strftime("%I:%M %p")
        print 'Set mark at %s on %s by changing status to "In Progress"' % (mark_time, branch)

    if not marked:
        print "ERROR: Issue %s is has a status of %s and has no worklogs.  You must log some time or re-open the issue to proceed." % \
              (branch, issue.fields.status.name)


@argh.arg('-a', '--show-all', help='Include all issues that are not Closed')
@argh.arg('-i', '--show-inprogress', help='Show only issues that are In Progress')
@argh.arg('-o', '--show-open', help='Show only issues that are Open')
@argh.arg('-q', '--quiet', help='Quiet, does not includes issue title')
def me(show_all=False, show_inprogress=False, show_open=False, quiet=False):
    """
    Prints a list of the users tickets and provides filtering options
    """
    default = not [arg for arg in sys.argv[2:] if arg not in ('-q', '--quiet')]

    status_exclusions = ['Backlog', 'Open', 'Closed']
    status_inclusions = []

    if show_inprogress or default:
        status_inclusions.append('In Progress')
    if show_open:
        status_exclusions = []
        status_inclusions.append('Open')
    elif show_all:
        status_exclusions = ['Closed']

    jql = \
        """
            assignee=currentUser()
            AND resolved is EMPTY
        """
    # We are switching between showing everything and only showing in progress items
    if not show_all and not show_open:
        jql += ' AND status was "In Progress" '

    inclusion_str = None
    if len(status_inclusions):
        inclusion_str = "status in ({0})".format((','.join('"' + issue_status + '"' for issue_status in status_inclusions)))
    exclusion_str = None
    if len(status_exclusions):
        exclusion_str = "status not in ({0})".format((','.join('"' + issue_status + '"' for issue_status in status_exclusions)))
    jql += " AND ( {0} {1} {2} ) ".format(inclusion_str if inclusion_str else "",
                                          " OR " if inclusion_str and exclusion_str else "",
                                          exclusion_str if exclusion_str else "")

    jql += " ORDER BY updated DESC "

    results = jira.search_issues(jql)

    for result in results:

        issue = result.key
        updated = dateutil.parser.parse(result.fields.updated).strftime("%a %x %I:%M %p")
        status = result.fields.status.name

        cycletime = jira.get_cycle_time(result.key)
        cycletime_str = " -- %.1f days" % cycletime if cycletime else ""
        print "%s (%s) %s%s" % (issue, updated, status, cycletime_str)

        # If verbose, add a line for the issue title
        if not quiet:
            title = result.fields.summary
            title = (title[:75] + '..') if len(title) > 75 else title
            print "  %s\n" % title

    # Print result count and usage hint for help
    print "\033[0;32m%s issue(s) found\033[00m (use 'jtime me -h' for filter options)" % len(results)

    print "One week avg cycle time: %.1f days" % jira.get_week_avg_cycletime()


def reopen():
    """
    Reopen an issue
    """
    issue = jira.get_issue(git.branch)
    jira.workflow_transition(issue, 'Open')


def main():
    """
    Set up the context and connectors
    """
    try:
        init()
    except custom_exceptions.NotConfigured:
        configure()
        init()
    # Adding this in case users are trying to run without adding a jira url.
    # I would like to take this out in a release or two.
    # TODO: REMOVE
    except (AttributeError, ConfigParser.NoOptionError):
        logging.error('It appears that your configuration is invalid, please reconfigure the app and try again.')
        configure()
        init()

    parser = argparse.ArgumentParser()
    argh.add_commands(parser, [configure, log, mark, status, me, reopen])

    # Putting the error logging after the app is initialized because
    # we want to adhere to the user's preferences
    try:
        argh.dispatch(parser)
    # We don't want to report keyboard interrupts to rollbar
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        if configured.get('jira').get('error_reporting', True):
            # Configure rollbar so that we report errors
            import rollbar
            from . import __version__ as version
            root_path = os.path.dirname(os.path.realpath(__file__))
            rollbar.init('7541b8e188044831b6728fa8475eab9f', 'v%s' % version, root=root_path)
            logging.error('Sorry. It appears that there was an error when handling your command. '
                          'This error has been reported to our error tracking system. To disable '
                          'this reporting, please re-configure the app: `jtime config`.')
            extra_data = {
                # grab the command that we're running
                'cmd': sys.argv[1],
                # we really don't want to see jtime in the args
                'args': sys.argv[2:],
                # lets grab anything useful, python version?
                'python': str(sys.version),
            }
            # We really shouldn't thit this line of code when running tests, so let's not cover it.
            rollbar.report_exc_info(extra_data=extra_data)  # pragma: no cover
        else:
            logging.error('It appears that there was an error when handling your command.')
            raise
