"""CLI entry point for fnd."""

import subprocess
import sys

from .translator import translate_find_args


def main():
    """Main entry point - translate find args and run fd."""
    find_args = sys.argv[1:]
    fd_args = translate_find_args(find_args)
    
    result = subprocess.run(["fd"] + fd_args)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
