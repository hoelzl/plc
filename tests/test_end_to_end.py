from pathlib import Path

import pytest

from plc.model import Model
from plc.open_router_provider import OpenRouterProvider
from plc.polyglot_language_converter import PolyglotLanguageConverter


# Disabled by renaming so that PyCharm does not complain about the test in the
# pre-commit hook.
# Add "test" in front of this test name to re-enable it
@pytest.mark.slow
@pytest.mark.asyncio
async def _convert_mockito_test(tmp_path):
    test_input = Path(__file__).parent / "data/mockito_test.java"
    test_file = tmp_path / "slides_mockito_test.java"
    text = test_input.read_text()
    test_file.write_text(text)

    converter = PolyglotLanguageConverter(
        llm_provider=OpenRouterProvider(),
        models=[Model(id="anthropic/claude-3.5-sonnet:beta", slug="sonnet")],
        from_slug="java",
        to_slug="csharp",
        max_chunk_size=4096,
        db_path=":memory:",
        directory_path=tmp_path,
    )
    await converter.process_files()

    test_output = test_file.with_suffix(".sonnet.cs")
    assert test_output.exists()

    result_text = test_output.read_text()
    assert len(result_text) > 500
