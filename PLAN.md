# greprip - Project Plan

## Goal

Create transparent drop-in replacements for `grep` and `find` that translate commands to their faster Rust equivalents (`rg` and `fd`). Primary use case: LLMs often use older tools; by aliasing `grep`→`grg` and `find`→`fnd`, we get the speed benefits of modern tools without requiring the LLM to know about them.

## Architecture

- **`grg`**: Translates grep arguments → rg arguments, then executes rg
- **`fnd`**: Translates find arguments → fd arguments, then executes fd

Separate entry points so users can alias each independently:
```bash
alias grep='grg'
alias find='fnd'
```

## Testing Strategy

Two levels of tests:

1. **Acceptance tests (bash)** - Language-agnostic, survive a rewrite
   - Run grep/find with various args on test fixtures
   - Run grg/fnd with same args
   - Compare outputs (same matching lines, not byte-exact)

2. **Unit tests (Python/pytest)**
   - Test argument translation logic in isolation
   - Cover flag mappings and edge cases

## Progress

### Phase 1: grep → rg (`grg`) ✅ COMPLETE

- [x] Project setup with UV
- [x] Test fixtures
- [x] Acceptance test harness (bash)
- [x] Unit tests for translator
- [x] Basic translator implementation
- [x] CLI entry point

**Supported flags:**
- [x] `-i`, `--ignore-case` (case insensitive)
- [x] `-n`, `--line-number` (line numbers)
- [x] `-v`, `--invert-match` (invert match)
- [x] `-w`, `--word-regexp` (word boundary)
- [x] `-l`, `--files-with-matches` (files with matches)
- [x] `-c`, `--count` (count)
- [x] `-o`, `--only-matching` (only matching)
- [x] `-h`, `--no-filename` (no filename)
- [x] `-H`, `--with-filename` (with filename)
- [x] `-r`, `-R`, `--recursive` (recursive - dropped, rg default)
- [x] `-E`, `--extended-regexp` (extended regex - dropped, rg default)
- [x] `-G`, `--basic-regexp` (basic regex - dropped)
- [x] `-F`, `--fixed-strings` (fixed strings)
- [x] `-P`, `--perl-regexp` (Perl regex)
- [x] `-q`, `--quiet`, `--silent` (quiet mode)
- [x] `-s` (suppress errors → `--no-messages`)
- [x] `-A NUM`, `--after-context=NUM` (after context)
- [x] `-B NUM`, `--before-context=NUM` (before context)
- [x] `-C NUM`, `--context=NUM` (context both)
- [x] `-NUM` shorthand (e.g., `-3` → `-C 3`)
- [x] `-e PATTERN`, `--regexp=PATTERN` (explicit pattern)
- [x] `-f FILE`, `--file=FILE` (patterns from file)
- [x] `-m NUM`, `--max-count=NUM` (max matches)
- [x] `--include=PATTERN` → `-g PATTERN`
- [x] `--exclude=PATTERN` → `-g !PATTERN`
- [x] `--exclude-dir=PATTERN` → `-g !PATTERN/`
- [x] `--color`, `--color=always/never/auto`
- [x] Combined flags like `-ri`, `-rni`

### Phase 2: find → fd (`fnd`) ✅ COMPLETE

- [x] Acceptance test harness
- [x] Unit tests
- [x] Translator implementation
- [x] CLI entry point

**Supported options:**
- [x] `-name PATTERN` → `-g PATTERN` (glob pattern)
- [x] `-iname PATTERN` → `-i -g PATTERN` (case insensitive)
- [x] `-type f/d/l` → `-t f/d/l` (file type)
- [x] `-maxdepth N` → `-d N` (max depth)
- [x] `-mindepth N` → `--min-depth N` (min depth)
- [x] `-print` (implicit, no-op)
- [x] `-print0` → `-0` (null-separated)
- [x] `! -name PATTERN` → `-E PATTERN` (exclude)
- [x] `-path PATTERN -prune` → `-E PATTERN` (exclude path)
- [x] Hidden files included by default (`-H` flag added)

**Known differences:**
- `find` includes the search root in output, `fd` does not (acceptable for LLM use case)

## Tech Stack

- Python 3.12+
- UV for dependency management and execution
- pytest for unit tests
- Bash for acceptance tests

## Future Considerations

- Rewrite in Rust if Python overhead becomes noticeable (unlikely for this use case)
- The acceptance tests are language-agnostic and will validate a rewrite
