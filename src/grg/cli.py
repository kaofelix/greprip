"""CLI entry point for grg."""

import subprocess
import sys

from .translator import translate_grep_args


def main():
    """Main entry point - translate grep args and run rg."""
    # Skip the program name, translate the rest
    grep_args = sys.argv[1:]
    rg_args = translate_grep_args(grep_args)
    
    # Execute rg with translated arguments
    result = subprocess.run(["rg"] + rg_args)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
