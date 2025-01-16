from .screen import Screen
from .utils import process_commits, status_char_color

import git

from typing import Optional
from functools import partial
from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import terminal256


class Ui:
    def __init__(self, scr: Screen):
        self.scr = scr
        self.repo: Optional[git.Repo] = None
        self.__commits: Optional[list[git.Commit]] = None

    def set_repo(self, repo: git.Repo):
        self.repo = repo

    def display_commits(self, commits: list[git.Commit]):
        if self.repo is None:
            raise RuntimeError("Repo is not setup")

        self.scr.clear()
        self.scr.restore_pos("display_commits")
        self.scr.define_quit_action(self.scr.default_quit)

        self.__commits = commits
        for n, c in enumerate(process_commits(self.repo, commits)):
            self.scr.add_line(c, partial(self.display_commit, commits[n]))

    def display_diff_file(self, commit: git.Commit, filename: str):
        self.scr.backup_pos("display_commit")
        self.scr.define_quit_action(partial(self.display_commit, commit))
        self.scr.clear()

        diff = commit.diff(
            commit.parents[0] if commit.parents else None,
            create_patch=True,
            paths=[filename],
            R=True,
        )

        for diff_item in diff:
            diff_item: git.Diff

            assert diff_item.diff is not None

            if isinstance(diff_item.diff, bytes):
                patch = diff_item.diff.decode()
            else:
                patch = diff_item.diff

            print(
                highlight(
                    patch,
                    DiffLexer(),
                    terminal256.Terminal256Formatter(style="vim"),
                )
            )

    def display_commit(self, commit: git.Commit):
        if self.__commits is None:
            raise RuntimeError("Don't call display_commit directly")

        if self.repo is None:
            raise RuntimeError("Repo is not setup")

        self.scr.backup_pos("display_commits")

        self.scr.define_quit_action(partial(self.display_commits, self.__commits or []))
        self.scr.clear()
        self.scr.restore_pos("display_commit")

        output = self.repo.git.show("--name-status", commit.hexsha)
        for line in output.splitlines():
            if "\t" in line:
                l = line.split("\t")
                status = l[0]
                file_path = l[-1]
                self.scr.add_line(
                    f"{status_char_color(status)}\t{file_path}",
                    partial(self.display_diff_file, commit, file_path),
                )
            else:
                self.scr.add_line(line)
