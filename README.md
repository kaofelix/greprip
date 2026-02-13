# greprip

Transparent drop-in replacements for `grep` and `find` that use the faster Rust alternatives (`rg` and `fd`).

## Why?

LLMs often use `grep` and `find` because they're universal. This tool lets you transparently redirect those commands to `rg` and `fd` for better performance, without the LLM needing to know about it.

## Requirements

- Python 3.12+
- [ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`)
- [fd](https://github.com/sharkdp/fd) (`fd`)

## Installation

```bash
# Install rg and fd (macOS)
brew install ripgrep fd

# Install greprip
uv tool install git+https://github.com/YOUR_USERNAME/greprip
```

## Usage

### Direct usage

```bash
grg -ri "pattern" src/       # like: grep -ri "pattern" src/
fnd . -name "*.py" -type f   # like: find . -name "*.py" -type f
```

### As transparent replacement (shell aliases)

Add to your shell config:

```bash
alias grep='grg'
alias find='fnd'
```

### With Pi (coding agent)

Add to `~/.pi/agent/settings.json`:

```json
{
  "shellCommandPrefix": "grep() { grg \"$@\"; }; find() { fnd \"$@\"; };"
}
```

Now when the agent runs `grep` or `find`, it transparently uses `grg`/`fnd`.

## Supported Flags

### grg (grep → rg)

Most common grep flags are supported:

- `-i`, `-n`, `-v`, `-w`, `-l`, `-c`, `-o`, `-h`, `-H`
- `-r`, `-R` (dropped - rg is recursive by default)
- `-E` (dropped - rg uses ERE by default)
- `-F`, `-P` (fixed strings, Perl regex)
- `-A`, `-B`, `-C`, `-NUM` (context lines)
- `-e`, `-f` (patterns)
- `--include`, `--exclude`, `--exclude-dir`
- `--color`

### fnd (find → fd)

Common find options are supported:

- `-name`, `-iname` (glob patterns)
- `-type f/d/l` (file type)
- `-maxdepth`, `-mindepth`
- `-print`, `-print0`
- `! -name` (exclude)
- `-exec {} \;` and `-exec {} +`
- `-L` (follow symlinks)

## Development

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/greprip
cd greprip
uv sync

# Run tests
uv run pytest                                    # Unit tests
GRG="uv run grg" ./tests/acceptance/test_grg.sh  # Acceptance tests
FND="uv run fnd" ./tests/acceptance/test_fnd.sh

# Install locally for development
uv pip install -e .
```

## Known Differences

- `fd` doesn't include the search root directory in output (find does)
- `fd -x` runs commands in parallel by default (find -exec is sequential)

## License

MIT
