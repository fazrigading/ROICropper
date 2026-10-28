# Contributing

Thank you for your interest in ROICropper!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/fazrigading/ROICropper.git
cd ROICropper

# Install dependencies
uv pip install -e '.[dev,cli,web]'

# Run tests
python -m pytest tests/ -v
```

## Project Structure

```
src/roicropper/   — Core crop logic (pure functions)
cli/              — Typer CLI entry point
web/              — Gradio web UI
tests/            — Unit tests
docs/             — Documentation
```

## Guidelines

- All new code must include tests in `tests/`
- Use Ruff for linting (`ruff check .`) and formatting (`ruff format .`)
- Keep the core module free of I/O side effects — it returns numpy arrays only
- CLI and web layers handle presentation; core handles logic
- Use conventional commit messages: `feat:`, `fix:`, `docs:`, `chore:`, `test:`

## Reporting Issues

Open a GitHub issue with:
- Python version and OS
- Sample image (if applicable)
- Steps to reproduce
