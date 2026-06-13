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


class TestContextLines:
    def test_after_context(self):
        result = translate_grep_args(["-A", "3", "hello", "file.txt"])
        assert "-A" in result
        assert "3" in result

    def test_before_context(self):
        result = translate_grep_args(["-B", "2", "hello", "file.txt"])
        assert "-B" in result
        assert "2" in result

    def test_context_both(self):
        result = translate_grep_args(["-C", "5", "hello", "file.txt"])
        assert "-C" in result
        assert "5" in result

    def test_combined_context_short_form(self):
        # grep allows -5 as shorthand for -C 5
        result = translate_grep_args(["-3", "hello", "file.txt"])
        assert "-C" in result
        assert "3" in result


class TestExplicitPattern:
    def test_single_pattern_with_e(self):
        result = translate_grep_args(["-e", "hello", "file.txt"])
        assert "-e" in result
        assert "hello" in result

    def test_multiple_patterns_with_e(self):
        result = translate_grep_args(["-e", "hello", "-e", "world", "file.txt"])
        assert result.count("-e") == 2
        assert "hello" in result
        assert "world" in result


class TestPatternFile:
    def test_patterns_from_file(self):
        result = translate_grep_args(["-f", "patterns.txt", "file.txt"])
        assert "-f" in result
        assert "patterns.txt" in result


class TestQuietAndSuppress:
    def test_quiet_mode(self):
        result = translate_grep_args(["-q", "hello", "file.txt"])
        assert "-q" in result

    def test_suppress_errors(self):
        # grep -s suppresses errors about nonexistent files
        # rg uses --no-messages
        result = translate_grep_args(["-s", "hello", "file.txt"])
        assert "--no-messages" in result


class TestColorHandling:
    def test_color_always(self):
        result = translate_grep_args(["--color=always", "hello", "file.txt"])
        assert "--color=always" in result

    def test_color_never(self):
        result = translate_grep_args(["--color=never", "hello", "file.txt"])
        assert "--color=never" in result

    def test_color_auto(self):
        result = translate_grep_args(["--color=auto", "hello", "file.txt"])
        assert "--color=auto" in result

    def test_color_flag_without_value(self):
        # --color alone means --color=always in grep
        result = translate_grep_args(["--color", "hello", "file.txt"])
        assert "--color=always" in result or "--color" in result


class TestFixedStrings:
    def test_fixed_strings(self):
        # grep -F treats pattern as literal, rg uses -F too
        result = translate_grep_args(["-F", "hello.world", "file.txt"])
        assert "-F" in result


class TestPerlRegex:
    def test_perl_regex(self):
        # grep -P for PCRE, rg uses -P too
        result = translate_grep_args(["-P", r"\bhello\b", "file.txt"])
        assert "-P" in result


class TestBREToEREConversion:
    """Test conversion of Basic Regular Expression (BRE) to Extended Regular Expression (ERE)."""

    def test_alternation(self):
        # BRE uses \| for alternation, ERE uses |
        result = translate_grep_args([r"foo\|bar", "file.txt"])
        assert result == ["foo|bar", "file.txt"]

    def test_one_or_more(self):
        # BRE uses \+ for one or more, ERE uses +
        result = translate_grep_args([r"foo\+", "file.txt"])
        assert result == ["foo+", "file.txt"]

    def test_zero_or_one(self):
        # BRE uses \? for zero or one, ERE uses ?
        result = translate_grep_args([r"foo\?", "file.txt"])
        assert result == ["foo?", "file.txt"]

    def test_grouping(self):
        # BRE uses \( \) for grouping, ERE uses ( )
        result = translate_grep_args([r"\(foo\)\?", "file.txt"])
        assert result == ["(foo)?", "file.txt"]

    def test_quantifier(self):
        # BRE uses \{n,m\} for quantifiers, ERE uses {n,m}
        result = translate_grep_args([r"foo\{1,3\}", "file.txt"])
        assert result == ["foo{1,3}", "file.txt"]

    def test_combined_bre_operators(self):
        # Test multiple BRE operators in one pattern
        result = translate_grep_args([r"\(foo\|bar\)\+", "file.txt"])
        assert result == ["(foo|bar)+", "file.txt"]

    def test_alternation_with_e_flag(self):
        # Pattern with -e flag should also be converted
        result = translate_grep_args(["-e", r"foo\|bar", "file.txt"])
        assert result == ["-e", "foo|bar", "file.txt"]

    def test_alternation_with_regexp_long(self):
        # Pattern with --regexp should also be converted
        result = translate_grep_args(["--regexp=foo\\|bar", "file.txt"])
        assert result == ["-e", "foo|bar", "file.txt"]

    def test_fixed_strings_no_conversion(self):
        # With -F, BRE escapes should NOT be converted (literal search)
        result = translate_grep_args(["-F", r"foo\|bar", "file.txt"])
        assert result == ["-F", r"foo\|bar", "file.txt"]

    def test_fixed_strings_combined_no_conversion(self):
        # With -F combined in flags like -Fi, no conversion
        result = translate_grep_args(["-Fi", r"foo\|bar", "file.txt"])
        assert r"foo\|bar" in result  # Should NOT be converted

    def test_literal_backslash_pipe_preserved(self):
        # If someone wants literal \| in ERE, they'd need to double escape
        # This test shows that \\| stays as \| (backslash then alternation)
        # But we can't distinguish user intent, so we just convert \| to |
        pass  # Documenting the limitation


class TestLongOptions:
    def test_ignore_case_long(self):
        result = translate_grep_args(["--ignore-case", "hello", "file.txt"])
        assert "-i" in result or "--ignore-case" in result

    def test_line_number_long(self):
        result = translate_grep_args(["--line-number", "hello", "file.txt"])
        assert "-n" in result or "--line-number" in result

    def test_recursive_long(self):
        result = translate_grep_args(["--recursive", "hello", "dir/"])
        assert "hello" in result  # -r should be dropped

    def test_word_regexp_long(self):
        result = translate_grep_args(["--word-regexp", "hello", "file.txt"])
        assert "-w" in result or "--word-regexp" in result

    def test_files_with_matches_long(self):
        result = translate_grep_args(["--files-with-matches", "hello", "dir/"])
        assert "-l" in result or "--files-with-matches" in result

    def test_invert_match_long(self):
        result = translate_grep_args(["--invert-match", "hello", "file.txt"])
        assert "-v" in result or "--invert-match" in result

    def test_count_long(self):
        result = translate_grep_args(["--count", "hello", "file.txt"])
        assert "-c" in result or "--count" in result
