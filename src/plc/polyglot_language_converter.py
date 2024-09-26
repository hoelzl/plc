# %%
import asyncio
import json
import os
import sqlite3
from pathlib import Path
from typing import Literal, TypedDict

import aiohttp

# %%
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")

# %%
DIRECTORY_PATH = Path(os.getcwd()).parent / "conversion"
DB_PATH = Path("converted_java_files.db")

# %%
MODELS = [
    ("anthropic/claude-3.5-sonnet:beta", "claude"),
    ("qwen/qwen-2.5-72b-instruct", "qwen"),
    ("google/gemini-pro-1.5-exp", "gemini"),
    ("openai/chatgpt-4o-latest", "chatgpt"),
]

# %%
INITIAL_PROMPT = """Convert the following notebook in jupytext format from Java, 
Python or C++ to C#:

1. Maintain the same number of markdown cells and preserve their contents, except for 
obvious language-specific conversions from the original programming language to "C#".
2. Maintain the same number of code cells, unless a utility class or other code is 
needed in one language but not the other. In such cases, add or remove the necessary 
code cells.
3. Preserve all cell tags and other metadata exactly as they are in the input file.
4. Convert the original code in each code cell to equivalent C# code, following the 
syntax and conventions of C#.
5. In particular:
   - Convert getters and setters to C# properties, and ensure that the code is 
   idiomatic C#.
   - Convert Java-specific constructs like `ArrayList` to their C# equivalents like 
   `List<T>`.
   - Convert Python-specific constructs like list comprehensions to equivalent C# code.
   - Convert C++-specific constructs like `std::vector` to their C# equivalents like 
   `List<T>`.
   - Ensure that the converted code is properly indented and follows C# naming 
   conventions and brace style.
   - Ensure that the resulting notebook uses the C# comment character `//` for comments.
   - Convert the IJava magic command `%maven` to the C# magic command `#r` with a 
   corresponding NuGet package.
   - When a notebook contains a cell with `import static 
   testrunner.TestRunner.runTests;` assume that a file `XunitTestRunner.cs` exists, 
   defining a class `XunitTestRunner` with a static method `RunTests` and import this 
   class using the `#load` magic.
   - Use xUnit.net for assertions and test discovery.
   - Convert all JUnit tests to xUnit.net tests.
   - Convert all Catch2 tests to xUnit.net tests.
   - Convert all Mockito mocks to Moq mocks.
6. Ensure that no additional output or comments are generated during the conversion 
process.
7. If any additional imports or utility classes are required for the converted C# 
code, add them as separate code cells with appropriate tags and metadata.
8. Do not modify the order or structure of the markdown and code cells, 
unless absolutely necessary for the conversion.

Please confirm that you understand these instructions before we begin the conversion 
process."""

# %%
CONVERT_CHUNK_PROMPT = """Convert the following chunk of code to C#, following the 
instructions provided earlier:

{chunk}

Reply with only the converted C# code. Do not add any explanations or comments about 
the conversion process."""

# %%
MAX_CHUNK_SIZE = 8192


# %%
class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


# %%
def split_into_chunks(content, max_chunk_size=MAX_CHUNK_SIZE):
    chunks = []
    current_chunk = ""
    for line in content.split("\n"):
        if len(current_chunk) + len(line) + 1 > max_chunk_size and (
            line.startswith("# %%") or line.startswith("// %%")
        ):
            chunks.append(current_chunk.strip())
            current_chunk = ""
        current_chunk += line + "\n"
        if len(current_chunk) >= max_chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = ""
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


# %%
TEST_CONTENT = """// %%
import java.util.ArrayList;
import java.util.List;

// %% [markdown] lang="de" tags=["subslide"]
// # Test auf Deutsch

// %% [markdown] lang="en" tags=["subslide"]
// ## Test in English

// %%
public class Test {
    public static void main(String[] args) {
        List<String> list = new ArrayList<>();
        list.add("Hello, world!");
        System.out.println(list);
    }
}
"""

# %%
split_into_chunks(TEST_CONTENT, 50)


# %%
async def send_to_openrouter(
    session: aiohttp.ClientSession,
    messages: list[Message],
    model: str,
    max_retries: int = 3,
    retry_delay: int = 5,
) -> str:
    headers = {"Authorization": f"Bearer {API_KEY}"}

    data = json.dumps(
        {
            "model": model,
            "messages": messages,
        }
    )

    for attempt in range(max_retries):
        try:
            async with session.post(
                url=OPENROUTER_API_URL, headers=headers, data=data
            ) as response:
                if response.status == 200:
                    response_json = await response.json()
                    return response_json["choices"][0]["message"]["content"]
                else:
                    response_text = await response.text()
                    raise RuntimeError(f"Failed to convert chunk: {response_text}")
        except Exception as e:
            if attempt < max_retries - 1:
                print(
                    f"Attempt {attempt + 1} failed. Retrying in {retry_delay} "
                    f"seconds..."
                )
                await asyncio.sleep(retry_delay)
            else:
                raise RuntimeError(
                    f"Failed to convert chunk after {max_retries} attempts: {str(e)}"
                )
    raise RuntimeError("This should never happen")


# %%
def set_up_database(conn, cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS converted_files (
            file_name TEXT,
            model TEXT,
            PRIMARY KEY (file_name, model)
        )
        """
    )
    conn.commit()


# %%
def create_database(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    set_up_database(conn, cursor)
    return conn


# %%
def has_file_been_processed(cursor, file_path, model):
    cursor.execute(
        "SELECT file_name FROM converted_files WHERE file_name = ? AND model = ?",
        (file_path.name, model),
    )
    return cursor.fetchone() is not None


# %%
async def process_file(file_path, model, model_suffix, cursor, conn, reprocess):
    if has_file_been_processed(cursor, file_path, model) and not reprocess:
        print(f"Skipping {file_path} for model {model} (already processed)")
        return

    with file_path.open("r", encoding="utf-8") as f:
        file_content = f.read()
    print(f"File content: {file_content[:160]}... ({len(file_content)} characters)")

    chunks = split_into_chunks(file_content)

    converted_chunks = []
    async with aiohttp.ClientSession() as session:
        # Initial conversation
        messages = [
            {"role": "user", "content": INITIAL_PROMPT},
        ]
        response = await send_to_openrouter(session, messages, model)
        messages.append({"role": "assistant", "content": response})

        for i, chunk in enumerate(chunks):
            print(
                f"Processing chunk {i + 1} of file {file_path.name} with model {model}"
            )
            try:
                messages.append(
                    {
                        "role": "user",
                        "content": CONVERT_CHUNK_PROMPT.format(chunk=chunk),
                    }
                )
                converted_chunk = await send_to_openrouter(session, messages, model)
                converted_chunks.append(converted_chunk)
                messages.append({"role": "assistant", "content": converted_chunk})
            except Exception as e:
                print(
                    f"Failed to convert chunk {i + 1} of file {file_path.name} with "
                    f"model {model} after 3 attempts: {str(e)}"
                )
                return

    if len(converted_chunks) == len(chunks):
        converted_content = "\n\n".join(converted_chunks)

        outfile_path = file_path.with_suffix(f".{model_suffix}.cs")

        with outfile_path.open("w", encoding="utf-8") as f:
            f.write(converted_content)

        cursor.execute(
            "INSERT OR REPLACE INTO converted_files (file_name, model) VALUES (?, ?)",
            (file_path.name, model),
        )
        conn.commit()
    else:
        print(f"Conversion incomplete for {file_path.name} with model {model}")


# %%
async def process_files(max_files=None, glob_pattern="*.java", reprocess=False):
    num_files_processed = 0
    conn = create_database()
    cursor = conn.cursor()

    for file_path in DIRECTORY_PATH.rglob(glob_pattern):
        if max_files and num_files_processed >= max_files:
            print(f"Exit: {num_files_processed} files processed.")
            break

        if "old" in str(file_path).lower() or "backup" in str(file_path).lower():
            continue

        if should_skip_file(file_path):
            print(f"Skipping {file_path} (indicated by file name)")
            continue

        print(f"Processing {file_path}")
        num_files_processed += 1

        tasks = [
            process_file(file_path, model, model_suffix, cursor, conn, reprocess)
            for model, model_suffix in MODELS
        ]
        await asyncio.gather(*tasks)

    conn.close()


# %%
def should_skip_file(file_path):
    return ".ipynb_checkpoints" in str(file_path).lower()
