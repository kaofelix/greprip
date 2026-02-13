"""Tests for the grg CLI."""

import subprocess


class TestDryRun:
    def test_dry_run_shows_rg_command(self):
        result = subprocess.run(
            ["uv", "run", "grg", "--dry-run", "-i", "hello", "file.txt"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "rg -i hello file.txt" in result.stdout

    def test_dry_run_with_combined_flags(self):
        result = subprocess.run(
            ["uv", "run", "grg", "--dry-run", "-ri", "hello", "dir/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "rg" in result.stdout
        assert "-i" in result.stdout
        assert "hello" in result.stdout
        # -r should be dropped
        assert "-r" not in result.stdout.split()

    def test_dry_run_with_include(self):
        result = subprocess.run(
            ["uv", "run", "grg", "--dry-run", "--include=*.py", "-r", "hello", "dir/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "-g" in result.stdout
        assert "*.py" in result.stdout
