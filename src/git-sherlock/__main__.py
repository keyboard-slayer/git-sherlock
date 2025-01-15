import typer

from .screen import Screen
from .ui import Ui
from .utils import get_commits, load_plugins

from pathlib import Path
from typing_extensions import Annotated

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


if __name__ == "__main__":
    load_plugins()
    app()
