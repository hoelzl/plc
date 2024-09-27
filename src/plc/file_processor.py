from pathlib import Path
from sqlite3 import Connection
from typing import List

from attrs import define, Factory
from loguru import logger

from plc.defaults import default_convert_chunk_prompt, default_initial_prompt
from plc.llm_provider import LlmProvider
from plc.message import Message
from plc.model import Model
from plc.prog_lang_spec import prog_lang_messages, prog_lang_specs
from src.plc.file_utils import split_into_chunks


@define
class FileProcessor:
    file_path: Path
    llm_provider: LlmProvider
    model: Model
    from_lang: str
    to_lang: str
    conn: Connection
    initial_prompt: str = default_initial_prompt
    convert_chunk_prompt: str = default_convert_chunk_prompt
    reprocess: bool = False
    messages: list[Message] = Factory(list)
    converted_chunks: list[str] = Factory(list)

    @property
    def from_suffix(self) -> str:
        return prog_lang_specs[self.from_lang].suffix

    @property
    def to_suffix(self) -> str:
        return prog_lang_specs[self.to_lang].suffix

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

        chunks = split_into_chunks(file_content)
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
            logger.warning(f"Failed converting chunks: {e}")
            return []

    def build_initial_message(self):
        return [
            Message(role="user", content=self.initial_prompt),
        ]

    def add_conversion_example_messages(self):
        self.messages.extend(
            (
                Message(
                    role="user",
                    content=self.convert_chunk_prompt.format(
                        chunk=prog_lang_messages[self.from_lang]
                    ),
                ),
                Message(role="assistant", content=prog_lang_messages[self.to_lang]),
            )
        )

    async def convert_chunk(self, chunk, index) -> str:
        try:
            self.messages.append(
                Message(
                    role="user",
                    content=self.convert_chunk_prompt.format(chunk=chunk),
                )
            )
            converted_chunk = await self.send_messages_to_llm()
        except Exception as e:
            logger.info(
                f"Failed to convert chunk {index + 1} of file {self.file_path.name} "
                f"with model {self.model.id}: {str(e)}"
            )
            raise
        return converted_chunk

    async def send_messages_to_llm(self):
        converted_chunk = await self.llm_provider.send_message(
            self.messages, self.model
        )
        self.messages.append(Message(role="assistant", content=converted_chunk))
        return converted_chunk

    def has_file_been_processed(self) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT file_name FROM converted_files WHERE file_name = ? AND model = ?",
            (self.file_path.name, self.model.id),
        )
        return cursor.fetchone() is not None

    def note_file_processed(self):
        self.conn.cursor().execute(
            (
                "INSERT OR REPLACE INTO converted_files (file_name, model)"
                " VALUES (?, ?)"
            ),
            (self.file_path.name, self.model.id),
        )
        self.conn.commit()

    def write_converted_chunks_to_file(self, converted_chunks: List[str]):
        converted_content = "".join(converted_chunks)
        outfile_path = self.output_file_path
        with outfile_path.open("w", encoding="utf-8") as f:
            f.write(converted_content)

    @property
    def output_file_path(self):
        return self.file_path.with_suffix(f".{self.model.slug}{self.to_suffix}")
