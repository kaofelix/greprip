"""CLI entry point for grg."""

import shlex
import subprocess
import sys

from .translator import translate_grep_args


def main():
    """Main entry point - translate grep args and run rg."""
    grep_args = sys.argv[1:]
    
    # Handle grg-specific flags (before translation)
    dry_run = False
    if "--dry-run" in grep_args:
        dry_run = True
        grep_args = [a for a in grep_args if a != "--dry-run"]
    
    rg_args = translate_grep_args(grep_args)
    
    if dry_run:
        # Print the command that would be run
        cmd = ["rg"] + rg_args
        print(shlex.join(cmd))
        sys.exit(0)
    
    # Execute rg with translated arguments
    result = subprocess.run(["rg"] + rg_args)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
