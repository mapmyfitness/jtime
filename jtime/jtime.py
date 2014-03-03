#!/usr/bin/env python
import argh
import argparse
import dateutil.parser
from dateutil.tz import tzlocal
import datetime
import getpass
import sys

import configuration
import connection
import custom_exceptions
import git_ext
import utils


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
    configuration._save_config(jira_url, username, password)
    

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

            created = dateutil.parser.parse(worklog_hash['created']).astimezone(tzlocal())
            comment = worklog_hash.get('comment', '<no comment>')

            updated_string = created.strftime("%a %x %I:%M %p")
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
        marked = jira.workflow_transition(issue, 'In Progress')
        mark_time = datetime.datetime.now(dateutil.tz.tzlocal()).strftime("%I:%M %p")
        print 'Set mark at %s on %s by changing status to "In Progress"' % (mark_time, branch)

    if not marked:
        print "ERROR: Issue %s is has a status of %s and has no worklogs.  You must log some time or re-open the issue to proceed." % \
              (branch, issue.fields.status.name)


@argh.arg('-a', '--include-all', help='Include all issues that are not Closed')
@argh.arg('-i', help='Include issues that are In Progress (DEFAULT)')
@argh.arg('-o', help='Include issues that are Open')
@argh.arg('-d', help='Include issues that are Ready for Devint QA')
@argh.arg('-c', help='Include issues that are Ready for Code Review')
@argh.arg('-p', help='Include issues that are Ready for Production Deployment')
@argh.arg('-q', '--quiet', help='Quiet, does not includes issue title')
def me(include_all=False, i=False, o=False, d=False, c=False, p=False, quiet=False):
    """
    Prints a list of the users tickets and provides filtering options
    """
    issue_statuses = []

    default = not [arg for arg in sys.argv[2:] if arg not in ('-q', '--quiet')]

    if include_all or o:
        issue_statuses.append("Open")

    if include_all or i or default:
        issue_statuses.append("In Progress")

    if include_all or d or default:
        issue_statuses.append("Ready for Devint QA")

    if include_all or c or default:
        issue_statuses.append("Ready for Code Review")

    if include_all or p:
        issue_statuses.append("Ready for Production Deployment")

    jql = \
        """
            status in (
                %s
            )
            AND assignee in (currentUser())
            ORDER BY updated DESC
        """ % (','.join('"' + issue_status + '"' for issue_status in issue_statuses))

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

    parser = argparse.ArgumentParser()
    argh.add_commands(parser, [configure, log, mark, status, me, reopen])
    argh.dispatch(parser)
