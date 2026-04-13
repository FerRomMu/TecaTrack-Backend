# TecaTrack Backend

## Development Setup

This project uses `uv` for dependency management and `ruff` for linting and formatting.

### Prerequisites

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Setup Steps

1. Install all dependencies and create a virtual environment:

   ```bash
   uv sync
   ```

2. Activate the virtual environment:
   ```bash
   # On Windows:
   .venv\Scripts\activate
   # On Linux/macOS:
   source .venv/bin/activate
   ```

### Linting and Formatting

We use `ruff` to keep the code clean and properly formatted.

To run the linter:

```bash
ruff check .
```

To automatically fix linting errors (where possible):

```bash
ruff check --fix .
```

To format the code:

```bash
ruff format .
```

## Database Schema

[dbdiagram](https://dbdiagram.io/) or dbdiagram extension for VSCode is needed to show the schema.
