import asyncio
import sys
from pathlib import Path

import click
from loguru import logger

from plc.defaults import default_models
from plc.open_router_provider import OpenRouterProvider
from .polyglot_language_converter import PolyglotLanguageConverter


@click.command()
@click.option(
    "--from",
    "from_",
    default="java",
    type=click.Choice(["cpp", "csharp", "java", "python", "typescript"]),
    help="The source language",
)
@click.option(
    "--to",
    default="csharp",
    type=click.Choice(["cpp", "csharp", "java", "python", "typescript"]),
    help="The target language",
)
@click.option(
    "--max-files", default=None, type=int, help="Maximum number of files to process"
)
@click.option(
    "--reprocess",
    is_flag=True,
    help="Reprocess files even if they've been processed before",
)
@click.option(
    "--db-path",
    default=None,
    type=click.Path(dir_okay=False, file_okay=True, resolve_path=True, path_type=Path),
    help="Path to the database of processed files",
)
@click.option(
    "--dir-path",
    default=None,
    type=click.Path(
        dir_okay=True, file_okay=False, exists=True, resolve_path=True, path_type=Path
    ),
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["TRACE", "DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Logging level",
)
@click.option(
    "--max-chunk-size",
    default=8192,
    type=int,
    help="Maximum size of each chunk sent to the LLM",
)
@click.option(
    "--models",
    default=None,
    type=str,
    help="Comma-separated list of model slugs to use (e.g., claude,qwen)",
)
def main(
    from_: str,
    to: str,
    max_files: int | None,
    reprocess: bool,
    db_path: Path | None,
    dir_path: Path,
    log_level: str,
    max_chunk_size: int,
    models: str | None,
):
    """Convert slides between programming languages using various AI models."""

    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.trace(f"Set log level to {log_level}")

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if db_path is None:
        db_path = Path.cwd() / "processed-files.sqlite3"
    if dir_path is None:
        dir_path = Path.cwd()

    if models:
        selected_slugs = models.split(",")
        selected_models = [
            model for model in all_models if model.slug in selected_slugs
        ]
        if not selected_models:
            raise ValueError(f"No valid models found for the specified slugs: {models}")
    else:
        selected_models = default_models

    converter = PolyglotLanguageConverter(
        llm_provider=OpenRouterProvider(),
        models=selected_models,
        from_slug=from_,
        to_slug=to,
        max_chunk_size=max_chunk_size,
        db_path=db_path,
        directory_path=dir_path,
    )

    loop.run_until_complete(
        converter.process_files(max_files=max_files, reprocess=reprocess)
    )
    print("Done!")


if __name__ == "__main__":
    main()
