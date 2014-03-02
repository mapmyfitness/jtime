""" Tests for jtime utils module """
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
