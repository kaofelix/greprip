"""Translate grep arguments to rg arguments."""

import re


# Flags that are identical in grep and rg (no argument)
IDENTICAL_SHORT_FLAGS = {"-i", "-n", "-v", "-w", "-l", "-c", "-o", "-h", "-H", "-q", "-F", "-P"}

# Short flags that take an argument and are identical
IDENTICAL_SHORT_FLAGS_WITH_ARG = {"-A", "-B", "-C", "-e", "-f", "-m"}

# Flags to drop (rg defaults or not needed)
DROP_SHORT_FLAGS = {"-r", "-R", "-E", "-G"}  # rg is recursive by default, ERE is default, -G is BRE (grep default)

# Long option mappings (grep long option -> rg equivalent)
LONG_OPTION_MAP = {
    "--ignore-case": "-i",
    "--line-number": "-n",
    "--invert-match": "-v",
    "--word-regexp": "-w",
    "--files-with-matches": "-l",
    "--count": "-c",
    "--only-matching": "-o",
    "--no-filename": "-h",
    "--with-filename": "-H",
    "--quiet": "-q",
    "--silent": "-q",
    "--fixed-strings": "-F",
    "--perl-regexp": "-P",
    "--extended-regexp": None,  # Drop, rg default
    "--basic-regexp": None,  # Drop
    "--recursive": None,  # Drop, rg default
}

# Long options that take an argument
LONG_OPTIONS_WITH_ARG = {"--after-context", "--before-context", "--context", "--regexp", "--file", "--max-count"}


def translate_grep_args(args: list[str]) -> list[str]:
    """
    Translate grep command-line arguments to rg equivalents.
    
    Args:
        args: List of arguments (without the 'grep' command itself)
        
    Returns:
        List of arguments suitable for rg
    """
    result = []
    i = 0
    
    while i < len(args):
        arg = args[i]
        
        # Handle numeric context shorthand: -3 means -C 3
        if re.match(r'^-\d+$', arg):
            num = arg[1:]
            result.extend(["-C", num])
            i += 1
            continue
        
        # Handle --color variants
        if arg == "--color":
            result.append("--color=always")
            i += 1
            continue
        if arg.startswith("--color="):
            result.append(arg)
            i += 1
            continue
        
        # Handle -s (suppress errors) -> --no-messages
        if arg == "-s":
            result.append("--no-messages")
            i += 1
            continue
        
        # Handle --include=PATTERN
        if arg.startswith("--include="):
            pattern = arg.split("=", 1)[1]
            result.extend(["-g", pattern])
            i += 1
            continue
            
        # Handle --exclude=PATTERN  
        if arg.startswith("--exclude="):
            pattern = arg.split("=", 1)[1]
            result.extend(["-g", f"!{pattern}"])
            i += 1
            continue
        
        # Handle --exclude-dir=PATTERN
        if arg.startswith("--exclude-dir="):
            pattern = arg.split("=", 1)[1]
            result.extend(["-g", f"!{pattern}/"])
            i += 1
            continue
        
        # Handle long options with = value
        if arg.startswith("--") and "=" in arg:
            opt, value = arg.split("=", 1)
            if opt in LONG_OPTIONS_WITH_ARG:
                # Map to short form
                short_map = {
                    "--after-context": "-A",
                    "--before-context": "-B",
                    "--context": "-C",
                    "--regexp": "-e",
                    "--file": "-f",
                    "--max-count": "-m",
                }
                if opt in short_map:
                    result.extend([short_map[opt], value])
            else:
                result.append(arg)  # Pass through
            i += 1
            continue
        
        # Handle long options
        if arg.startswith("--"):
            if arg in LONG_OPTION_MAP:
                mapped = LONG_OPTION_MAP[arg]
                if mapped is not None:
                    result.append(mapped)
                # else: drop it
            elif arg in LONG_OPTIONS_WITH_ARG:
                # Next arg is the value
                short_map = {
                    "--after-context": "-A",
                    "--before-context": "-B",
                    "--context": "-C",
                    "--regexp": "-e",
                    "--file": "-f",
                    "--max-count": "-m",
                }
                if arg in short_map and i + 1 < len(args):
                    result.extend([short_map[arg], args[i + 1]])
                    i += 2
                    continue
                else:
                    result.append(arg)
            else:
                result.append(arg)  # Pass through unknown long options
            i += 1
            continue
        
        # Handle combined short flags like -ri, -rni
        if arg.startswith("-") and len(arg) > 2 and not arg[1].isdigit():
            expanded = expand_combined_flags(arg)
            for flag in expanded:
                if flag in IDENTICAL_SHORT_FLAGS:
                    result.append(flag)
                elif flag == "-s":
                    result.append("--no-messages")
                elif flag in DROP_SHORT_FLAGS:
                    pass  # Skip
                # Note: combined flags with args like -e are tricky, pass through
            i += 1
            continue
        
        # Handle short flags with arguments
        if arg in IDENTICAL_SHORT_FLAGS_WITH_ARG:
            result.append(arg)
            if i + 1 < len(args):
                result.append(args[i + 1])
                i += 2
                continue
            i += 1
            continue
        
        # Handle identical short flags
        if arg in IDENTICAL_SHORT_FLAGS:
            result.append(arg)
            i += 1
            continue
            
        # Handle flags to drop
        if arg in DROP_SHORT_FLAGS:
            i += 1
            continue
        
        # Everything else passes through (pattern, paths, etc.)
        result.append(arg)
        i += 1
    
    return result


def expand_combined_flags(arg: str) -> list[str]:
    """Expand combined flags like -ri into [-r, -i]."""
    flags = []
    for char in arg[1:]:  # Skip the leading -
        flags.append(f"-{char}")
    return flags
