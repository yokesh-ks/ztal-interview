Create, Update, or Fix a Backend Feature

$ARGUMENTS

# Architecture

app/
├── main.py
├── container.py              # API DI container
├── worker_container.py       # Worker DI container (if service has Celery workers)
├── server/
│   ├── http_server.py
│   ├── router.py
│   ├── middleware.py
│   ├── exception_handlers.py
│   └── lifespan.py
│
├── adapters/
│   ├── inbound/
│   │   ├── cli/
│   │   │   └── user_cli.py
│   │   ├── http/
│   │   │   ├── v1/
│   │   │   │   ├── routes/
│   │   │   │   │   ├── user_routes.py
│   │   │   │   │   ├── generic_routes.py
│   │   │   │   │   └── ...
│   │   │   │   ├── schemas/
│   │   │   │   │   ├── user_schemas.py
│   │   │   │   │   └── ...
│   │   │   │   ├── mappers/
│   │   │   │   │   ├── user_mappers.py
│   │   │   │   │   └── ...
│   │   │   │   └── __init__.py
│   │   │   └── ...
│   │   └── consumers/
│   │       └── kafka_consumer.py
│   │
│   └── outbound/
│       ├── db/
│       │   ├── models/
│       │   │   ├── user_row.py
│       │   │   └── base.py
│       │   ├── user_repository_sql.py
│       │   ├── db_mappers.py
│       │   └── engine.py
│       │
│       ├── external/
│       │   ├── stripe/
│       │   │   ├── stripe_client.py
│       │   │   ├── stripe_models.py
│       │   │   └── stripe_mappers.py
│       │   └── sendgrid/
│       │       └── sendgrid_email_sender.py
│       │
│       └── cache/
│           └── redis_cache.py
│
├── application/
│   └── use_cases/
│       ├── create_user.py
│       ├── get_user.py
│       └── update_user.py
│
├── domain/
│   ├── models/
│   │   └── user.py
│   ├── services/
│   │   └── user_rules.py
│   └── ports/
│       ├── user_repository_port.py
│       └── payment_gateway_port.py
│
├── common/
│   ├── utils/
│   │   ├── string_utils.py
│   │   └── date_utils.py
│   └── exceptions/
│       ├── domain_errors.py
│       └── api_errors.py
│
└── config/
    ├── settings.py
    └── env_loader.py

# Architecture Rules

# 1. Test-Driven Development (TDD)

**TDD is mandatory for all backend work.** Follow the Red-Green-Refactor cycle:

### The TDD Workflow

1. **RED: Write a failing test first**
   ```bash
   # Run the test to confirm it fails
   .venv/bin/pytest tests/unit/<test_file>.py::<test_name> -v
   ```

2. **GREEN: Write minimal code to make the test pass**
   - Only write enough code to pass the test
   - Don't over-engineer or add extra features

3. **REFACTOR: Clean up while keeping tests green**
   - Improve code structure
   - Remove duplication
   - Run tests after each refactor

### Test Structure

```python
# tests/unit/<layer>/<test_file>.py
from unittest.mock import Mock, create_autospec
from service.domain.models import SomeDomainModel
from service.domain.ports import SomePort

class TestFeatureName:
    """Tests for [feature description]."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        """Create mock using create_autospec (NOT AsyncMock/MagicMock)."""
        return create_autospec(SomePort, instance=True)

    @pytest.mark.asyncio
    async def test_<action>_<expected_outcome>(self, mock_repo: Mock):
        """Test that [expected behavior]."""
        # Arrange - return domain models, NOT dicts
        mock_repo.some_method.return_value = SomeDomainModel(
            id=uuid4(),
            name="test",
        )
        use_case = SomeUseCase(mock_repo)

        # Act
        result = await use_case.execute(input_data)

        # Assert
        assert result == expected_outcome
        mock_repo.some_method.assert_called_once_with(expected_args)
```

### When to Write Tests

| Scenario | Test First? | Example |
|----------|-------------|---------|
| New feature | Yes | New use case, new domain service |
| Bug fix | Yes | Reproduce bug with failing test first |
| Refactoring | No (tests exist) | Keep existing tests green |
| Updating existing feature | Update test first | Modify test to expect new behavior |

### Test File Organization

```
tests/
├── unit/
│   ├── domain/
│   │   └── services/         # Domain service tests
│   ├── use_cases/            # Use case tests
│   └── adapters/
│       └── outbound/         # Repository/adapter tests
├── integration/              # Tests with real dependencies
└── conftest.py               # Shared fixtures
```

### What to Test at Each Layer

| Layer | What to Test | Mocking |
|-------|--------------|---------|
| Use Cases | Orchestration logic, port calls | Mock all ports |
| Domain Services | Business rules, pure logic | No mocks needed |
| Outbound Adapters | Data mapping, query building | Mock external deps |

### Before Adding New Tests

- **Check if an existing test should be updated** instead of creating a new one
- Avoid duplicate tests that cover the same logic
- Group related tests in the same test class

---

# 2. Backend Architecture Layers
The backend follows **Hexagonal Architecture**, using four main layers:

- **Server** — FastAPI application, HTTP server, middleware, exception handlers, lifespan
- **Container**
  - Dependency injection wiring
  - Maps ports → outbound adapters
  - Maps use cases → inbound adapters
  - Constructs singletons (DB engine, clients)
- **Inbound Adapters** — HTTP controllers, DTOs, validation
- **Application** — use cases, orchestration
- **Domain** — entities, domain services, ports
- **Outbound Adapters** — DB, external APIs, message brokers

**Dependency direction:**
`Server → Inbound → Application → Domain → Outbound`

---

# 3. Server Layer

The server layer handles HTTP server setup and configuration. It should be split into 4 files:

```
server/
├── __init__.py          # Exports create_app, lifespan, configure_cors, register_routes
├── http_server.py       # Clean app factory - orchestrates lifespan, middleware, routes
├── router.py            # Registers v1_router (and future v2_router)
├── middleware.py        # CORS and other middleware configuration
└── lifespan.py          # Application lifecycle management (startup/shutdown)
```

### http_server.py
Factory pattern for FastAPI app creation:
```python
def create_app() -> FastAPI:
    app = FastAPI(**get_fastapi_config(...), lifespan=lifespan)
    configure_cors(app)
    register_routes(app)
    return app
```

### router.py
Imports the aggregated v1 router:
```python
from service.adapters.inbound.http.v1 import router as v1_router

def register_routes(app: FastAPI) -> None:
    app.include_router(v1_router)  # Future: add v2_router
```

### middleware.py
Separate middleware configuration:
```python
def configure_cors(app: FastAPI) -> None:
    app.add_middleware(CORSMiddleware, ...)
```

### lifespan.py
Async context manager for startup/shutdown:
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup logic
    yield
    # Shutdown logic
```

---

# 4. Route Organization & API Versioning

Routes should be organized with a v1 aggregation layer for future API versioning support:

```
adapters/inbound/http/v1/
├── __init__.py          # Aggregates all v1 routes into single v1_router
└── routes/
    ├── __init__.py      # Exports individual routers (health_router, user_router, etc.)
    ├── health_routes.py
    └── *_routes.py
```

### routes/__init__.py
Export individual routers:
```python
from .health_routes import router as health_router
from .user_routes import router as user_router

__all__ = ["health_router", "user_router"]
```

### v1/__init__.py
Aggregate all v1 routers:
```python
from fastapi import APIRouter
from .routes import health_router, user_router

router = APIRouter()
router.include_router(health_router)
router.include_router(user_router)

__all__ = ["router"]
```

This pattern enables easy addition of v2 APIs:
```python
# In server/router.py
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

---

# 5. Models & Naming Conventions

### Inbound Models
- End with `DTO`
- Examples:
  - `CreateUserRequestDTO`
  - `UserResponseDTO`

### Application Layer Models
- Generally none; use cases operate on domain models.

### Domain Models
- **No suffix**
- Canonical business objects
- Examples:
  - `User`
  - `Order`
### Domain Enums
- Define enums in `domain/types/` and import them into domain models or adapters as needed.

### Outbound Adapter Models
- Must indicate infrastructure type:
  - DB: `UserRow`, `UserRecord`, `UserTable`
  - External API: `StripeChargeResponse`, `S3FileMetadata`

---

# 6. Mapping Between Layers
- All conversions must use explicit mapper functions.
- Valid conversions:
  - Inbound DTO ↔ Domain model
  - Domain model ↔ Outbound model
- No layer may directly use another layer’s model types.
- Mapper placement:
  - Inbound mappers → inbound layer
  - Outbound mappers → outbound layer

---

# 7. Inbound Adapter Layer
Contains:
- FastAPI routers
- Request/response DTOs
- Validation logic
- DTO → Domain mappers

Rules:
- No business logic
- Each endpoint maps **1:1** to an application use case
- Never calls repositories or outbound implementations directly

---

# 8. Application Layer
Contains:
- Use cases (application services)
- Application-level orchestration

Rules:
- Use cases have one clear responsibility
- Orchestrate by calling domain services or ports
- Purely procedural; no domain rules or infrastructure code

This layer may be merged into the domain layer for small projects.

---

# 9. Domain Layer
Contains:
- Domain models (entities)
- Domain services (business logic)
- Ports (interfaces required from outbound adapters). This should be always ABC--not protocols

Rules:
- No framework-specific code
- No outbound implementations
- Domain defines *what* it needs, not *how* implementations work
- No TYPE_CHECKING usages. Implement properly so that there are no circular imports and TYPE_CHECKING usage needed.

---

# 10. Outbound Adapter Layer
Contains:
- Repository implementations
- External API clients
- Event publishers
- Outbound models (SQL rows, API payloads)
- Domain ↔ Outbound mappers

Rules:
- Implements domain ports
- Knows nothing about inbound or application layers
- Never write raw SQL queries; use SQLAlchemy Core instead

### SQLModel Query Patterns

When writing SQLAlchemy select statements with SQLModel, **always wrap column references in `col()`** for Pylance type checking:

```python
from sqlmodel import col

# GOOD: Pylance can infer types correctly
stmt = (
    select(
        col(UserRow.id),
        col(UserRow.email),
        col(RoleRow.name).label("role_name"),
    )
    .select_from(UserOrgMembershipRow)
    .join(UserRow, col(UserOrgMembershipRow.user_id) == col(UserRow.id))
    .where(col(UserOrgMembershipRow.organization_id) == org_id)
    .order_by(col(UserRow.created_at).desc())
)

# BAD: Pylance shows type errors, though runtime works
stmt = (
    select(UserRow.id, UserRow.email, RoleRow.name.label("role_name"))
    .join(UserRow, UserOrgMembershipRow.user_id == UserRow.id)
    .where(UserOrgMembershipRow.organization_id == org_id)
)
```

**Where to use `col()`:**
- All column references in `select()`
- Join conditions on both sides
- Where clause comparisons
- Order by clauses
- Group by clauses

---

# 11. Database Migrations (Alembic)

Rules:
- **Always update SQLModels first**, then autogenerate migrations
- Never manually create migration files
- Use `alembic revision --autogenerate -m "description"` to generate migrations
- Review autogenerated migrations before applying them
- Migration files should be committed with the corresponding model changes

### Adding New Tables

When adding a new SQLModel table, you must update `alembic/env.py` for autogenerate to detect it:

1. Create the model in `adapters/outbound/db/models/`
2. Export it from `adapters/outbound/db/models/__init__.py`
3. Import it in `alembic/env.py` (add to the imports from `adapters.outbound.db.models`)
4. If using filtered metadata (like auth-service), add the table name to the filter list in `env.py`
5. Then run `alembic revision --autogenerate -m "description"`

**Why this is needed:** Alembic autogenerate only detects models that are imported into `env.py` and registered in `target_metadata`. Without these steps, autogenerate produces an empty migration with just `pass`.

### Standard Workflow

1. Update the SQLModel in `adapters/outbound/db/models/`
2. Run `alembic revision --autogenerate -m "description of change"`
3. Review the generated migration file
4. Apply with `alembic upgrade head`

---

# 12. Container Layer
Contains:
- FastAPI app initialization
- CORS middleware
- DI bindings (ports → implementations)
- Router registration
- Startup/shutdown hooks

This layer composes the entire application.

- Inbound routes should pull use cases from the container at call time (e.g., `get_*_use_case()`), not via FastAPI dependency injection.
- Use `binder.bind()` for all bindings; avoid `@provider` methods.
- Use `@inject` decorator on classes that need constructor injection.

### Dependency Injection Patterns

Use `binder.bind()` in the `configure()` method of your Module class:

```python
from injector import Binder, CallableProvider, Injector, InstanceProvider, Module, singleton

class ServiceModule(Module):
    def configure(self, binder: Binder) -> None:
        # Port → Adapter bindings (interface to implementation)
        binder.bind(UserRepositoryPort, to=PostgreSQLUserRepository, scope=singleton)
        binder.bind(EmailSenderPort, to=SendGridEmailSender, scope=singleton)

        # Singleton bindings for services/use cases (ensures single instance reuse)
        # Required for @inject-decorated classes to be singletons
        binder.bind(UserService, scope=singleton)
        binder.bind(CreateUserUseCase, scope=singleton)

        # Pre-constructed instances (for infrastructure with complex setup)
        db_factory = self._create_db_factory()
        binder.bind(DatabaseConnectionFactory, to=InstanceProvider(db_factory))

        # Lazy instantiation (for heavy deps that shouldn't load at module import)
        binder.bind(
            HeavyDependencyPort,
            to=CallableProvider(self._create_heavy_dependency),
        )

    def _create_heavy_dependency(self) -> HeavyDependencyPort:
        """Lazy import to avoid loading heavy deps at container creation."""
        from some_module import HeavyDependencyAdapter
        return HeavyDependencyAdapter()
```

### Binding Types

| Pattern | When to Use |
|---------|-------------|
| `binder.bind(Port, to=Adapter, scope=singleton)` | Port → adapter mappings |
| `binder.bind(Service, scope=singleton)` | Services/use cases with `@inject` |
| `binder.bind(Class, to=InstanceProvider(instance))` | Pre-constructed infrastructure |
| `binder.bind(Port, to=CallableProvider(factory))` | Lazy loading heavy dependencies |

### Important Rules

1. **Singleton bindings are required** for services and use cases to ensure single instance reuse. Without `binder.bind(Service, scope=singleton)`, the injector creates new instances on every resolution.

2. **Use `CallableProvider` for lazy imports** when a dependency has heavy module-level imports (like `pydantic_ai`, `openpyxl`). The factory method delays the import until first resolution.

3. **Avoid `@provider` methods** - use `binder.bind()` with `InstanceProvider` or `CallableProvider` instead.

4. **Import from barrel files** when available to keep imports clean:
   ```python
   # GOOD: Import from barrel
   from service.adapters.outbound import PostgreSQLUserRepository, EmailSender
   from service.domain.ports import UserRepositoryPort, EmailSenderPort
   from service.application.use_cases import CreateUserUseCase, GetUserUseCase

   # AVOID: Deep imports
   from service.adapters.outbound.db.repositories.user_repository import PostgreSQLUserRepository
   ```

### Services with Celery Workers

For services with separate API and worker processes:

- **`container.py`** — API container (async use cases, no heavy deps)
- **`worker_container.py`** — Worker container (sync use cases, lazy imports heavy deps)

Worker containers should use `CallableProvider` for dependencies that require heavy imports (like ML libraries, Excel generators) to avoid loading them when the module is imported:

```python
# In worker_container.py - lazy load heavy deps
def configure(self, binder: Binder) -> None:
    # ... other bindings ...

    # Heavy dependency - use CallableProvider for lazy import
    binder.bind(
        WorkModePreferencePort,
        to=CallableProvider(self._create_work_mode_adapter),
    )

def _create_work_mode_adapter(self) -> WorkModePreferencePort:
    """Lazy import to avoid pydantic_ai at module load."""
    from service.adapters.outbound.external.work_mode import WorkModeAdapter
    return WorkModeAdapter()
```

---

# 13. Utils vs Helpers

### Utils
- Pure, dependency-free functions
- Examples: hashing, string formatting, date utilities

### Helpers
- Adapter-specific or infrastructure-aware helpers
- Must live inside an adapter (never in domain)
- Examples: SQL pagination helper, HTTP retry wrapper

---

# 14. Commonly used libraries
- Pydantic for adapter layer models
- dataclasses for the other layers

# 15. Type Safety
- Never use `dict` or `Any` as workarounds for type issues
- Define explicit Pydantic models or dataclasses or SQLModels (depending on the layer) with proper field types
- Use `TypedDict` when a dictionary structure is truly needed
- Never use forward references (quoted strings like `"ClassName"`) in type annotations; define types before use or restructure to avoid circular dependencies

### Port Return Types (Critical)
**Ports are the type safety boundary** between domain and adapters. Port methods must:
- Return domain models (dataclasses), not `dict` or raw database types
- Accept domain models or primitives as parameters, not `dict`
- Never expose infrastructure details (SQL rows, API responses) through the port interface

```python
# BAD: Port returns dict - violates type safety at the boundary
class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_user_permissions(self, user_id: UUID) -> dict[str, Any]: ...

# GOOD: Port returns domain model - enforces type safety
class UserRepositoryPort(ABC):
    @abstractmethod
    async def get_user_permissions(self, user_id: UUID) -> UserPermissions: ...
```

The adapter implementation handles the mapping from infrastructure types to domain models:
```python
# In PostgreSQLUserRepository (outbound adapter)
async def get_user_permissions(self, user_id: UUID) -> UserPermissions:
    row = await self._fetch_permissions(user_id)  # Returns dict from SQL
    return UserPermissions(  # Convert to domain model before returning
        roles=row["roles"],
        permissions=row["permissions"],
    )
```

---

# 16. Avoid Magic Values
- Use named constants for repeated literals (strings, numbers, etc.)
- Place constants in the relevant domain model or a constants module

# 17. Model Placement
- Define models only in their designated layer directories (`models/`, `schemas/`).
- Never define models inline or locally within use cases, services, or adapter files.

### Use Case Input/Result Models
Use case input and result dataclasses must be defined in `domain/models/`, NOT inline in use case files:

```python
# BAD: Defining models inline in use case file
# application/use_cases/interviews/execute_interview_evaluation_use_case.py
@dataclass
class InterviewEvaluationInput:  # Don't define here!
    processing_id: UUID
    ...

@dataclass
class InterviewEvaluationResult:  # Don't define here!
    success: bool
    ...

# GOOD: Define in domain/models/ and import
# domain/models/interview_evaluation.py
@dataclass
class InterviewEvaluationInput:
    """Input for interview evaluation workflow."""
    processing_id: UUID
    ...

@dataclass
class InterviewEvaluationResult:
    """Result of interview evaluation workflow."""
    success: bool
    ...

# application/use_cases/interviews/execute_interview_evaluation_use_case.py
from recruitment_service.domain.models import (
    InterviewEvaluationInput,
    InterviewEvaluationResult,
)
```

**Why this matters:**
- Models can be imported by other modules (tasks, tests) without importing the use case
- Avoids circular imports
- Keeps use case files focused on orchestration logic
- Makes models discoverable via the domain models barrel file

---

# 18. Testing with Mocks

Always use `create_autospec` when mocking ports/ABCs:

```python
from unittest.mock import create_autospec

# GOOD: Raises AttributeError if code calls nonexistent methods
mock_repo = create_autospec(UserRepositoryPort)

# BAD: Silently accepts any method call, hiding bugs when interfaces change
mock_repo = MagicMock()
```

This catches bugs when method signatures change (e.g., `publish_event` → `publish_event_sync`).

### Mock Return Values Must Use Domain Models

When mocking port methods, return domain models (dataclasses) not dicts:

```python
# BAD: Mock returns dict - tests pass but production fails
mock_repo.get_role_by_id.return_value = {
    "id": role_id,
    "name": "admin",
    "organization_id": org_id,
}

# GOOD: Mock returns domain model - matches actual port behavior
from service.domain.models import RoleInfo

mock_repo.get_role_by_id.return_value = RoleInfo(
    id=role_id,
    name="admin",
    organization_id=org_id,
    permissions=["read", "write"],
    user_count=5,
    created_at=datetime.now(UTC),
)
```

This ensures tests validate how code actually uses the returned data (attribute access vs dict subscripting).

---

# 19. Completion Checklist

Before considering a task complete, verify:

- [ ] All new code follows the hexagonal architecture pattern
- [ ] Tests are written and passing
- [ ] No linting errors (run `ruff check`)
- [ ] No circular imports
- [ ] Mappers exist for all layer boundary crossings
- [ ] DTOs are used in inbound adapters (not domain models)
- [ ] Ports are ABCs in the domain layer
- [ ] **Port methods return domain models, not `dict` or `Any`**
- [ ] Use cases only depend on ports, not implementations
- [ ] No TYPE_CHECKING imports (fix circular imports properly)
- [ ] No duplicate models created (checked common first)
- [ ] Models imported from canonical locations (not from use cases)
- [ ] Imports organized: stdlib → third-party → domain → application → adapters

After completing the task, provide a summary:

```
## Task Summary

### Files Modified
- `path/to/file1.py` - [description of change]
- `path/to/file2.py` - [description of change]

### Files Created
- `path/to/new_file.py` - [purpose]

### Tests
- `path/to/test.py::test_name` - [what it tests]

### Status
- Tests: PASSED/FAILED
- Lint: PASSED/FAILED
- Architecture: COMPLIANT/VIOLATIONS
```

### Final Cleanup Commands
After completing the task, run these commands to fix linting, formatting, and type checking:
```bash
cd backend/<service>
uv run ruff check . --fix --unsafe-fixes
uv run ruff format .
uv run pyright
```

---

# 20. Pre-Implementation Checks

**IMPORTANT:** Before creating new models or modifying existing ones, run these checks:

### 1. Check for existing models in `common/` package first
```bash
grep -r "class.*Row\|class.*Model" backend/common/src --include="*.py"
```
If model exists in common, import it instead of creating a new one.

### 2. Check for duplicates across services
```bash
grep -r "class YourModelName" backend/*/src --include="*.py"
```
If found elsewhere, consider hoisting to common or importing from there.

### 3. Verify import sources
- Domain models should come from `domain/models/` or `common.domain.models`
- Row models from `adapters/outbound/db/models/` or `common.adapters.outbound.db.models`
- **NEVER** import models from `use_cases/` files
- **NEVER** import types from files that also import from the current file

### 4. Check for TYPE_CHECKING usage
```bash
grep -n "TYPE_CHECKING" backend/<service>/src --include="*.py"
```
Any match indicates a circular import that should be fixed properly by restructuring.

---

# 21. Import Organization

Imports should be organized in this order, with blank lines between groups:

```python
# 1. Standard library
import os
import sys
from datetime import datetime
from typing import Optional

# 2. Third-party packages
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

# 3. Domain layer (from same service or common)
from service.domain.models import User
from service.domain.ports import UserRepositoryPort
from common.domain.models import BaseEntity

# 4. Application layer
from service.application.use_cases import CreateUserUseCase

# 5. Adapter layer
from service.adapters.outbound.db.models import UserRow

# 6. Config
from service.config import settings
```

**Rules:**
- Never mix import groups
- Use absolute imports, not relative (except within the same package)
- Avoid `from x import *`

---

# 22. Barrel File Usage

Use `__init__.py` files to create clean public APIs for packages:

### Domain Models
```python
# domain/models/__init__.py
from .user import User
from .order import Order

__all__ = ["User", "Order"]
```

### Domain Ports
```python
# domain/ports/__init__.py
from .user_repository_port import UserRepositoryPort
from .payment_gateway_port import PaymentGatewayPort

__all__ = ["UserRepositoryPort", "PaymentGatewayPort"]
```

### Benefits
```python
# Instead of:
from service.domain.models.user import User
from service.domain.models.order import Order

# Use:
from service.domain.models import User, Order
```

**Rules:**
- Every package directory should have an `__init__.py`
- Export only the public API
- Use `__all__` to be explicit about exports
- Import from barrel files when available

---

# 23. Service Infrastructure

When creating a new service or modifying service structure, ensure infrastructure files are updated:

### 1. Dockerfile (`backend/<service>/Dockerfile`)
- Update if new dependencies added to pyproject.toml
- Verify COPY paths match service structure
- Check health endpoint matches actual route

### 2. Docker Compose (`backend/compose.dev.yaml`)
- Add service entry if new service
- Verify port mappings don't conflict
- Check environment variables match settings.py

### 3. Kubernetes Manifest (`infra/k8s/base/deployments/<service>.yaml`)
- Update if new env vars, ports, or resources needed
- Verify referenced ConfigMaps/Secrets exist
- Check `kustomization.yaml` includes new resources

### 4. Validation Commands
```bash
# Validate docker compose syntax
docker compose -f backend/compose.dev.yaml config --quiet

# Validate kubernetes manifest
kubectl apply --dry-run=client -f infra/k8s/base/deployments/<service>.yaml
```

**NOTE:** For cross-service infrastructure (shared ConfigMaps, networking, secrets), use the `/infra` skill instead.
