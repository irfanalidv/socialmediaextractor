# Contributing to socialmediaextractor

Thanks for helping improve `socialmediaextractor`!

## Development setup

```bash
git clone https://github.com/irfanalidv/socialmediaextractor.git
cd socialmediaextractor
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Before opening a pull request

```bash
ruff check .          # lint
ruff format --check . # formatting
pytest                # tests
```

- Add or update tests for any behaviour change.
- Add a line to `CHANGELOG.md` under **Unreleased**.
- Keep pull requests focused: one fix or feature per PR.

## Reporting bugs and requesting features

Use the [issue templates](https://github.com/irfanalidv/socialmediaextractor/issues/new/choose).
