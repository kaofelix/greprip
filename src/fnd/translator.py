"""Translate find arguments to fd arguments."""


def translate_find_args(args: list[str]) -> list[str]:
    """
    Translate find command-line arguments to fd equivalents.
    
    Args:
        args: List of arguments (without the 'find' command itself)
        
    Returns:
        List of arguments suitable for fd
    """
    result = []
    paths = []
    pattern = None
    i = 0
    
    # fd needs -H to show hidden files (find shows them by default)
    result.append("-H")
    
    while i < len(args):
        arg = args[i]
        
        # Path arguments (don't start with -)
        if not arg.startswith("-") and arg not in ("!", "(", ")"):
            # Check if it looks like a path (first positional args before options)
            if not any(a.startswith("-") for a in args[:i]) or i == 0:
                paths.append(arg)
                i += 1
                continue
        
        # -name PATTERN → -g PATTERN (glob)
        if arg == "-name":
            if i + 1 < len(args):
                pattern = args[i + 1]
                result.extend(["-g", pattern])
                i += 2
                continue
        
        # -iname PATTERN → -i -g PATTERN (case insensitive glob)
        if arg == "-iname":
            if i + 1 < len(args):
                pattern = args[i + 1]
                result.extend(["-i", "-g", pattern])
                i += 2
                continue
        
        # -type TYPE
        if arg == "-type":
            if i + 1 < len(args):
                find_type = args[i + 1]
                result.extend(["-t", find_type])
                i += 2
                continue
        
        # -maxdepth N → -d N
        if arg == "-maxdepth":
            if i + 1 < len(args):
                result.extend(["-d", args[i + 1]])
                i += 2
                continue
        
        # -mindepth N → --min-depth N
        if arg == "-mindepth":
            if i + 1 < len(args):
                result.extend(["--min-depth", args[i + 1]])
                i += 2
                continue
        
        # -print0 → -0
        if arg == "-print0":
            result.append("-0")
            i += 1
            continue
        
        # -print is default, skip it
        if arg == "-print":
            i += 1
            continue
        
        # ! -name PATTERN → -E PATTERN (exclude)
        if arg == "!":
            if i + 1 < len(args) and args[i + 1] == "-name" and i + 2 < len(args):
                result.extend(["-E", args[i + 2]])
                i += 3
                continue
            # Skip lone ! for now
            i += 1
            continue
        
        # -path PATTERN -prune -o ... -print → -E PATTERN (simplified)
        if arg == "-path":
            if i + 1 < len(args):
                path_pattern = args[i + 1]
                # Check if followed by -prune
                if i + 2 < len(args) and args[i + 2] == "-prune":
                    # Extract the directory name from pattern like "*/.git"
                    exclude_pattern = path_pattern.replace("*/", "").replace("*", "")
                    result.extend(["-E", exclude_pattern])
                    i += 3
                    # Skip -o if present
                    if i < len(args) and args[i] == "-o":
                        i += 1
                    continue
            i += 1
            continue
        
        # -prune alone (already handled above, skip)
        if arg == "-prune":
            i += 1
            continue
        
        # -o (or) - skip, we handle the main expression
        if arg == "-o":
            i += 1
            continue
        
        # Unknown args - skip for now
        i += 1
    
    # fd requires a pattern - if none specified via -name/-iname, use "." (match all)
    # The pattern must come before paths in fd
    if pattern is None:
        result.append(".")
    
    # Add paths at the end (fd takes paths after pattern/options)
    if paths:
        result.extend(paths)
    
    return result
