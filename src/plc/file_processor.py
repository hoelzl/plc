import re
from pathlib import Path
from sqlite3 import Connection
from typing import List

from attrs import Factory, define, field
from loguru import logger

from plc.defaults import (
    default_convert_chunk_prompt,
    get_initial_prompt,
)
from plc.file_utils import split_into_chunks
from plc.llm_provider import LlmProvider
from plc.message import Message
from plc.model import Model
from plc.prog_lang_spec import prog_lang_conversions, prog_lang_specs


@define
class FileProcessor:
    file_path: Path
    llm_provider: LlmProvider
    model: Model
    from_slug: str
    to_slug: str
    conn: Connection
    max_chunk_size: int = 4096
    initial_prompt: str = field()
    convert_chunk_prompt: str = default_convert_chunk_prompt
    reprocess: bool = False
    messages: list[Message] = Factory(list)
    converted_chunks: list[str] = Factory(list)

    @initial_prompt.default  # noqa
    def _init_initial_prompt(self):
        self.initial_prompt = get_initial_prompt(self.from_slug, self.to_slug)

    @property
    def from_suffix(self) -> str:
        return prog_lang_specs[self.from_slug].suffix

    @property
    def to_suffix(self) -> str:
        return prog_lang_specs[self.to_slug].suffix

    @property
    def from_lang(self) -> str:
        return prog_lang_specs[self.from_slug].name

    @property
    def to_lang(self) -> str:
        return prog_lang_specs[self.to_slug].name

    async def process(self):
        if self.has_file_been_processed() and not self.reprocess:
            logger.info(
                f"Skipping {self.file_path} for model {self.model.id} "
                f"(already processed)"
            )
            return

        with self.file_path.open("r", encoding="utf-8") as f:
            file_content = f.read()
        logger.info(
            f"File content: {file_content[:120]}... ({len(file_content)} "
            f"characters)"
        )

        chunks = split_into_chunks(file_content, max_chunk_size=self.max_chunk_size)
        converted_chunks = await self.convert_chunks(chunks)

        if len(converted_chunks) == len(chunks):
            self.write_converted_chunks_to_file(converted_chunks)
            self.note_file_processed()
        else:
            logger.info(
                f"Conversion incomplete for {self.file_path.name} with "
                f"model {self.model.id}"
            )

    async def convert_chunks(self, chunks: list[str]) -> list[str]:
        converted_chunks: list[str] = []
        self.messages = self.build_initial_message()

        try:
            # The first message should just be an acknowledgement that the LLM has
            # understood the task
            ack_message = await self.send_messages_to_llm()
            logger.trace(f"{self.model.slug} replied with {ack_message[:80]}...")
            self.add_conversion_example_messages()

            for index, chunk in enumerate(chunks):
                logger.info(
                    f"Processing chunk {index + 1} of file {self.file_path.name} "
                    f"with model {self.model.slug}"
                )
                converted_chunk: str = await self.convert_chunk(chunk, index)
                converted_chunks.append(converted_chunk)
            return converted_chunks
        except Exception as e:
            logger.warning(
                f"Failed while converting chunks with model {self.model.slug}: {e}"
            )
            return []

    def build_initial_message(self):
        return [
            Message(
                role="user",
                content=self.initial_prompt.format(
                    from_lang=self.from_lang, to_lang=self.to_lang
                ),
            ),
        ]

    @logger.catch
    def add_conversion_example_messages(self):
        logger.trace(f"From: {self.from_slug} to {self.to_slug}")
        logger.trace(prog_lang_conversions[self.to_slug])
        self.messages.extend(
            (
                Message(
                    role="user",
                    content=self.convert_chunk_prompt.format(
                        chunk=prog_lang_conversions[self.from_slug],
                        from_lang=self.from_lang,
                        to_lang=self.to_lang,
                    ),
                ),
                Message(
                    role="assistant",
                    content=prog_lang_conversions[self.to_slug],
                ),
            )
        )
        logger.trace(
            f"Messages for {self.model.slug} after adding examples: {self.messages}"
        )

    @logger.catch
    async def convert_chunk(self, chunk, index) -> str:
        try:
            new_message = Message(
                role="user",
                content=self.convert_chunk_prompt.format(
                    chunk=chunk, from_lang=self.from_lang, to_lang=self.to_lang
                ),
            )
            self.messages.append(new_message)
            logger.trace(f"Added message: {new_message}")
            converted_chunk = await self.send_messages_to_llm()
            logger.trace(f"Converted chunk: {converted_chunk}")
            converted_chunk = self.clean_chunk(converted_chunk)

        except Exception as e:
            logger.info(
                f"Failed to convert chunk {index + 1} of file {self.file_path.name} "
                f"with model {self.model.id}: {str(e)}"
            )
            raise
        return converted_chunk

    def clean_chunk(self, chunk: str) -> str:
        if chunk is None:
            raise ValueError("Trying to clean invalid chunk.")
        # Remove enclosing tags if present
        pattern = rf"^```{self.to_slug}\n(.*)\n```$"
        match = re.match(pattern, chunk, re.DOTALL)
        if match:
            logger.info(f"Removing decoration from chunk for {self.model.slug}")
            result = match.group(1).strip()
            logger.trace(f"New chunk: {result}")
            return result
        return chunk

    @logger.catch
    async def send_messages_to_llm(self):
        converted_chunk = await self.llm_provider.send_message(
            self.messages, self.model
        )
        if converted_chunk is None:
            raise ValueError(f"{self.model.slug} returned None as converted chunk.")
        reply_message = Message(role="assistant", content=converted_chunk)
        self.messages.append(reply_message)
        logger.trace(f"Appended reply message: {reply_message}")
        return converted_chunk

    def has_file_been_processed(self) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT file_name FROM converted_files "
            "WHERE file_name = ? AND model = ? AND from_lang = ? AND to_lang = ?",
            (self.file_path.name, self.model.id, self.from_slug, self.to_slug),
        )
        return cursor.fetchone() is not None

    def note_file_processed(self):
        self.conn.cursor().execute(
            (
                "INSERT OR REPLACE INTO converted_files"
                " (file_name, model, from_lang, to_lang)"
                " VALUES (?, ?, ?, ?)"
            ),
            (self.file_path.name, self.model.id, self.from_slug, self.to_slug),
        )
        self.conn.commit()

    def write_converted_chunks_to_file(self, converted_chunks: List[str]):
        if any(c is None for c in converted_chunks):
            raise ValueError("Bad converted chunk detected. Not writing file")
        converted_content = "\n".join(converted_chunks)
        outfile_path = self.output_file_path
        with outfile_path.open("w", encoding="utf-8") as f:
            f.write(converted_content)

    @property
    def output_file_path(self):
        return self.file_path.with_suffix(f".{self.model.slug}{self.to_suffix}")
