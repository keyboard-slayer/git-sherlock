import datetime
import importlib.util as importlib
import pygit2
import sys

from .colors import Colors

from pathlib import Path


def get_commits(
    path: Path, n: int
) -> tuple[pygit2.repository.Repository, list[pygit2.Commit]]:
    dotGit = pygit2.discover_repository(str(path))

    if dotGit is None:
        raise RuntimeError(f"{path} is not a valid git repository")

    repo = pygit2.repository.Repository(dotGit)
    head_commit = repo[repo.head.target]

    commits: list[pygit2.Commit] = []

    for commit in repo.walk(head_commit.id, pygit2.enums.SortMode.TOPOLOGICAL):
        if len(commits) > n:
            break

        commits.append(commit)

    return repo, commits


def load_plugins():
    pluginDir = Path.home() / ".config" / "git-search" / "plugins"
    pluginDir.mkdir(parents=True, exist_ok=True)

    sys.modules["git_search"] = sys.modules[__name__]

    for plugin in pluginDir.glob("*.py"):
        spec = importlib.spec_from_file_location("plugin", plugin)

        if not spec or not spec.loader:
            sys.stderr.write(f"[-] Couldn't load plugin file {plugin}")
            continue

        module = importlib.module_from_spec(spec)
        sys.modules["plugin"] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            sys.stderr.write(f"[-] Couldn't load plugin file {plugin}: {e}")
            continue


def process_commits(commits: list[pygit2.Commit]) -> list[str]:
    ret = []

    for c in commits:
        t = datetime.datetime.fromtimestamp(c.commit_time)
        title = c.message.splitlines()[0].strip()
        ret.append(
            f"{t.strftime('%d-%m-%Y')} {Colors.BRIGHT_BLACK.value}{c.short_id}{Colors.RESET.value} {title}"
        )

    return ret
