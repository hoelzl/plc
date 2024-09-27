import asyncio
from pathlib import Path

import click

from plc.defaults import (
    default_convert_chunk_prompt,
    default_initial_prompt,
    default_models,
)
from plc.open_router_provider import OpenRouterProvider
from .polyglot_language_converter import PolyglotLanguageConverter


@click.command()
@click.option(
    "--glob-pattern", default="*.java", help="Glob pattern for files to process"
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
    type=click.Path(),
    help="Path to the database of processed files",
    dir_okay=False,
    file_okay=True,
)
def main(
    glob_pattern: str, max_files: int | None, reprocess: bool, db_path: Path | None
):
    """Convert Java, Python, or C++ files to C# using various AI models."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if db_path is None:
        db_path = Path.cwd() / "processed-files.sqlite3"

    converter = PolyglotLanguageConverter(
        llm_provider=OpenRouterProvider(),
        models=default_models,
        initial_prompt=default_initial_prompt,
        convert_chunk_prompt=default_convert_chunk_prompt,
        db_path=db_path,
    )

    loop.run_until_complete(
        converter.process_files(
            glob_pattern=glob_pattern, max_files=max_files, reprocess=reprocess
        )
    )
    print("Done!")


if __name__ == "__main__":
    main()
