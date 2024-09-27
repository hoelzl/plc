MAX_CHUNK_SIZE = 8192


def split_into_chunks(content: str, max_chunk_size: int = MAX_CHUNK_SIZE) -> list[str]:
    possible_chunks = split_into_possible_chunks(content)
    final_chunks = aggregate_chunks(max_chunk_size, possible_chunks)
    return final_chunks


def split_into_possible_chunks(content: str) -> list[str]:
    possible_chunks: list = []
    current_chunk = ""
    lines = content.splitlines(keepends=True)  # Keep original line endings

    for line in lines:
        if line.strip().startswith("# %%") or line.strip().startswith("// %%"):
            if current_chunk:
                possible_chunks.append(current_chunk)
            current_chunk = line
        else:
            current_chunk += line

    if current_chunk:
        possible_chunks.append(current_chunk)

    return possible_chunks


def aggregate_chunks(max_chunk_size: int, possible_chunks: list[str]) -> list[str]:
    final_chunks = []
    current_chunk = ""

    for chunk in possible_chunks:
        if len(chunk) > max_chunk_size:
            if current_chunk:
                final_chunks.append(current_chunk)
                current_chunk = ""
            final_chunks.append(chunk)
        elif len(current_chunk) + len(chunk) <= max_chunk_size:
            current_chunk += chunk
        else:
            final_chunks.append(current_chunk)
            current_chunk = chunk

    if current_chunk:
        final_chunks.append(current_chunk)

    return final_chunks
