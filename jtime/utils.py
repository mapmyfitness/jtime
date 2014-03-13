from __future__ import division  # This allows division to stay as a float
import datetime
import sys


def get_input(input_func, input_str):
    """
    Get input from the user given an input function and an input string
    """
    val = input_func("Please enter your {0}: ".format(input_str))
    while not val or not len(val.strip()):
        val = input_func("You didn't enter a valid {0}, please try again: ".format(input_str))
    return val


def working_cycletime(start, end, workday_start=datetime.timedelta(hours=0), workday_end=datetime.timedelta(hours=24)):
    """
    Get the working time between a beginning and an end point subtracting out non-office time
    """
    def clamp(t, start, end):
        "Return 't' clamped to the range ['start', 'end']"
        return max(start, min(end, t))

    def day_part(t):
        "Return timedelta between midnight and 't'."
        return t - t.replace(hour=0, minute=0, second=0)

    if not start:
        return None
    if not end:
        end = datetime.datetime.now()

    zero = datetime.timedelta(0)
    # Make sure that the work day is valid
    assert(zero <= workday_start <= workday_end <= datetime.timedelta(1))
    # Get the workday delta
    workday = workday_end - workday_start
    # Get the number of days it took
    days = (end - start).days + 1
    # Number of weeks
    weeks = days // 7
    # Get the number of days in addition to weeks
    extra = (max(0, 5 - start.weekday()) + min(5, 1 + end.weekday())) % 5
    # Get the number of working days
    weekdays = weeks * 5 + extra
    # Get the total time spent accounting for the workday
    total = workday * weekdays
    if start.weekday() < 5:
        # Figuring out how much time it wasn't being worked on and subtracting
        total -= clamp(day_part(start) - workday_start, zero, workday)
    if end.weekday() < 5:
        # Figuring out how much time it wasn't being worked on and subtracting
        total -= clamp(workday_end - day_part(end), zero, workday)

    cycle_time = timedelta_total_seconds(total) / timedelta_total_seconds(workday)
    return cycle_time


# Could we override the class to add this on import instead?
def timedelta_total_seconds(td):
    if sys.version_info >= (2, 7):
        return td.total_seconds()
    return td.days * 24 * 60 * 60 + td.seconds
