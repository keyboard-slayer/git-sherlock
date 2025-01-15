from .screen import Screen
from .utils import process_commits

import pygit2

from typing import Optional
from functools import partial


class Ui:
    def __init__(self, scr: Screen):
        self.scr = scr
        self.repo: Optional[pygit2.repository.Repository] = None
        self.__commits: Optional[list[pygit2.Commit]] = None

    def set_repo(self, repo: pygit2.repository.Repository):
        self.repo = repo

    def display_commits(self, commits: list[pygit2.Commit]):
        self.scr.clear()
        self.scr.restore_pos()
        self.scr.define_quit_action(self.scr.default_quit)
        self.__commits = commits
        for n, c in enumerate(process_commits(commits)):
            self.scr.add_line(c, partial(self.display_commit, commits[n]))

    def display_commit(self, commit: pygit2.Commit):
        if self.__commits is None:
            raise RuntimeError("Don't call display_commit directly")

        if self.repo is None:
            raise RuntimeError("Repo is not setup")

        self.scr.backup_pos()
        self.scr.define_quit_action(partial(self.display_commits, self.__commits or []))

        self.scr.clear()
        print(commit)
