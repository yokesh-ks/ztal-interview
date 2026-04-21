look for violations of the architecture at backend.md and frontend.md
look at the imports. that should quickly tell you if there are violations: hooks would have domain imports and presentation imports. repositories would have data imports and domain imports. services and use cases and services should have domain imports only.
see if imports can be better bunched through barrel export/imports
look for dependency direction regressions inside a feature. data MUST NOT import from presentation, domain MUST NOT import from presentation or data, and presentation should not reach around hooks/use cases into adapters or infrastructure.
look for presentation code consuming domain models directly when a `Ui` model should exist. hooks should map domain models to explicit UI models instead of making components do model translation inline.
look for business rules leaking into components/hooks: status-to-field rules, validation rules, payload-building rules, workflow transitions, and persistence side effects belong in domain/application code, not presentation.
look for repeated magic strings and repeated switch branches around statuses, stages, workflow names, query keys, and event names. Prefer shared enums/constants/config maps so there is one source of truth.
look for duplicated validation/error messages or duplicated rule checks across layers. if a rule already exists in domain, application/adapters should call it instead of re-encoding it.
look for repository/query-cache helpers living in the wrong layer. query keys and cache coordination used by repositories should live in data or a neutral shared module, not presentation.
look for large presentation components becoming orchestration layers. if a component is validating business rules, constructing API/domain payloads, and coordinating workflow state, that logic likely needs to move into hooks/use cases/domain helpers.

## Backend-specific violations to check

### Business logic leaking into use cases

Use cases MUST be purely procedural orchestration. Business rules — validation predicates, status transition guards, required-field rules, stage constraints, reason-string construction — belong in **domain services** (pure functions or stateless classes in `domain/services/`), not in use cases or as private module-level helpers inside use case files.

**How to spot it fast:** look for module-level private functions (`def _something(...)`) at the top of a use case file. Any such function that encodes a rule (not just wires calls) is a violation.

```python
# ❌ WRONG — business rules as private helpers in a use case file
# application/use_cases/candidates/update_candidate_use_case.py

def _is_valid_contact_field(value: str | None, field_type: str) -> bool:
    ...  # validation rule — belongs in domain/services/

def _append_missing_phone_reason(reason: str | None) -> str:
    ...  # reason-building rule — belongs in domain/services/

def _validate_required_status_tracking_fields(candidate, status, should_validate) -> None:
    if status == CandidateStatus.L2_SCHEDULED and candidate.l2_scheduled_datetime is None:
        raise ValueError(...)  # status transition guard — belongs in domain/services/

# ✅ CORRECT — domain service owns the rules; use case delegates
# domain/services/candidate_update_rules.py

def is_valid_contact_field(value: str | None, field_type: str) -> bool: ...
def append_missing_phone_reason(reason: str | None) -> str: ...
def validate_required_status_tracking_fields(candidate, status, should_validate) -> None: ...

# application/use_cases/candidates/update_candidate_use_case.py
from recruitment_service.domain.services.candidate_update_rules import (
    is_valid_contact_field,
    append_missing_phone_reason,
    validate_required_status_tracking_fields,
)
```

**Checklist for use case files:**
- No module-level `def _private_rule(...)` functions
- No inline `if status == X and field is None: raise ValueError(...)` blocks that aren't delegated to a domain service
- No inline status-to-reason string construction
- No stage/status constraint logic (e.g. "SL Screening FBP only valid in L2") defined inline — must call a domain service function
- Domain service functions must have their own unit tests in `tests/unit/domain/services/`

## Frontend-specific violations to check

### Direct Storage Access in Hooks/Components
Hooks and components MUST NOT directly access `sessionStorage` or `localStorage` for business state. Storage operations should be encapsulated in:
1. Domain services (for business logic with storage)
2. Repositories (data layer) - for persistence operations
3. Use cases - that call repository/service methods

**Exception:** Pure UI state (scroll position, accordion expansion) MAY access sessionStorage directly in components since it's presentation-layer state, not business data.

```typescript
// ❌ WRONG - Hook directly accessing sessionStorage for business state
export function useProcessingState(jobId: string) {
  const [progress, setProgress] = useState<ProcessingProgress | null>(null);

  useEffect(() => {
    // Direct sessionStorage access for business state - VIOLATION
    const savedState = sessionStorage.getItem(STORAGE_KEY);
    if (!savedState) {
      setProgress(null);
      return;
    }
    // ...
  }, [jobId]);
}

// ✅ CORRECT - Use existing domain service/repository pattern
export function useProcessingState(jobId: string) {
  // DI-injected factory creates state manager with proper storage encapsulation
  const createStateManager = useInjectedResumeProcessingStateManagerFactory();
  const stateManager = useMemo(() => createStateManager(() => jobId), [createStateManager, jobId]);

  useEffect(() => {
    // State manager encapsulates sessionStorage access
    stateManager.startPolling({ jobId }, (state) => setRecoveredState(state));
  }, [stateManager, jobId]);
}

// ✅ OK - Pure UI state in component (scroll position)
function KanbanBoard() {
  useEffect(() => {
    // Scroll position is pure UI state, not business data
    const scrollPos = sessionStorage.getItem(`scroll-${id}`);
    if (scrollPos) container.scrollTo({ left: parseInt(scrollPos) });
  }, []);
}
```

### React Query in Components
Components MUST NOT use `useQueryClient` directly. Query cache operations (invalidation, updates) should be encapsulated in:
1. Repository methods (data layer) - where `useQueryClient` is allowed
2. Use cases (domain layer) - that call repository methods
3. Presentation hooks - that call use cases

```typescript
// ❌ WRONG - Component using useQueryClient directly
import { useQueryClient } from '@tanstack/react-query';

function MyComponent() {
  const queryClient = useQueryClient();

  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ['candidates', jobId] });
  }, [jobId]);
}

// ✅ CORRECT - Component uses a hook that calls a use case
import { useInvalidateCandidatesCache } from '../../index';

function MyComponent() {
  const { invalidateCandidatesCache } = useInvalidateCandidatesCache();

  useEffect(() => {
    if (jobId) {
      invalidateCandidatesCache(jobId);
    }
  }, [jobId, invalidateCandidatesCache]);
}
```

This ensures:
- Components remain thin (no business/data logic)
- Cache operations are testable via DI mocks
- Query key management is centralized in the data layer
