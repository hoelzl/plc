import os
from pathlib import Path

from plc.model import Model

DIRECTORY_PATH = Path(os.getcwd())
DB_PATH = Path("converted_java_files.db")
default_models = [
    Model(id="anthropic/claude-3.5-sonnet:beta", slug="claude"),
    Model(id="qwen/qwen-2.5-72b-instruct", slug="qwen"),
    Model(id="google/gemini-pro-1.5-exp", slug="gemini"),
    Model(id="openai/chatgpt-4o-latest", slug="chatgpt"),
]

default_initial_prompt_start = """Convert the following notebook in jupytext format from {from_lang} to {to_lang}:

1. Maintain the same number of markdown cells and preserve their contents, except for obvious language-specific conversions from {from_lang} language to {to_lang}.
2. Maintain the same number of code cells, unless a utility class or other code is needed in one language but not the other. In such cases, add or remove the necessary code cells.
3. Preserve all cell tags and other metadata exactly as they are in the input file.
4. Convert the original {from_lang} code in each code cell to equivalent {to_lang} code, following the syntax and conventions of {to_lang}.
5. Ensure that the converted code is properly indented and follows {to_lang} naming conventions and brace style.
6. Ensure that the resulting notebook uses the {to_lang} comment character for comments.
7. If any additional imports or utility classes are required for the converted {to_lang} code, add them as separate code cells with appropriate tags and metadata.
8. Do not modify the order or structure of the markdown and code cells, unless absolutely necessary for the conversion.
"""


language_specific_instructions = {
    "python_to_cpp": {
        "instructions": """
    - Use `snake_case` for variable and function names in C++ code.
    - Use `PascalCase` for struct, class and enumeration names in C++ code.
    - Convert Python-specific constructs like list comprehensions to equivalent C++ code.
    - Create getters and setters for each Python property annotated with `@property`
    - Ensure that the resulting notebook uses the C++ comment character `//` for comments.
    - Convert pytest tests to Catch2 tests.
    - Convert Python mocks to  Google Mock mocks.
    - Convert the IPython magic commands to appropriate C++ equivalents or remove them if they are not applicable.
"""
    },
    "python_to_java": {
        "instructions": """
    - Convert Python-specific constructs like list comprehensions to equivalent Java code.
    - Create getters and setters for each Python property annotated with `@property`
    - Ensure that the resulting notebook uses the Java comment character `//` for comments.
    - Convert pytest tests to JUnit tests.
    - Convert Python mocks to Mockito mocks.
    - Convert the IPython magic commands to appropriate Java equivalents or remove them if they are not applicable.
"""
    },
    "python_to_csharp": {
        "instructions": """
    - Convert Python-specific constructs like list comprehensions to equivalent C# code.
    - Ensure that the resulting notebook uses the C# comment character `//` for comments.
    - Convert pytest tests to xUnit.net tests.
    - Convert Python mocks to Moq mocks.
    - Convert the IPython magic commands to appropriate C# equivalents or remove them if they are not applicable.
    - Use `#r` for package references where applicable.
"""
    },
    "cpp_to_python": {
        "instructions": """
    - Use PEP-8 conventions for names.
    - Convert C++-specific constructs like `std::vector` to equivalent Python code.
    - Ensure that the resulting notebook uses the Python comment character `#` for comments.
    - Convert Catch2 tests to pytest tests.
    - Convert C++ mocks to Python mocks (e.g., `unittest.mock`).
    - Convert the C++ magic commands to appropriate Python equivalents or remove them if they are not applicable.
"""
    },
    "cpp_to_java": {
        "instructions": """
    - Convert C++-specific constructs like `std::vector` to equivalent Java code.
    - Ensure that the resulting notebook uses the Java comment character `//` for comments.
    - Convert Catch2 tests to JUnit tests.
    - Convert C++ mocks to Mockito mocks.
    - Convert the C++ magic commands to appropriate Java equivalents or remove them if they are not applicable.
"""
    },
    "cpp_to_csharp": {
        "instructions": """
    - Convert C++-specific constructs like `std::vector` to equivalent C# code.
    - Ensure that the resulting notebook uses the C# comment character `//` for comments.
    - Convert Catch2 tests to xUnit.net tests.
    - Convert C++ mocks to Moq mocks.
    - Convert the C++ magic commands to appropriate C# equivalents or remove them if they are not applicable.
    - Use `#r` for package references where applicable.
"""
    },
    "java_to_python": {
        "instructions": """
    - Use PEP-8 conventions for names.
    - Convert Java-specific constructs like `ArrayList` to equivalent Python code.
    - Ensure that the resulting notebook uses the Python comment character `#` for comments.
    - Convert JUnit tests to pytest tests.
    - Convert Mockito mocks to Python mocks (e.g., `unittest.mock`).
    - Convert the IJava magic commands to appropriate Python equivalents or remove them if they are not applicable.
"""
    },
    "java_to_cpp": {
        "instructions": """
    - Use `snake_case` for variable and function names in C++ code.
    - Use `PascalCase` for struct, class and enumeration names in C++ code.
    - Convert Java-specific constructs like `ArrayList` to equivalent C++ code.
    - Ensure that the resulting notebook uses the C++ comment character `//` for comments.
    - Convert JUnit tests to Catch2 tests.
    - Convert Mockito mocks to C++ mocking frameworks (e.g., Mockitcpp or Google Mock).
    - Convert the IJava magic commands to appropriate C++ equivalents or remove them if they are not applicable.
"""
    },
    "java_to_csharp": {
        "instructions": """
    - Convert Java-specific constructs like `ArrayList` to equivalent C# code.
    - Convert getters and setters to C# properties.
    - Ensure that the resulting notebook uses the C# comment character `//` for comments.
    - Convert JUnit tests to xUnit.net tests.
    - Convert Mockito mocks to Moq mocks.
    - Convert the IJava magic command `%maven` to the C# magic command `#r` with a corresponding NuGet package.
    - When a notebook contains a cell with `import static testrunner.TestRunner.runTests;` assume that a file `XunitTestRunner.cs` exists, defining a class `XunitTestRunner` with a static method `RunTests` and import this class using the `#load` magic.
"""
    },
    "csharp_to_python": {
        "instructions": """
    - Use PEP-8 conventions for names.
    - Convert C#-specific constructs like `List<T>` to equivalent Python code.
    - Ensure that the resulting notebook uses the Python comment character `#` for comments.
    - Convert xUnit.net tests to pytest tests.
    - Convert Moq mocks to Python mocks (e.g., `unittest.mock`).
    - Convert the C# magic commands to appropriate Python equivalents or remove them if they are not applicable.
"""
    },
    "csharp_to_cpp": {
        "instructions": """
    - Use `snake_case` for variable and function names in C++ code.
    - Use `PascalCase` for struct, class and enumeration names in C++ code.
    - Convert C#-specific constructs like `List<T>` to equivalent C++ code.
    - Ensure that the resulting notebook uses the C++ comment character `//` for comments.
    - Convert xUnit.net tests to Catch2 tests.
    - Convert Moq mocks to C++ mocking frameworks (e.g., Mockitcpp or Google Mock).
    - Convert the C# magic commands to appropriate C++ equivalents or remove them if they are not applicable.
"""
    },
    "csharp_to_java": {
        "instructions": """
    - Convert C#-specific constructs like `List<T>` to equivalent Java code.
    - Ensure that the resulting notebook uses the Java comment character `//` for comments.
    - Convert xUnit.net tests to JUnit tests.
    - Convert Moq mocks to Mockito mocks.
    - Convert the C# magic command `#r` to the IJava magic command `%maven` with a corresponding Maven package.
    - When a notebook contains a cell with `#load "XunitTestRunner.cs"`; assume that a Jar-file `testrunner-0.1.jar` exists, defining a class `TestRunner` with a static method `runTests` and import this class using the magic commands `%jars .` and `%classpath testrunner-0.1.jar`.
    - When a notebook requires JUnit, import the following packages with the `%maven` magic:
        - `%maven org.junit.jupiter:junit-jupiter-api:5.8.2`
        - `%maven org.junit.jupiter:junit-jupiter-engine:5.8.2`
        - `%maven org.junit.jupiter:junit-jupiter-params:5.8.2`
        - `%maven org.junit.platform:junit-platform-launcher:1.9.3`
"""
    },
}

default_initial_prompt_end = """Please confirm that you understand these instructions before we begin the conversion process."""


def get_initial_prompt(from_lang: str, to_lang: str):
    initial_prompt = default_initial_prompt_start.format(
        from_lang=from_lang, to_lang=to_lang
    )
    language_specific = language_specific_instructions[f"{from_lang}_to_{to_lang}"][
        "instructions"
    ]
    final_prompt = default_initial_prompt_end
    return initial_prompt + language_specific + final_prompt


default_convert_chunk_prompt = """Convert the following chunk of code to {to_lang}, following the instructions provided earlier:

{chunk}

Reply with only the converted {to_lang} code. Do not add any explanations or comments about the conversion process."""
