# Core Module

The **app/core** directory contains the core business logic and data representation components of the Recipe App. This layer is responsible for managing data models, data transfer objects (DTOs), database interactions, repositories, services, and utility functions.

## Directory Structure

```
app/core/
├── database/      # Database schema definitions, migrations, and session management
├── dtos/          # Data Transfer Objects for request/response validation
├── models/        # Domain models and ORM mappings
├── repos/         # Repository layer for CRUD operations and data access
├── services/      # Business logic implementations and orchestrations
└── utils/         # Core utility functions and helpers used across the core layer
```

## Packages and Responsibilities

### database
- Defines SQLAlchemy models and Alembic migration scripts.
- Manages database sessions, engines, and connection pooling.
- Provides functions to initialize and migrate the database schema.

### dtos
- Contains Pydantic models for input validation and response formatting.
- Ensures data consistency and type safety at service boundaries.
- Centralizes DTO definitions used by services and API layers.

### models
- Implements domain models that represent application entities.
- Defines ORM mappings to database tables.
- Encapsulates business attributes and behaviors of entities.

### repos
- Provides a repository pattern abstraction for CRUD operations.
- Contains classes or functions to interact with the database at a low level.
- Decouples data access logic from business logic in services.

### services
- Implements business rules and orchestrates workflows.
- Invokes repository methods and applies transformations using models and DTOs.
- Contains core application functionality such as recipe management, shopping list operations, and more.

### utils
- Houses helper functions, converters, and shared utilities.
- Includes common error handling, logging helpers, and formatting utilities.
- Supports DRY principles by preventing code duplication across packages.

## Getting Started

1. Ensure dependencies are installed via `pip install -r requirements.txt`.
2. Initialize or migrate the database by running:
   ```powershell
   alembic upgrade head
   ```
3. Review and run unit tests located under `tests/core/` to verify core functionality.

## Contribution Guidelines

- Add new feature logic under the appropriate subpackage (e.g., service, repo, model).
- Define or update DTOs in `dtos/` when new request/response schemas are needed.
- Write accompanying unit tests in `tests/core/` for any new or modified code.
- Follow the coding style outlined in the project's style guide.

---
*Last updated: July 6, 2025*
