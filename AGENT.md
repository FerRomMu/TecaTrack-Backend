# CRITICAL OPERATIONAL RULES

1. **NO TERMINAL COMMANDS:** Never execute any terminal commands (pip install, uvicorn, etc.).
2. **AUTHORIZED ACTIONS:** You are only allowed to **read**, **create**, or **edit** files and directories.
3. **COMMANDS:** If a command needs to be executed, ask the user to run it instead of executing it yourself.

# CONTRIBUTION STYLE

- **Incremental Changes:** Prioritize small, atomic changes in code and database schema.
- **Avoid Bloat:** Avoid large refactors or massive file rewrites unless explicitly requested.
- **Progressive Updates:** Break complex tasks into steps and wait for feedback before continuing.

# BACKEND STACK

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic v2
- **Async:** Use async implementations when supported by stack

# CODE QUALITY STANDARDS

- **Language:** All code, comments, and documentation must be in English.
- **Typing:** Use strict typing everywhere. Avoid `Any`.
- **Structure:** Keep clear separation between:
  - routers
  - services
  - repositories
  - schemas
