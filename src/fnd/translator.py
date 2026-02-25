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
    patterns = []  # Support multiple patterns (for OR operations)
    exec_args = []  # Store -x/-X args separately (must come last)
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
        
        # -name PATTERN → collect pattern for later (might be OR'd)
        if arg == "-name":
            if i + 1 < len(args):
                patterns.append(args[i + 1])
                i += 2
                continue
        
        # -iname PATTERN → -i option + collect pattern
        if arg == "-iname":
            if i + 1 < len(args):
                result.append("-i")  # Add case-insensitive flag once
                patterns.append(args[i + 1])
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
        
        # -o (or) - continue collecting patterns (already handled)
        if arg == "-o":
            i += 1
            continue
        
        # -exec cmd {} \; → -x cmd
        # -exec cmd {} + → -X cmd (batch mode)
        if arg == "-exec":
            cmd_args = []
            i += 1
            batch_mode = False
            while i < len(args):
                if args[i] == ";":
                    break
                elif args[i] == "+":
                    batch_mode = True
                    break
                elif args[i] == "{}":
                    # fd uses {} too, but handles it automatically
                    cmd_args.append("{}")
                else:
                    cmd_args.append(args[i])
                i += 1
            i += 1  # Skip the terminator
            
            # Store exec args to add at the very end (after paths)
            if batch_mode:
                exec_args = ["-X"] + cmd_args
            else:
                exec_args = ["-x"] + cmd_args
            continue
        
        # -L (follow symlinks) → -L
        if arg == "-L":
            result.append("-L")
            i += 1
            continue
        
        # Unknown args - skip for now
        i += 1
    
    # fd requires a pattern - if none specified via -name/-iname, use "." (match all)
    # The pattern must come before paths in fd
    if not patterns:
        # No patterns specified, use "." to match all
        result.append(".")
    else:
        # Handle one or more patterns
        if len(patterns) == 1:
            # Single pattern, use directly
            result.extend(["-g", patterns[0]])
        else:
            # Multiple patterns - use brace expansion
            # Convert list of patterns to {p1,p2,p3} format
            brace_pattern = "{" + ",".join(patterns) + "}"
            result.extend(["-g", brace_pattern])
    
    # Add paths (fd takes paths after pattern/options, but before -x/-X)
    if paths:
        result.extend(paths)
    
    # Add exec args last (everything after -x/-X is treated as the command)
    if exec_args:
        result.extend(exec_args)
    
    return result
