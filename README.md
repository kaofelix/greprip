# greprip

Transparent drop-in replacements for `grep` and `find` that use the faster Rust alternatives (`rg` and `fd`).

## Goal

LLM coding agents like [Pi](https://pi.dev) default to using `grep` and `find` because they're universal POSIX tools. But modern Rust alternatives like `ripgrep` and `fd` are significantly faster.

**greprip** solves this by providing `grg` and `fnd` commands that:
1. Accept `grep`/`find` syntax
2. Translate arguments to `rg`/`fd` equivalents
3. Execute the faster tool transparently

This gives you the speed benefits of modern tools without requiring the LLM to know about them.

## Setup with Pi

### 1. Install dependencies

```bash
# Install rg and fd (macOS)
brew install ripgrep fd

# Install greprip
uv tool install git+https://github.com/kaofelix/greprip
```

### 2. Configure Pi

Add to `~/.pi/agent/settings.json`:

```json
{
  "shellCommandPrefix": "grep() { grg \"$@\"; }; find() { fnd \"$@\"; };"
}
```

### 3. Restart Pi

Start a new session. Now when the agent runs `grep` or `find`, it transparently uses `rg`/`fd`.

Verify it's working:
```bash
type grep   # Should show: grep is a function
grep --version  # Should show: ripgrep X.X.X
```

## Supported Flags

### grg (grep → rg)

| Category | Flags |
|----------|-------|
| Basic | `-i`, `-n`, `-v`, `-w`, `-l`, `-c`, `-o`, `-h`, `-H` |
| Recursive | `-r`, `-R` (dropped - rg default) |
| Regex | `-E` (dropped - rg default), `-F`, `-P` |
| Context | `-A NUM`, `-B NUM`, `-C NUM`, `-NUM` |
| Patterns | `-e PATTERN`, `-f FILE` |
| Filters | `--include=`, `--exclude=`, `--exclude-dir=` |
| Output | `--color`, `-q`, `-s` |

### fnd (find → fd)

| Category | Options |
|----------|---------|
| Name | `-name`, `-iname` |
| Type | `-type f/d/l` |
| Depth | `-maxdepth`, `-mindepth` |
| Output | `-print`, `-print0` |
| Exclude | `! -name`, `-path ... -prune` |
| Execute | `-exec {} \;`, `-exec {} +` |
| Symlinks | `-L` |

## Direct Usage

Without Pi integration, you can use the tools directly:

```bash
grg -ri "pattern" src/       # like: grep -ri "pattern" src/
fnd . -name "*.py" -type f   # like: find . -name "*.py" -type f
```

Or add shell aliases:

```bash
alias grep='grg'
alias find='fnd'
```

## Known Differences

- `fd` doesn't include the search root directory in output (find does)
- `fd -x` runs commands in parallel by default (find -exec is sequential)

## Development

```bash
uv sync                  # Install dependencies
uv run pytest            # Run unit tests (68 tests)

# Acceptance tests
GRG="uv run grg" ./tests/acceptance/test_grg.sh  # 21 tests
FND="uv run fnd" ./tests/acceptance/test_fnd.sh  # 11 tests
```

## License

MIT
