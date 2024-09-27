import pytest

from conftest import FILE_PROCESSOR_TEST_TExT
from plc.message import Message
from plc.prog_lang_spec import prog_lang_conversions


def test_output_file_path_is_correct(file_processor_stub):
    assert file_processor_stub.output_file_path.name == "test_file.llama.cs"
    assert (
        file_processor_stub.output_file_path.parent
        == file_processor_stub.file_path.parent
    )


def test_note_file_processed_marks_file_as_processed(file_processor_stub):
    file_processor_stub.note_file_processed()
    assert file_processor_stub.has_file_been_processed()


@pytest.mark.asyncio
async def test_process_marks_file_as_processed(file_processor_stub):
    await file_processor_stub.process()
    assert file_processor_stub.has_file_been_processed()


@pytest.mark.asyncio
async def test_process_posts_expected_messages(file_processor_stub, tmp_path):
    await file_processor_stub.process()
    assert file_processor_stub.output_file_path.read_text() == "Received 5 message(s)"

    assert file_processor_stub.messages[0] == Message(
        role="user", content="initial-prompt"
    )

    assert file_processor_stub.messages[1] == Message(
        role="assistant", content="Received 1 message(s)"
    )

    expected_message = Message(
        role="user", content="convert " + prog_lang_conversions["java"]
    )
    assert file_processor_stub.messages[2] == expected_message

    expected_message = Message(
        role="assistant", content=prog_lang_conversions["csharp"]
    )
    assert file_processor_stub.messages[3] == expected_message

    expected_message = Message(
        role="user", content="convert " + FILE_PROCESSOR_TEST_TExT
    )
    assert file_processor_stub.messages[4] == expected_message
