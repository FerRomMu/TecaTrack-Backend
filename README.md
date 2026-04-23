# TecaTrack Backend

<p align="center">
  <img src=".github/assets/app-icon.png" alt="TecaTrack Logo" width="350"/>
</p>

## About the Project

TecaTrack is an app for managing receipts and transactions using OCR technology. Currently in a Proof of Concept (PoC) phase. The core functionality revolves around extracting data from physical receipts and accurately mapping it to user accounts and transaction records.

### Key Features

- **User Management:** Create and manage users,with validation for Argentine CUILs.
- **OCR Processing:** Receive, validate, and extract structured data from Brunbank's receipts images.
- **Transaction Management:** Mapping extracted OCR data to valid transaction entities, linking them to users' bank accounts.
- **File Persistence:** Upload on binary storage users' receipts images.

## Project Architecture

This project uses a source layout to avoid import issues. It has a layered architecture to ensure separation of concerns and maintainability:

- `src/tecatrack_backend/core/`: Configuration, database setup, and centralized exception handling.
- `src/tecatrack_backend/models.py`: SQLAlchemy database models.
- `src/tecatrack_backend/schemas/`: Pydantic models for request/response validation.
- `src/tecatrack_backend/repositories/`: Data access layer (database queries, file storage operations).
- `src/tecatrack_backend/services/`: Core business logic (OCR mapping, validation rules).
- `src/tecatrack_backend/routers/`: API endpoints and network layer.
- `src/tecatrack_backend/infraestructure/`: Infrastructure layer (OCR).

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

This project uses PostgreSQL for the database and Alembic for schema migrations. It leverages asynchronous database connections using the `asyncpg` driver.

1. Create the PostgreSQL Databases (Main and Test):

   ```bash
   # Create the main database
   psql -U postgres -c "CREATE DATABASE tecatrack;"
   # Create the test database
   psql -U postgres -c "CREATE DATABASE tecatrack_test;"
   ```

2. Configure the `.env` file:
   Copy the `.env-example` file to create your own `.env` file in the root directory. Specify your database connection details using the `DATABASE_URL` and `TEST_DATABASE_URL` variables.

   ```bash
   # On Windows:
   copy .env-example .env
   # On Linux/macOS:
   cp .env-example .env
   ```

   Example `.env` content:

   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/tecatrack
   TEST_DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/tecatrack_test
   ```

3. Apply database migrations:
   Run the following command to create the necessary tables in your main database:
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

### Testing

We use `pytest` along with `pytest-asyncio` for testing.

1. Make sure your `TEST_DATABASE_URL` is specified in your `.env` file.
2. Run the tests:

   ```bash
   uv run pytest
   ```

## Database Schema

The entity-relationship diagram for the application's database is available below:

![Database Schema](doc/db-schema.png)

_(You can also use the [dbdiagram](https://dbdiagram.io/) extension for VSCode with the `doc/poc-datamodel.dbml` file to view it in a more interactive way)_

> [!NOTE]
> At the PoC stage, the schema is already being created, but the application only uses the `users`, `accounts`, and `files` tables.
