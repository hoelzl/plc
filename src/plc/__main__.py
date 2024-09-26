import asyncio

import click

from .polyglot_language_converter import process_files


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
def main(glob_pattern: str, max_files: int | None, reprocess: bool):
    """Convert Java, Python, or C++ files to C# using various AI models."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(
        process_files(
            glob_pattern=glob_pattern, max_files=max_files, reprocess=reprocess
        )
    )
    print("Done!")


if __name__ == "__main__":
    main()
