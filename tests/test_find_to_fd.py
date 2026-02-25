"""Unit tests for find → fd argument translation."""

import pytest
from fnd.translator import translate_find_args


class TestBasicUsage:
    def test_path_only(self):
        # find /path → fd . /path
        result = translate_find_args(["/some/path"])
        assert "/some/path" in result

    def test_current_dir(self):
        # find . → fd . .
        result = translate_find_args(["."])
        assert "." in result


class TestNamePatterns:
    def test_name_pattern(self):
        # find -name "*.txt" → fd -g "*.txt" or fd ".*\.txt$"
        result = translate_find_args([".", "-name", "*.txt"])
        assert "*.txt" in " ".join(result) or ".txt" in " ".join(result)

    def test_iname_pattern(self):
        # find -iname "*.txt" → fd -i ... 
        result = translate_find_args([".", "-iname", "*.TXT"])
        assert "-i" in result

    def test_name_with_path(self):
        result = translate_find_args(["/path", "-name", "*.py"])
        assert "/path" in result
        assert "*.py" in " ".join(result) or ".py" in " ".join(result)


class TestTypeFilter:
    def test_type_file(self):
        # find -type f → fd -t f
        result = translate_find_args([".", "-type", "f"])
        assert "-t" in result or "--type" in result
        assert "f" in result or "file" in result

    def test_type_directory(self):
        # find -type d → fd -t d
        result = translate_find_args([".", "-type", "d"])
        assert "-t" in result or "--type" in result
        assert "d" in result or "directory" in result

    def test_type_symlink(self):
        # find -type l → fd -t l
        result = translate_find_args([".", "-type", "l"])
        assert "-t" in result or "--type" in result
        assert "l" in result or "symlink" in result


class TestDepthControl:
    def test_maxdepth(self):
        # find -maxdepth 2 → fd -d 2 or --max-depth 2
        result = translate_find_args([".", "-maxdepth", "2"])
        assert "-d" in result or "--max-depth" in result
        assert "2" in result

    def test_mindepth(self):
        # find -mindepth 1 → fd --min-depth 1
        result = translate_find_args([".", "-mindepth", "1"])
        assert "--min-depth" in result
        assert "1" in result


class TestExcludePatterns:
    def test_not_name(self):
        # find ! -name "*.pyc" → fd -E "*.pyc"
        result = translate_find_args([".", "!", "-name", "*.pyc"])
        assert "-E" in result or "--exclude" in result
        assert "*.pyc" in " ".join(result)

    def test_prune_directory(self):
        # find -name ".git" -prune -o -print is complex
        # Basic: find -path "*/.git" -prune → fd -E .git
        result = translate_find_args([".", "-path", "*/.git", "-prune", "-o", "-type", "f", "-print"])
        # Should exclude .git somehow
        assert "-E" in result or "--exclude" in result or ".git" in " ".join(result)


class TestExecuteActions:
    def test_print(self):
        # find -print is default, should be handled
        result = translate_find_args([".", "-name", "*.txt", "-print"])
        # -print is implicit in fd, should not cause issues
        assert "*.txt" in " ".join(result) or ".txt" in " ".join(result)

    def test_print0(self):
        # find -print0 → fd -0
        result = translate_find_args([".", "-print0"])
        assert "-0" in result or "--print0" in result


class TestCombinations:
    def test_name_and_type(self):
        result = translate_find_args([".", "-name", "*.py", "-type", "f"])
        assert "-t" in result or "--type" in result
        assert "*.py" in " ".join(result) or ".py" in " ".join(result)

    def test_path_name_maxdepth(self):
        result = translate_find_args(["/path", "-maxdepth", "3", "-name", "*.js"])
        assert "/path" in result
        assert "-d" in result or "--max-depth" in result
        assert "3" in result


class TestHiddenFiles:
    def test_include_hidden_default(self):
        # find includes hidden by default, fd doesn't
        # We need to add -H to fd to match find behavior
        result = translate_find_args([".", "-name", "*.txt"])
        assert "-H" in result or "--hidden" in result


class TestExec:
    def test_exec_single(self):
        # find -exec cmd {} \; → fd -x cmd
        result = translate_find_args([".", "-name", "*.py", "-exec", "wc", "-l", "{}", ";"])
        assert "-x" in result
        assert "wc" in result
        assert "-l" in result

    def test_exec_batch(self):
        # find -exec cmd {} + → fd -X cmd (batch)
        result = translate_find_args([".", "-type", "f", "-exec", "chmod", "644", "{}", "+"])
        assert "-X" in result
        assert "chmod" in result
        assert "644" in result

    def test_exec_with_grep(self):
        # Common pattern: find -exec grep
        result = translate_find_args([".", "-name", "*.py", "-exec", "grep", "pattern", "{}", ";"])
        assert "-x" in result
        assert "grep" in result
        assert "pattern" in result


class TestFollowSymlinks:
    def test_follow_symlinks(self):
        # find -L → fd -L
        result = translate_find_args(["-L", ".", "-name", "*.txt"])
        assert "-L" in result


class TestOrPatterns:
    """Test handling of -o (OR) with multiple -name patterns."""

    def test_simple_or_patterns(self):
        # find . -name "a" -o -name "b" -o -name "c"
        # Should translate to fd --glob '{a,b,c}' .
        result = translate_find_args([".", "-name", ".ruby-version", "-o", "-name", ".tool-versions", "-o", "-name", "mise.toml"])
        
        # Should use brace expansion pattern
        result_str = " ".join(result)
        assert "{" in result_str or "|" in result_str
        # Should contain all the patterns
        assert ".ruby-version" in result_str
        assert ".tool-versions" in result_str
        assert "mise.toml" in result_str

    def test_or_with_path_and_maxdepth(self):
        # find /path -maxdepth 3 -name "a" -o -name "b"
        result = translate_find_args(["/path", "-maxdepth", "3", "-name", ".ruby-version", "-o", "-name", ".tool-versions"])
        
        result_str = " ".join(result)
        assert "/path" in result_str
        assert "-d" in result_str or "--max-depth" in result_str
        assert "{" in result_str or "|" in result_str
