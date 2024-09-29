from attrs import define


@define
class ProgLangSpec:
    slug: str
    name: str
    glob_pattern: str
    suffix: str


prog_lang_specs: dict[str, ProgLangSpec] = {
    "cpp": ProgLangSpec(slug="cpp", name="C++", glob_pattern="*.cpp", suffix=".cpp"),
    "csharp": ProgLangSpec(slug="csharp", name="C#", glob_pattern="*.cs", suffix=".cs"),
    "java": ProgLangSpec(
        slug="java", name="Java", glob_pattern="*.java", suffix=".java"
    ),
    "python": ProgLangSpec(
        slug="python", name="Python", glob_pattern="*.py", suffix=".py"
    ),
}


prog_lang_conversions: dict[str, str] = {
    "cpp": (
        "// j2 from 'macros.j2' import header\n"
        '// {{ header("Funktionen in C++", "Functions in C++") }}\n'
        '// %% [markdown] lang="de" tags=["slide"]\n'
        "//\n// Da C++ eine statisch getypte Sprache ist, müssen wir bei \n"
        "// der Definition einer Funktion Typen für ihre Parameter und ihr \n"
        "// Ergebnis angeben.\n\n"
        '// %% [markdown] lang="en" tags=["slide"]\n'
        "//\n// As C++ is a statically typed language, we have to specify\n"
        "// types for its parameters and result when defining a function.\n"
        '// %% tags=["keep"]\n'
        "// #include <iostream>\n"
        "// #include <string>\n\n"
        '// %% tags=["keep"]\n'
        "void say_hi(std::str name) {\n"
        '    std::cout << "Hello," << name << "!\\n";\n'
        "}\n\n"
        '// %% tags=["keep"]\n'
        'say_hi("World")'
    ),
    "csharp": (
        "// j2 from 'macros.j2' import header\n"
        '// {{ header("Funktionen in C#", "Functions in C#") }}\n'
        '// %% [markdown] lang="de" tags=["slide"]\n'
        "//\n// Da C# eine statisch getypte Sprache ist, müssen wir bei \n"
        "// der Definition einer Funktion Typen für ihre Parameter und ihr \n"
        "// Ergebnis angeben.\n\n"
        '// %% [markdown] lang="en" tags=["slide"]\n'
        "//\n// As C# is a statically typed language, we have to specify\n"
        "// types for its parameters and result when defining a function.\n"
        '// %% tags=["keep"]\n'
        "using System;\n\n"
        "static void SayHi(string name)\n"
        "{\n"
        '    Console.WriteLine($"Hello, {name}!");\n'
        "}\n\n"
        '// %% tags=["keep"]\n'
        'SayHi("World");'
    ),
    "java": (
        "// j2 from 'macros.j2' import header\n"
        '// {{ header("Funktionen in Java", "Functions in Java") }}\n'
        '// %% [markdown] lang="de" tags=["slide"]\n'
        "//\n// Da Java eine statisch getypte Sprache ist, müssen wir bei \n"
        "// der Definition einer Funktion Typen für ihre Parameter und ihr \n"
        "// Ergebnis angeben.\n\n"
        '// %% [markdown] lang="en" tags=["slide"]\n'
        "//\n// As Java is a statically typed language, we have to specify\n"
        "// types for its parameters and result when defining a function.\n"
        '// %% tags=["keep"]\n'
        "public static void sayHi(String name) {\n"
        '    System.out.println("Hello, " + name);\n'
        "}\n\n"
        '// %% tags=["keep"]\n'
        'sayHi("World");'
    ),
    "python": (
        "# j2 from 'macros.j2' import header\n"
        '# {{ header("Funktionen in Python", "Functions in Python") }}\n'
        '# %% [markdown] lang="de" tags=["slide"]\n'
        "#\n# Da Python eine dynamisch getypte Sprache ist, müssen wir bei \n"
        "# der Definition einer Funktion keine Typen angeben.\n\n"
        '# %% [markdown] lang="en" tags=["slide"]\n'
        "#\n# As Python is a dynamically typed language, we don't have to\n"
        "# specify types when defining a function.\n"
        '# %% tags=["keep"]\n'
        "def say_hi(name):\n"
        '    print("Hello,", name)\n\n'
        '# %% tags=["keep"]\n'
        'say_hi("world")'
    ),
}
