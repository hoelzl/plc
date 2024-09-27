import pytest
from attr import Factory
from attrs import define

from plc.file_processor import FileProcessor
from plc.llm_provider import LlmProvider
from plc.message import Message
from plc.model import Model


@pytest.fixture
def in_memory_db():
    """
    Create an in-memory SQLite database for testing.
    This isolates our tests from the actual file system.
    """
    import sqlite3

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
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
    conn.commit()
    yield conn
    conn.close()


@define
class LlmProviderSpy(LlmProvider):
    sent_messages: list[list[Message]] = Factory(list)

    async def send_message(self, messages: list[Message], model: Model) -> str:
        self.sent_messages.append(messages)
        return f"Received {len(messages)} message(s)"


@pytest.fixture
def llm_provider_spy():
    return LlmProviderSpy()


FILE_PROCESSOR_TEST_TExT = """// %% [markdown] tags=["slide"]
// # This is a slide

// %%
class MyClass { /* some Java code */ }

// %% tags=["subslide"]
class YourClass { /* more Java code */ }

// %% [markdown] tags=["subslide"]
//
// And another slide
"""


@pytest.fixture
def file_processor_stub(llm_provider_spy, in_memory_db, tmp_path):
    file_to_process = tmp_path / "test_file.java"
    file_to_process.write_text(FILE_PROCESSOR_TEST_TExT)
    return FileProcessor(
        file_path=file_to_process,
        llm_provider=llm_provider_spy,
        model=Model("meta/llama", "llama"),
        from_lang="java",
        to_lang="csharp",
        initial_prompt="initial-prompt",
        convert_chunk_prompt="convert {chunk}",
        conn=in_memory_db,
    )
