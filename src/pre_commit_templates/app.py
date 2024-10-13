from pathlib import Path
from typing import Annotated

import typer
from jinja2 import Template
from loguru import logger

from .configs import Configs
from .files import get_matching_files, is_up_to_date

__all__ = ["app"]

app = typer.Typer()


@app.command()
def main(
    updated_files: Annotated[
        list[Path],
        typer.Argument(help="Files to update. Must be relative to the root directory."),
    ],
    root: Annotated[
        Path | None,
        typer.Option(
            "-R",
            "--root",
            help="Directory to operate in. If not set, defaults to the root of the current git repository.",
        ),
    ] = None,
    mkdirs: Annotated[
        bool,
        typer.Option(
            "-m",
            "--mkdirs/--no-mkdirs",
            help="Create directories that don't exist for templates.",
        ),
    ] = True,
    use_mtime: Annotated[
        bool,
        typer.Option(
            "-M",
            "--mtime/--no-mtime",
            help="Use filesystem modify time to check if a template needs to be updated.",
        ),
    ] = True,
):
    configs = Configs.from_environment(root=root)

    template_directory = configs.resolve_template_directory()
    target_directory = configs.resolve_target_directory()
    matching_files = get_matching_files(
        template_directory=template_directory,
        target_directory=target_directory,
        updated_paths=updated_files,
    )

    errors: bool = False

    for template_path, target_path in matching_files:
        if not template_path.is_file():
            logger.error(f"Template path is not a valid file: {template_path}")
            errors = True
            continue
        elif not target_path.parent.exists():
            if mkdirs:
                target_path.parent.mkdir(parents=True)
            else:
                logger.error(f"Directory does not exist: {target_path}")
                errors = True
                continue
        elif use_mtime and is_up_to_date(target_path, template_path):
            logger.info(f"File is up to date: {target_path}")
            continue

        template_text = template_path.read_text()
        template_text = Template(template_text).render(configs.data)
        target_text = target_path.read_text() if target_path.exists() else None

        if template_text == target_text:
            logger.info(f"File is up to date: {target_path}")
            target_path.touch()
        else:
            _ = target_path.write_text(template_text)

    raise typer.Exit(errors)
