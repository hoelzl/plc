import os
from pathlib import Path

from plc.model import Model

DIRECTORY_PATH = Path(os.getcwd()).parent / "conversion"
DB_PATH = Path("converted_java_files.db")
default_models = [
    Model(id="anthropic/claude-3.5-sonnet:beta", slug="claude"),
    Model(id="qwen/qwen-2.5-72b-instruct", slug="qwen"),
    Model(id="google/gemini-pro-1.5-exp", slug="gemini"),
    Model(id="openai/chatgpt-4o-latest", slug="chatgpt"),
]
default_initial_prompt = """Convert the following notebook in jupytext format from 
Java, Python or C++ to C#:

1. Maintain the same number of markdown cells and preserve their contents, except for obvious language-specific conversions from the original programming language to "C#".
2. Maintain the same number of code cells, unless a utility class or other code is needed in one language but not the other. In such cases, add or remove the necessary code cells.
3. Preserve all cell tags and other metadata exactly as they are in the input file.
4. Convert the original code in each code cell to equivalent C# code, following the syntax and conventions of C#.
5. In particular:
   - Convert getters and setters to C# properties, and ensure that the code is idiomatic C#.
   - Convert Java-specific constructs like `ArrayList` to their C# equivalents like `List<T>`.
   - Convert Python-specific constructs like list comprehensions to equivalent C# code.
   - Convert C++-specific constructs like `std::vector` to their C# equivalents like `List<T>`.
   - Ensure that the converted code is properly indented and follows C# naming conventions and brace style.
   - Ensure that the resulting notebook uses the C# comment character `//` for comments.
   - Convert the IJava magic command `%maven` to the C# magic command `#r` with a corresponding NuGet package.
   - When a notebook contains a cell with `import static testrunner.TestRunner.runTests;` assume that a file `XunitTestRunner.cs` exists, defining a class `XunitTestRunner` with a static method `RunTests` and import this class using the `#load` magic.
   - Use xUnit.net for assertions and test discovery.
   - Convert all JUnit tests to xUnit.net tests.
   - Convert all Catch2 tests to xUnit.net tests.
   - Convert all Mockito mocks to Moq mocks.
6. Ensure that no additional output or comments are generated during the conversion process.
7. If any additional imports or utility classes are required for the converted C# code, add them as separate code cells with appropriate tags and metadata.
8. Do not modify the order or structure of the markdown and code cells, unless absolutely necessary for the conversion.

Please confirm that you understand these instructions before we begin the conversion process."""
default_convert_chunk_prompt = """Convert the following chunk of code to C#, following the instructions provided earlier:

{chunk}

Reply with only the converted C# code. Do not add any explanations or comments about the conversion process."""
