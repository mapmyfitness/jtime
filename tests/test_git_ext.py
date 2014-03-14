""" Tests for the jtime git_ext module. """
import git
import mock
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from jtime import git_ext


class JtimeGitTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = git_ext.GIT()

    def tearDown(self):
        pass

    def test_init_repo_InvalidGitRepository(self):
        with mock.patch('git.Repo.__init__') as mock_git_init:
            mock_git_init.side_effect = git.errors.InvalidGitRepositoryError

            with self.assertRaises(SystemExit):
                git_ext.GIT()

    def test_branch(self):
        with mock.patch('jtime.git_ext.GIT.active_branch', new_callable=mock.PropertyMock) as mock_active_branch:
            mock_active_branch.return_value = 'test'
            self.assertNotEqual(self.repo.branch, None)

    def test_branch_raises_InvalidGitRepositoryError(self):
        with mock.patch('jtime.git_ext.GIT.active_branch', new_callable=mock.PropertyMock) as mock_active_branch:
            mock_active_branch.side_effect=git.errors.InvalidGitRepositoryError
            self.repo.branch

    def test_get_last_commit_message(self):
        # Since travis-ci doesn't operate on a branch but a commit
        with mock.patch('jtime.git_ext.GIT.active_branch', new_callable=mock.PropertyMock) as mock_active_branch:
            mock_active_branch.return_value = self.repo.heads[0].name
            self.assertIsInstance(self.repo.get_last_commit_message(), basestring)

    def test_get_last_commit_message_raises_InvalidGitRepositoryError(self):
        with mock.patch('jtime.git_ext.GIT.active_branch', new_callable=mock.PropertyMock) as mock_active_branch:
            mock_active_branch.side_effect = git.errors.InvalidGitRepositoryError
            self.assertEquals(self.repo.get_last_commit_message(), None)
