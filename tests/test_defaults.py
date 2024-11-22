import pytest

from plc.defaults import get_initial_prompt


def test_get_initial_prompt_contains_from_and_to_language():
    unit = get_initial_prompt("csharp", "python")
    assert "C#" in unit
    assert "Python" in unit


def test_get_initial_prompt_contains_only_from_and_to_language():
    unit = get_initial_prompt("csharp", "python")
    assert "C++" not in unit
    assert "Java" not in unit


@pytest.mark.parametrize(
    "lang,framework",
    [
        ("cpp", "Catch2"),
        ("java", "JUnit"),
        ("csharp", "xUnit.net"),
        ("python", "pytest"),
    ],
)
def test_assert_get_initial_prompt_mentions_from_test_framework(lang, framework):
    a_random_language = "python" if lang == "csharp" else "csharp"
    unit = get_initial_prompt(lang, a_random_language)
    assert framework in unit


@pytest.mark.parametrize(
    "lang,framework",
    [
        ("cpp", "Catch2"),
        ("java", "JUnit"),
        ("csharp", "xUnit.net"),
        ("python", "pytest"),
        ("typescript", "Deno"),
    ],
)
def test_assert_get_initial_prompt_mentions_to_test_framework(lang, framework):
    a_random_language = "python" if lang == "cpp" else "cpp"
    unit = get_initial_prompt(a_random_language, lang)
    assert framework in unit
