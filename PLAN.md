# greprip - Project Plan

## Goal

Create transparent drop-in replacements for `grep` and `find` that translate commands to their faster Rust equivalents (`rg` and `fd`). Primary use case: LLMs often use older tools; by aliasing `grep`→`grg` and `find`→`fnd`, we get the speed benefits of modern tools without requiring the LLM to know about them.

## Architecture

- **`grg`**: Translates grep arguments → rg arguments, then executes rg
- **`fnd`**: Translates find arguments → fd arguments, then executes fd (Phase 2)

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

### Phase 1: grep → rg (`grg`)

- [x] Project setup with UV
- [x] Test fixtures
- [x] Acceptance test harness (bash)
- [x] Unit tests for translator
- [x] Basic translator implementation
- [x] CLI entry point

**Supported flags:**
- [x] `-i` (case insensitive)
- [x] `-n` (line numbers)
- [x] `-v` (invert match)
- [x] `-w` (word boundary)
- [x] `-l` (files with matches)
- [x] `-c` (count)
- [x] `-r`, `-R` (recursive - dropped, rg default)
- [x] `-E` (extended regex - dropped, rg default)
- [x] `-o`, `-h`, `-H` (pass through)
- [x] `--include=PATTERN` → `-g PATTERN`
- [x] `--exclude=PATTERN` → `-g !PATTERN`
- [x] Combined flags like `-ri`, `-rni`

**Missing flags (to add):**
- [ ] `-A NUM`, `-B NUM`, `-C NUM` (context lines)
- [ ] `-e PATTERN` (explicit pattern)
- [ ] `-f FILE` (patterns from file)
- [ ] `-q` (quiet)
- [ ] `-s` (suppress errors)
- [ ] `--color` handling
- [ ] `-F` (fixed strings)
- [ ] `-P` (Perl regex)

**Missing features:**
- [ ] `--dry-run` flag to print rg command without executing
- [ ] Better error handling

### Phase 2: find → fd (`fnd`)

- [ ] Acceptance test harness
- [ ] Unit tests
- [ ] Translator implementation
- [ ] CLI entry point

## Tech Stack

- Python 3.12+
- UV for dependency management and execution
- pytest for unit tests
- Bash for acceptance tests

## Future Considerations

- Rewrite in Rust if Python overhead becomes noticeable (unlikely for this use case)
- The acceptance tests are language-agnostic and will validate a rewrite
