import datetime
import importlib.util as importlib
import git
import sys
import inspect

from .colors import Colors

from pathlib import Path


def get_commits(path: Path, n: int) -> tuple[git.Repo, list[git.Commit]]:
    repo = git.Repo(path)
    return repo, list(repo.iter_commits(max_count=n))


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


def process_commits(r: git.Repo, commits: list[git.Commit]) -> list[str]:
    ret = []

    for c in commits:
        t = datetime.datetime.fromtimestamp(c.committed_date)
        title = c.message.splitlines()[0].strip()
        sha = r.rev_parse(c.hexsha)
        ret.append(
            f"{t.strftime('%d-%m-%Y')} {Colors.BRIGHT_BLACK.value}{str(sha)[:7]}{Colors.RESET.value} {title}"
        )

    return ret


def status_char_color(status: str) -> str:
    match status:
        case "":
            return f"{Colors.BRIGHT_BLACK.value}U{Colors.RESET.value}"
        case "M":
            return f"{Colors.BRIGHT_CYAN.value}M{Colors.RESET.value}"
        case "T":
            return f"{Colors.YELLOW.value}T{Colors.RESET.value}"
        case "A":
            return f"{Colors.BRIGHT_GREEN.value}A{Colors.RESET.value}"
        case "D":
            return f"{Colors.BRIGHT_RED.value}R{Colors.RESET.value}"
        case "R":
            return f"{Colors.BRIGHT_PURPLE.value}R{Colors.RESET.value}"
        case "C":
            return f"{Colors.BRIGHT_BLUE.value}C{Colors.RESET.value}"
        case "U":
            return f"{Colors.BRIGHT_BROWN.value}U{Colors.RESET.value}"
        case _:
            raise RuntimeError(f"Unknown status {status}")
