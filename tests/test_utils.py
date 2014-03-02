""" Tests for jtime utils module """
import datetime
import mock
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from jtime import utils


class JtimeUtilsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_input(self):
        input_func = mock.Mock(return_value="valid input")
        utils.get_input(input_func, "Test to get input!")

    def test_get_input_bad_input(self):
        input_func = mock.Mock(side_effect=["", None, "input!"])
        utils.get_input(input_func, "Test to get input!")

    def test_timedelta_total_seconds(self):
        one_day = datetime.timedelta(1)  # 1 day
        one_day_sec = 60 * 60 * 24

        one_hr = datetime.timedelta(hours=1)
        one_hr_sec = 60 * 60

        self.assertEquals(utils.timedelta_total_seconds(one_day), one_day_sec)
        self.assertEquals(utils.timedelta_total_seconds(one_hr), one_hr_sec)

    def test_working_cycletime(self):
        mon_noon = datetime.datetime(2014, 3, 3, 12)
        cycle_time = utils.working_cycletime(mon_noon, (mon_noon + datetime.timedelta(hours=1)))

        self.assertEquals(cycle_time, (1 / 24.0))  # 1hr of 24 total

    def test_working_cycletime_no_start(self):
        self.assertEquals(utils.working_cycletime(None, None), None)

    def test_working_cycletime_no_end(self):
        # making sure it's a very small number because we said start was now and end was assumed as now
        assert utils.working_cycletime(datetime.datetime.now(), None) < (1 / (24.0 * 60))
