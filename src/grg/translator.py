"""Translate grep arguments to rg arguments."""

import re


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
    
    # Flags that are identical in grep and rg
    IDENTICAL_FLAGS = {"-i", "-n", "-v", "-w", "-l", "-c", "-o", "-h", "-H"}
    
    # Flags to drop (rg defaults or not needed)
    DROP_FLAGS = {"-r", "-R", "-E"}  # rg is recursive by default, ERE is default
    
    while i < len(args):
        arg = args[i]
        
        # Handle combined short flags like -ri, -rni
        if arg.startswith("-") and not arg.startswith("--") and len(arg) > 2:
            expanded = expand_combined_flags(arg)
            # Process each flag
            for flag in expanded:
                if flag in IDENTICAL_FLAGS:
                    result.append(flag)
                elif flag in DROP_FLAGS:
                    pass  # Skip
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
        
        # Handle identical flags
        if arg in IDENTICAL_FLAGS:
            result.append(arg)
            i += 1
            continue
            
        # Handle flags to drop
        if arg in DROP_FLAGS:
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
