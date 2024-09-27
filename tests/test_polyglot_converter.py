from pathlib import Path

import pytest

from conftest import file_processor_stub
from plc.model import Model
from plc.polyglot_language_converter import PolyglotLanguageConverter


def test_connect_to_database(in_memory_db, llm_provider_spy):
    """
    Test that the database connection is properly established and the table is created.
    This ensures that our database setup is correct for further operations.
    """
    converter = PolyglotLanguageConverter(llm_provider=llm_provider_spy)
    with converter.connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND "
            "name='converted_files'"
        )
        assert cursor.fetchone() is not None


@pytest.mark.asyncio
async def test_process_files(file_processor_stub, llm_provider_spy, tmp_path):
    """
    Test that process_files correctly iterates over files and calls FileProcessor.
    This verifies the main workflow of the PolyglotLanguageConverter.
    """
    converter = PolyglotLanguageConverter(
        llm_provider=llm_provider_spy,
        db_path=":memory:",
        directory_path=tmp_path,
    )
    converter.models = [
        Model(id="model1", slug="gpt"),
        Model(id="model2", slug="llama"),
        Model(id="model3", slug="qwen"),
    ]

    for file_index in range(1, 5):
        (tmp_path / f"file{file_index}.java").write_text(f"File {file_index}")

    await converter.process_files(max_files=2)

    output_files = list(tmp_path.glob("*.cs"))
    assert len(output_files) == 6  # 2 files processed * 3 models

    output_file_names = [file.name for file in output_files]
    assert "file1.gpt.cs" in output_file_names
    assert "file1.qwen.cs" in output_file_names
    assert "file1.llama.cs" in output_file_names
    assert "file2.gpt.cs" in output_file_names
    assert "file2.qwen.cs" in output_file_names
    assert "file2.llama.cs" in output_file_names


def test_skip_file_because_of_name(llm_provider_spy):
    """
    Test that files with specific keywords are skipped.
    This ensures that our file filtering logic works as expected.
    """
    converter = PolyglotLanguageConverter(llm_provider=llm_provider_spy)
    assert converter.skip_file_because_of_name(Path("old_file.java")) == True
    assert converter.skip_file_because_of_name(Path("backup_file.java")) == True
    assert converter.skip_file_because_of_name(Path("old/file.java")) == True
    assert (
        converter.skip_file_because_of_name(Path(".ipynb_checkpoints/file.java"))
        == True
    )
    assert converter.skip_file_because_of_name(Path("normal_file.java")) == False
