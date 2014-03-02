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
