"""Unit tests for grep → rg argument translation."""

import pytest
from grg.translator import translate_grep_args


class TestBasicPatterns:
    def test_simple_pattern_and_file(self):
        assert translate_grep_args(["hello", "file.txt"]) == ["hello", "file.txt"]

    def test_pattern_only(self):
        assert translate_grep_args(["hello"]) == ["hello"]


class TestCommonFlags:
    def test_case_insensitive(self):
        assert translate_grep_args(["-i", "hello", "file.txt"]) == [
            "-i", "hello", "file.txt"
        ]

    def test_line_numbers(self):
        assert translate_grep_args(["-n", "hello", "file.txt"]) == [
            "-n", "hello", "file.txt"
        ]

    def test_recursive(self):
        assert translate_grep_args(["-r", "hello", "dir/"]) == [
            "hello", "dir/"
        ]  # rg is recursive by default

    def test_invert_match(self):
        assert translate_grep_args(["-v", "hello", "file.txt"]) == [
            "-v", "hello", "file.txt"
        ]

    def test_word_boundary(self):
        assert translate_grep_args(["-w", "foo", "file.txt"]) == [
            "-w", "foo", "file.txt"
        ]

    def test_files_with_matches(self):
        assert translate_grep_args(["-l", "hello", "dir/"]) == [
            "-l", "hello", "dir/"
        ]

    def test_count(self):
        assert translate_grep_args(["-c", "hello", "file.txt"]) == [
            "-c", "hello", "file.txt"
        ]


class TestCombinedFlags:
    def test_recursive_case_insensitive(self):
        # -ri should drop -r (rg default) but keep -i
        result = translate_grep_args(["-ri", "hello", "dir/"])
        assert "-i" in result
        assert "hello" in result
        assert "dir/" in result

    def test_multiple_separate_flags(self):
        result = translate_grep_args(["-i", "-n", "hello", "file.txt"])
        assert "-i" in result
        assert "-n" in result
        assert "hello" in result


class TestExtendedRegex:
    def test_extended_regex_flag(self):
        # grep -E is default in rg, so we can drop it
        assert translate_grep_args(["-E", "foo|bar", "file.txt"]) == [
            "foo|bar", "file.txt"
        ]


class TestIncludeExclude:
    def test_include_pattern(self):
        result = translate_grep_args(["--include=*.py", "-r", "hello", "dir/"])
        assert "-g" in result or "--glob" in result
        assert "*.py" in " ".join(result)

    def test_exclude_pattern(self):
        result = translate_grep_args(["--exclude=*.pyc", "-r", "hello", "dir/"])
        assert "-g" in result or "--glob" in result
        assert "!*.pyc" in " ".join(result) or "*.pyc" in " ".join(result)
