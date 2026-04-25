# Changelog

All notable changes to this project will be documented in this file.

This project follows **Semantic Versioning (SemVer)**.

---

## [0.1.0] - 2026-04-24 - PoC Version

### Added

- Initial FastAPI backend project setup.
- PostgreSQL integration and database configuration.
- Alembic integration for schema migrations.
- GitHub Actions initial pipeline.
- Healthcheck endpoint.
- Layered architecture structure (`routers`, `services`, `repositories`, `schemas`, `models`).
- Domain-level exception system mapped to HTTP errors.
- User CRUD implementation (repository, service, router).
- Account create and retrieval logic.
- CBU persistence and unique constraint handling.
- OCR processing service for Brunbank receipt images.
- Receipt processing flow to extract and validate receipt fields.
- File persistence system using PostgreSQL `BYTEA`.
- Receipt upload integration flow.
- Balance update logic with concurrency-safe database-level operations.
- Integration and unit tests for user, account, OCR processing, and receipt upload workflows.

---
