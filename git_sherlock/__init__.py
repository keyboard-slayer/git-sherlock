import typer
import sys
import traceback
import importlib.util as importlib

from pathlib import Path
from typing_extensions import Annotated


# === Plugin loader ============================================================

sys.path.append(str(Path(__file__).parents[1]))

pluginDir = Path.home() / ".config" / "git_sherlock" / "plugins"
pluginDir.mkdir(parents=True, exist_ok=True)

with open(pluginDir / "__init__.py", "w") as f:
    f.writelines(
        [
            f"from . import {f.name.split('.')[0]}\n"
            for f in pluginDir.glob("*.py")
            if f.name != "__init__.py"
        ]
    )

spec = importlib.spec_from_file_location("plugin", pluginDir / "__init__.py")

if not spec or not spec.loader:
    sys.stderr.write(f"[-] Couldn't load plugin file __init__.py")

module = importlib.module_from_spec(spec)
sys.modules["plugin"] = module

try:
    spec.loader.exec_module(module)
except Exception as e:
    print(f"[-] Couldn't load plugins: {traceback.format_exc()}")
    exit()

# ==============================================================================

from .screen import Screen
from .ui import Ui
from .utils import get_commits

app = typer.Typer()
scr = Screen()
ui = Ui(scr)


@app.command()
def recent(
    path: Annotated[Path, typer.Option("--repo", "-r")] = Path.cwd(),
    n: Annotated[int, typer.Option("--number", "-n")] = 100,
):
    repo, commits = get_commits(path, n)
    ui.set_repo(repo)
    ui.display_commits(commits)
    scr.mainloop()


def main():
    app()
