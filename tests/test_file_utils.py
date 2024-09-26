import pytest

from src.plc.file_utils import split_into_chunks


def test_single_small_chunk():
    content = "# %%\nSmall chunk"
    result = split_into_chunks(content, max_chunk_size=20)
    assert result == [content]


def test_multiple_small_chunks():
    content = "# %%\nChunk 1\n# %%\nChunk 2\n# %%\nChunk 3"
    result = split_into_chunks(content, max_chunk_size=30)
    assert result == ["# %%\nChunk 1\n# %%\nChunk 2\n", "# %%\nChunk 3"]


def test_single_large_chunk():
    content = "# %%\n" + "x" * 100
    result = split_into_chunks(content, max_chunk_size=50)
    assert result == [content]


def test_mixed_size_chunks():
    content = "# %%\nSmall\n# %%\n" + "x" * 100 + "\n# %%\nAnother small"
    result = split_into_chunks(content, max_chunk_size=50)
    assert result == [
        "# %%\nSmall\n",
        "# %%\n" + "x" * 100 + "\n",
        "# %%\nAnother small",
    ]


def test_exact_size_chunks():
    content = "# %%\n" + "x" * 23 + "\n# %%\n" + "y" * 23
    result = split_into_chunks(content, max_chunk_size=30)
    assert result == ["# %%\n" + "x" * 23 + "\n", "# %%\n" + "y" * 23]


def test_empty_content():
    content = ""
    result = split_into_chunks(content, max_chunk_size=50)
    assert result == []


def test_no_chunk_markers():
    content = "No markers here\nJust plain text"
    result = split_into_chunks(content, max_chunk_size=50)
    assert result == [content]


def test_different_markers():
    content = "# %%\nPython\n// %%\nJavaScript"
    result = split_into_chunks(content, max_chunk_size=10)
    assert result == ["# %%\nPython\n", "// %%\nJavaScript"]


# Parametrized test for different max_chunk_sizes
@pytest.mark.parametrize(
    "max_chunk_size, expected",
    [
        (20, ["# %%\nSmall\n", "# %%\nChunk\n", "# %%\nAnother"]),
        (30, ["# %%\nSmall\n# %%\nChunk\n", "# %%\nAnother"]),
        (50, ["# %%\nSmall\n# %%\nChunk\n# %%\nAnother"]),
    ],
)
def test_different_max_chunk_sizes(max_chunk_size, expected):
    content = "# %%\nSmall\n# %%\nChunk\n# %%\nAnother"
    result = split_into_chunks(content, max_chunk_size=max_chunk_size)
    assert result == expected
