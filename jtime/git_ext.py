import sys
import subprocess
import git
from git.errors import InvalidGitRepositoryError


class GIT(git.Repo):
    def __init__(self, **kwargs):
        try:
            super(GIT, self).__init__(**kwargs)
        except InvalidGitRepositoryError:
            print "You must be in a git repository to use jtime"
            sys.exit(1)

    @property
    def branch(self):
        """
        Gets the active branch in the current repo.

        Returns None if not in a git repo or no current branch
        """
        branch = None
        # Check if we are currently in a repo
        try:
            branch = self.active_branch
        except InvalidGitRepositoryError:
            print "Not in a git repo"
        return branch

    def get_last_commit_message(self):
        """
        Gets the last commit message on the active branch

        Returns None if not in a git repo
        """
        # Check if we are currently in a repo
        try:
            branch = self.active_branch
            return self.commit(branch).message
        except InvalidGitRepositoryError:
            print "Not in a git repo"
            return None

    def get_last_modified_timestamp(self):
        """
        Looks at the files in a git root directory and grabs the last modified timestamp
        """
        cmd = "find . -print0 | xargs -0 stat -f '%T@ %p' | sort -n | tail -1 | cut -f2- -d' '"
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        print output
