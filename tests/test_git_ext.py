""" Tests for the jtime git_ext module. """
import unittest

from jtime import git_ext


class JtimeGitTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = git_ext.GIT()

    def tearDown(self):
        pass

    def test_branch(self):
        self.assertNotEqual(self.repo.branch, None)
