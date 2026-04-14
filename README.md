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

3. Install the project in editable mode:
   ```bash
   uv pip install -e .
   ```

### Running the Application

To start the development server with hot-reload:

```bash
uv run uvicorn tecatrack_backend.main:app --reload
```
### Database Setup and Migrations (Alembic)

This project uses PostgreSQL for the database and Alembic for schema migrations.

1. Create the PostgreSQL Database:

   ```bash
   psql -U postgres -c "CREATE DATABASE tecatrack;"
   ```

2. Configure the `.env` file:
   Create a `.env` file in the root of the backend directory (`TecaTrack-Backend`) and specify your database connection details through the `DATABASE_URL` variable:
   ```env
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/tecatrack
   ```

3. Apply database migrations:
   Run the following command to create the necessary tables in your newly created database:
   ```bash
   alembic upgrade head
   ```

### Managing Migrations (For developers)

Whenever you add or modify a model in `src/tecatrack_backend/models.py`, you'll need to generate and apply a new migration:

1. **Auto-generate a migration script:**
   ```bash
   alembic revision --autogenerate -m "describe_your_changes_here"
   ```
2. **Apply the migration to the database:**
   ```bash
   alembic upgrade head
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
