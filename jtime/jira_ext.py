import jira
import datetime
import dateutil.parser

import utils


class JIRA(jira.client.JIRA):
    """
    Overloading the jira-python JIRA class with custom methods
    that we are using for our application
    """
    def __init__(self, **kwargs):
        super(JIRA, self).__init__(**kwargs)

    def get_issue(self, branch):
        """
        Gets the JIRA issue associated with the branch name.

        Returns None if no issue with this branch name.
        """
        if branch:
            try:
                issue = self.issue(branch, expand='changelog')
                return issue
            except jira.exceptions.JIRAError as ex:
                if ex.status_code == 404:
                    print "No JIRA issue found for branch %s" % branch
                else:
                    print str(ex)

    def get_worklog(self, issue):
        """
        Gets the worklogs for a JIRA issue
        """
        return issue.fields.worklog.worklogs

    def get_elapsed_time(self, issue):
        """
        Gets the elapsed time since the last mark (either the updated time of the last log or the time that the issue was
        marked in progress)
        """
        last_mark = None

        # Get the last mark from the work logs
        worklogs = self.get_worklog(issue)
        if worklogs:
            last_worklog = worklogs[-1]
            last_mark = dateutil.parser.parse(last_worklog.raw['updated'])

        # If no worklogs, get the time since the issue was marked In Progress
        if not last_mark:
            last_mark = self.get_datetime_issue_in_progress(issue)

        if last_mark:
            now = datetime.datetime.now(dateutil.tz.tzlocal())
            delta = now - last_mark
            minutes = int(utils.timedelta_total_seconds(delta) / 60)
            if minutes > 0:
                return str(minutes) + 'm'
            else:
                return None

    def workflow_transition(self, issue, status_name):
        """
        Change the status of a JIRA issue to a named status.  Will only be updated
        if this transition is available from the current status.
        """
        transitions = self.transitions(issue)
        for transition in transitions:
            if transition['to']['name'] == status_name:
                transition_id = transition['id']
                self.transition_issue(issue, transition_id)
                print "Changed status of issue %s to %s" % (issue.key, status_name)
                return True

        print "Unable to change status of issue %s to %s" % (issue.key, status_name)

    def get_datetime_issue_in_progress(self, issue):
        """
        If the issue is in progress, gets that most recent time that the issue became 'In Progress'
        """
        histories = issue.changelog.histories
        for history in reversed(histories):
            history_items = history.items
            for item in history_items:
                if item.field == 'status' and item.toString == "In Progress":
                    return dateutil.parser.parse(history.created)

    def touch_last_worklog(self, issue):
        """
        Touch the last worklog for an issue (changes the updated date on the worklog).  We use this date as the 'mark' for
        determining the time elapsed for the next log entry.
        """
        worklogs = self.get_worklog(issue)
        if worklogs:
            last_worklog = worklogs[-1]
            last_worklog.update()
            return True

    def get_cycle_time(self, issue_or_start_or_key):
        """
        Provided an issue or a start datetime, will return the cycle time since the start or progress
        """
        if isinstance(issue_or_start_or_key, basestring):
            issue_or_start_or_key = self.get_issue(issue_or_start_or_key)

        if isinstance(issue_or_start_or_key, jira.resources.Issue):
            progress_started = self.get_datetime_issue_in_progress(issue_or_start_or_key)
        elif isinstance(issue_or_start_or_key, datetime.datetime):
            progress_started = issue_or_start_or_key

        curr_time = datetime.datetime.now(dateutil.tz.tzlocal())
        return utils.working_cycletime(progress_started, curr_time)

    def get_week_avg_cycletime(self):
        """
        Gets the average cycletime of the current user for the past week.
        This includes any ticket that was marked "In Progress" but not reopened.
        """
        def moving_average(new_val, old_avg, prev_n):
            return (new_val + old_avg) / (prev_n + 1)

        active_tickets_jql = 'assignee=currentUser() and status was "In Progress" DURING (startOfWeek(), endofweek()) and status not in (Backlog, Open) ORDER BY updated DESC'

        week_active_tickets = self.search_issues(active_tickets_jql)

        avg_cycletime = 0
        n_issues = 0
        for issue in week_active_tickets:
            cycle_time = self.get_cycle_time(self.get_issue(issue.key))
            avg_cycletime = moving_average(cycle_time, avg_cycletime, n_issues)
            n_issues = n_issues + 1

        return avg_cycletime
