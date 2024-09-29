import asyncio
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection
from typing import List

from attrs import Factory, define

from plc.defaults import (
    DIRECTORY_PATH,
    default_convert_chunk_prompt,
    default_initial_prompt_start,
    default_models,
    get_initial_prompt,
)
from plc.file_processor import FileProcessor
from plc.llm_provider import LlmProvider
from plc.model import Model
from plc.open_router_provider import OpenRouterProvider
from plc.prog_lang_spec import prog_lang_specs


@define
class PolyglotLanguageConverter:
    llm_provider: LlmProvider
    models: List[Model] = Factory(list)
    from_slug: str = "java"
    to_slug: str = "csharp"
    initial_prompt: str = ""
    convert_chunk_prompt: str = ""
    db_path: Path | str = ":memory:"
    directory_path: Path = DIRECTORY_PATH
    max_chunk_size: int = 8192

    def __attrs_post_init__(self):
        if not self.initial_prompt:
            self.initial_prompt = get_initial_prompt(self.from_slug, self.to_slug)

    @property
    def glob_pattern(self):
        return prog_lang_specs[self.from_slug].glob_pattern

    @property
    def from_suffix(self):
        return prog_lang_specs[self.from_slug].suffix

    @property
    def to_suffix(self):
        return prog_lang_specs[self.to_slug].suffix

    @contextmanager
    def connect_to_database(self) -> Connection:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS converted_files (
                    file_name TEXT,
                    model TEXT,
                    from_lang TEXT,
                    to_lang TEXT,
                    PRIMARY KEY (file_name, model, from_lang, to_lang)
                )
                """
            )
            cursor.close()
            yield conn
        finally:
            conn.close()

    async def process_files(
        self,
        max_files: int = None,
        reprocess: bool = False,
    ):
        num_files_processed = 0
        with self.connect_to_database() as conn:
            for file_path in self.directory_path.rglob(self.glob_pattern):
                if max_files and num_files_processed >= max_files:
                    print(f"Exit: {num_files_processed} files processed.")
                    break

                if self.skip_file_because_of_name(file_path):
                    continue

                print(f"Processing {file_path}")
                num_files_processed += 1

                tasks = [
                    FileProcessor(
                        file_path=file_path,
                        llm_provider=self.llm_provider,
                        model=model,
                        from_slug=self.from_slug,
                        to_slug=self.to_slug,
                        conn=conn,
                        max_chunk_size=self.max_chunk_size,
                        initial_prompt=self.initial_prompt,
                        convert_chunk_prompt=self.convert_chunk_prompt,
                        reprocess=reprocess,
                    ).process()
                    for model in self.models
                ]
                await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    def skip_file_because_of_name(file_path):
        return (
            "old" in str(file_path).lower()
            or "backup" in str(file_path).lower()
            or ".ipynb_checkpoints" in str(file_path).lower()
        )


if __name__ == "__main__":
    converter = PolyglotLanguageConverter(
        llm_provider=OpenRouterProvider(),
        models=default_models,
        initial_prompt=default_initial_prompt_start,
        convert_chunk_prompt=default_convert_chunk_prompt,
    )

    asyncio.run(converter.process_files())
