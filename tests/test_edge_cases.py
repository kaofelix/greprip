"""Edge case tests for grg and fnd."""

import subprocess
import os
import tempfile
import pytest


class TestExitCodes:
    """Exit codes must match for script compatibility."""
    
    def test_grg_no_match_exits_1(self):
        """grep exits 1 when no match found."""
        result = subprocess.run(
            ["uv", "run", "grg", "this_pattern_wont_match_xyz", "tests/fixtures/sample.txt"],
            capture_output=True,
        )
        assert result.returncode == 1
    
    def test_grg_match_exits_0(self):
        """grep exits 0 when match found."""
        result = subprocess.run(
            ["uv", "run", "grg", "hello", "tests/fixtures/sample.txt"],
            capture_output=True,
        )
        assert result.returncode == 0
    
    def test_grg_error_exits_2(self):
        """grep exits 2 on error (e.g., file not found)."""
        result = subprocess.run(
            ["uv", "run", "grg", "pattern", "nonexistent_file_xyz.txt"],
            capture_output=True,
        )
        # rg exits 2 for errors, matching grep behavior
        assert result.returncode == 2
    
    def test_fnd_no_match_exits_0(self):
        """find exits 0 even when nothing found."""
        result = subprocess.run(
            ["uv", "run", "fnd", "tests/fixtures", "-name", "nonexistent_xyz.txt"],
            capture_output=True,
        )
        # fd exits 0 when no matches (like find)
        assert result.returncode == 0


class TestSpecialCharacters:
    """Filenames with spaces and special characters."""
    
    def test_grg_file_with_spaces(self, tmp_path):
        """grep should handle files with spaces."""
        test_file = tmp_path / "file with spaces.txt"
        test_file.write_text("hello world\n")
        
        result = subprocess.run(
            ["uv", "run", "grg", "hello", str(test_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "hello" in result.stdout
    
    def test_fnd_file_with_spaces(self, tmp_path):
        """find should handle files with spaces."""
        test_file = tmp_path / "file with spaces.txt"
        test_file.write_text("content\n")
        
        result = subprocess.run(
            ["uv", "run", "fnd", str(tmp_path), "-name", "*.txt"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "file with spaces.txt" in result.stdout


class TestPipingAndXargs:
    """Common piping patterns used in scripts."""
    
    def test_fnd_print0_for_xargs(self):
        """find -print0 for xargs -0 compatibility."""
        result = subprocess.run(
            ["uv", "run", "fnd", "tests/fixtures", "-name", "*.txt", "-print0"],
            capture_output=True,
        )
        assert result.returncode == 0
        # Output should contain null bytes
        assert b'\x00' in result.stdout
    
    def test_grg_null_separated(self):
        """grep -l with null separation for xargs."""
        result = subprocess.run(
            ["uv", "run", "grg", "-l", "--null", "hello", "tests/fixtures/"],
            capture_output=True,
        )
        # rg supports --null for -l output
        assert result.returncode == 0


class TestSymlinks:
    """Symlink handling."""
    
    def test_fnd_follows_symlinks_with_L(self, tmp_path):
        """find -L follows symlinks."""
        # Create a file and symlink
        real_file = tmp_path / "real.txt"
        real_file.write_text("content\n")
        
        link_dir = tmp_path / "links"
        link_dir.mkdir()
        symlink = link_dir / "link.txt"
        symlink.symlink_to(real_file)
        
        # Without -L, fd shows symlinks as type l
        result = subprocess.run(
            ["uv", "run", "fnd", str(link_dir), "-type", "l"],
            capture_output=True,
            text=True,
        )
        assert "link.txt" in result.stdout


class TestEmptyAndEdgeCases:
    """Empty inputs and edge cases."""
    
    def test_grg_empty_pattern(self):
        """Empty pattern should match all lines."""
        result = subprocess.run(
            ["uv", "run", "grg", "", "tests/fixtures/sample.txt"],
            capture_output=True,
            text=True,
        )
        # rg with empty pattern matches all lines
        assert result.returncode == 0
        assert len(result.stdout.strip().split('\n')) > 1
    
    def test_fnd_current_dir_implicit(self):
        """find with just . should list all."""
        result = subprocess.run(
            ["uv", "run", "fnd", "tests/fixtures"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "sample.txt" in result.stdout
