Create, update or fix a frontend feature

$ARGUMENTS

# Architecture Rules

## 1. Test-Driven Development (TDD)

**TDD is mandatory for all frontend work.** Follow the Red-Green-Refactor cycle:

### The TDD Workflow

1. **RED: Write a failing test first**
   ```bash
   # Run the test to confirm it fails
   npm test -- <test_file> --run
   ```

2. **GREEN: Write minimal code to make the test pass**
   - Only write enough code to pass the test
   - Don't over-engineer or add extra features

3. **REFACTOR: Clean up while keeping tests green**
   - Improve code structure
   - Remove duplication
   - Run tests after each refactor

### Test Structure by Layer

#### Domain Layer (Use Cases, Services)
```typescript
// __tests__/domain/usecases/getJob.usecase.test.ts

describe('GetJobUseCase', () => {
  const mockJobRepository: MockedObject<IJobRepository> = {
    getJob: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should return the job from the repository', async () => {
    // Arrange
    const useCase = new GetJobUseCase(mockJobRepository);
    const jobId = 'job-123';
    mockJobRepository.getJob.mockResolvedValue({ id: jobId, title: 'Engineer' });

    // Act
    const job = await useCase.execute(jobId);

    // Assert
    expect(job).toEqual({ id: jobId, title: 'Engineer' });
  });
});
```

#### Presentation Layer (Hooks)
```typescript
// __tests__/presentation/hooks/useJob.test.ts

describe('useJob', () => {
  const mockGetJobUseCase = vi.fn();

  beforeEach(() => {
    vi.mocked(useInjectedGetJobUseCase).mockReturnValue({
      execute: mockGetJobUseCase,
    });
  });

  it('should call use case with job id', () => {
    // Arrange
    mockGetJobUseCase.mockResolvedValue({ id: 'job-123', title: 'Engineer' });

    // Act
    renderHook(() => useJob('job-123'));

    // Assert
    expect(mockGetJobUseCase).toHaveBeenCalledWith('job-123');
  });
});
```

#### Components (Integration with User Interaction)
```typescript
// __tests__/presentation/components/JobCard.test.tsx

describe('JobCard', () => {
  it('should display job title and call onClick when clicked', async () => {
    // Arrange
    const onClickMock = vi.fn();
    const job = { id: '1', title: 'Software Engineer' };

    // Act
    render(<JobCard job={job} onClick={onClickMock} />);
    await userEvent.click(screen.getByText('Software Engineer'));

    // Assert
    expect(onClickMock).toHaveBeenCalledWith('1');
  });
});
```

### When to Write Tests

| Scenario | Test First? | Example |
|----------|-------------|---------|
| New feature | Yes | New use case, new component |
| Bug fix | Yes | Reproduce bug with failing test first |
| Refactoring | No (tests exist) | Keep existing tests green |
| Updating existing feature | Update test first | Modify test to expect new behavior |

### Test File Organization

```
feature-name/
├── __tests__/
│   ├── domain/
│   │   ├── usecases/         # Use case tests
│   │   └── services/         # Domain service tests
│   ├── data/
│   │   ├── repositories/     # Repository tests
│   │   └── mappers/          # Mapper tests
│   └── presentation/
│       ├── hooks/            # Hook tests
│       └── components/       # Component tests
```

### What to Test at Each Layer

| Layer | What to Test | Mocking |
|-------|--------------|---------|
| Use Cases | Business logic orchestration | Mock repositories |
| Domain Services | Pure business rules | No mocks needed |
| Repositories | Query options, data mapping | Mock services |
| Hooks | Hook behavior, state updates | Mock use cases via DI |
| Components | User interactions, rendering | Mock hooks via DI |

### Testing DI-Injected Dependencies

Always mock DI hooks, not the underlying classes:

```typescript
// ✅ Correct - Mock the DI hook
vi.mock('@/shared/di', () => ({
  useInjectedJobRepository: () => ({
    getJobQueryOptions: mockGetJobQueryOptions,
  }),
}));

// ❌ Wrong - Mocking class directly
vi.mock('../repositories/JobRepository', () => ({
  JobRepository: vi.fn().mockImplementation(() => ({
    getJobQueryOptions: mockGetJobQueryOptions,
  })),
}));
```

### Before Adding New Tests

- **Check if an existing test should be updated** instead of creating a new one
- Avoid duplicate tests that cover the same logic
- Group related tests in the same describe block

---

## 2. Frontend Architecture Layers
- The application has three layers:
  - Presentation
  - Domain
  - Data
- Dependency flow is strictly: Presentation → Domain ← Data
- Domain is the innermost layer and knows nothing about Presentation or Data layers.

## 3. Models & Naming
- Presentation layer models end with: `Ui` (e.g., `JobUi`, `CandidateUi`)
- Domain layer models: Use base name (e.g., `Job`, `Candidate`) - these are the canonical business objects
- Data layer models end with: `Dto` (e.g., `JobDto`, `CandidateDto`)

## 4. Mapping Between Layers
- Mappers belong in the layer that knows about both types:
  - `data/mappers/`: Contains `Dto` → `Model` mappers (data layer knows about domain types)
  - `presentation/mappers/`: Contains `Model` → `Ui` mappers (presentation layer knows about domain types)
- Domain layer has NO mappers (it doesn't know about Dto or Ui types).
- No layer should directly use another layer's model type without mapping.

## 5. Presentation Layer Rules
- Folder name: `presentation/` (not `ui/`)
- Contains no business logic.
- Uses Zustand for all state management (see §5.1 for store patterns).
- Each React hook has a single responsibility and maps 1:1 to one domain use case.
- Hooks:
  - Call the corresponding use case.
  - Use mappers for Model → Ui conversions.
  - Prepare UI-facing state only.
- UI models should be explicit types with display fields, not just aliases to domain models.
  ```typescript
  // ❌ Wrong - just an alias
  export type JobUi = Job;

  // ✅ Correct - explicit UI type with display fields
  export type JobUi = Job & {
    salaryDisplay: string;
    statusDisplay: string;
  };
  ```

### 5.1 Zustand Store Patterns

#### SessionStorage Persistence for State Recovery

When state needs to survive page refreshes (e.g., batch processing progress), use Zustand's `persist` middleware with `sessionStorage`:

```typescript
// stores/batchProcessingStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface BatchProcessingState {
  currentBatch: BatchInfo | null;
  recoveryState: RecoveryState | null;
  // ... other state
}

export const useBatchProcessingStore = create<BatchProcessingState>()(
  persist(
    (set, get) => ({
      currentBatch: null,
      recoveryState: null,

      trackBatch: (batchId: string, totalCount: number) => {
        set({
          currentBatch: { batchId, totalCount, processedCount: 0 },
          recoveryState: { isProcessing: true },
        });
      },

      // ... other actions
    }),
    {
      name: 'batch-processing-storage', // Key in sessionStorage
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        // Only persist what's needed for recovery
        currentBatch: state.currentBatch,
        recoveryState: state.recoveryState,
      }),
    }
  )
);
```

**When to use sessionStorage persistence:**
- Batch processing state (resume uploads, talent pool imports)
- Multi-step wizard progress
- Any state that should survive F5 but NOT persist across browser sessions

**When NOT to use persistence:**
- File objects (File can't be serialized)
- Transient UI state (dialogs, loading spinners)
- State derived from server data

#### Accessing Zustand State Outside React (SSE/Callbacks)

When accessing Zustand state in SSE handlers, WebSocket callbacks, or other non-React contexts, use `store.getState()` to avoid stale closures:

```typescript
// ❌ Wrong - Stale closure captures initial state
function useResumeProcessing() {
  const { currentBatch, updateProgress } = useBatchProcessing();

  const handleSSEMessage = useCallback((event: MessageEvent) => {
    // BUG: currentBatch is stale - captured when callback was created
    console.log(currentBatch?.batchId);
    updateProgress(1);
  }, [currentBatch, updateProgress]); // Even with deps, closure can be stale
}

// ✅ Correct - Read fresh state at call time
function useResumeProcessing() {
  const updateProgress = useBatchProcessingStore((s) => s.updateProgress);

  const handleSSEMessage = useCallback((event: MessageEvent) => {
    // FRESH: Read current state when event fires
    const { currentBatch, processedCount } = useBatchProcessingStore.getState();
    console.log(currentBatch?.batchId);
    updateProgress(processedCount + 1);
  }, [updateProgress]);
}
```

**Rule:** In event handlers, SSE callbacks, or WebSocket handlers that fire asynchronously:
- Use `store.getState()` to read current state
- Actions (like `updateProgress`) are stable and safe to use from closures

## 6. Domain Layer Rules
- Contains:
  - Use cases (injectable classes with `@injectable()` and `@inject()` decorators)
  - Domain services
  - Repository interfaces
  - Domain models (types/)
- Does NOT contain:
  - Mappers (these belong in data or presentation layers)
  - Any imports from data or presentation layers
- Each use case:
  - Has a single responsibility.
  - Maps 1:1 to a presentation hook.
  - Is an injectable class with repository injected via constructor.
- Shared logic goes into domain services.
- Use cases/services depend only on repository interfaces (never data implementations).
- Domain models are pure business data - no display/formatting fields.

### Use Case Independence
- Use cases MUST NOT depend on or call other use cases.
- If shared logic is needed between use cases, extract it to a **domain service**.
- Use cases are application entry points called by presentation hooks, not reusable building blocks.

```typescript
// ❌ Wrong - Use case depends on another use case
@injectable()
export class UploadCandidatesUseCase {
  constructor(
    @inject(DI_TOKENS.ValidateResumesUseCase)
    private validateResumesUseCase: ValidateResumesUseCase  // Anti-pattern!
  ) {}
}

// ✅ Correct - Extract shared logic to domain service
@injectable()
export class UploadCandidatesUseCase {
  constructor(
    @inject(DI_TOKENS.FileValidationService)
    private fileValidationService: IFileValidationService  // Domain service
  ) {}
}
```

### Use Case DI Pattern
Use cases MUST be injectable classes, not plain functions. The repository is injected via constructor, not passed as a parameter.

**Use cases don't need interfaces** - unlike repositories and services, use cases:
- Contain pure business logic with no external dependencies to swap
- Are testable via mocking their injected repository
- Have only one implementation per use case

```typescript
// ❌ WRONG - Plain function with repository parameter
export function getJobUseCase(
  jobRepository: IJobRepository,
  jobId: string
): JobQueryResult {
  return jobRepository.getJob(jobId);
}

// ✅ CORRECT - Injectable class (no interface needed)
import { injectable, inject } from 'tsyringe';
import { DI_TOKENS } from '@/shared/di/tokens';

@injectable()
export class GetJobUseCase {
  constructor(
    @inject(DI_TOKENS.JobRepository) private readonly jobRepository: IJobRepository
  ) {}

  execute(jobId: string | undefined): JobQueryResult {
    return this.jobRepository.getJob(jobId);
  }
}
```

**Presentation hook usage:**
```typescript
// ❌ WRONG - Injecting repository and passing to use case function
function useJob(jobId: string) {
  const jobRepository = useInjectedJobRepository();
  return getJobUseCase(jobRepository, jobId);  // DI violation!
}

// ✅ CORRECT - Injecting use case directly
function useJob(jobId: string) {
  const getJobUseCase = useInjectedGetJobUseCase();
  return getJobUseCase.execute(jobId);
}
```

## 7. Data Layer Rules
- Implements the repository interfaces defined in the domain layer.
- Connects to APIs or local storage.
- Contains mappers in `data/mappers/` for Dto → Model conversions.
- Repository implementations return domain models (mapping happens internally).
- Must be framework-agnostic with respect to React and TanStack Query.
- Repositories expose plain async methods that return `Promise<Model>`, `Promise<Result>`, or `Promise<void>`.
- TanStack Query usage belongs only in `presentation/hooks/`.

### Repository Contracts

```typescript
// ✅ Correct - plain async repository method
async updateJobStatus(jobId: string, status: string): Promise<void> {
  await this.jobService.updateJobStatus(jobId, status);
}
```

### TanStack Query Placement

- `presentation/hooks/` owns:
  - `useQuery`, `useMutation`
  - query keys
  - stale time / refetch / polling behavior
  - cache invalidation and optimistic updates
- `domain/` and `data/` must not import:
  - `@tanstack/react-query`
  - `UseQueryOptions`
  - `UseMutationOptions`
  - `QueryClient`

### Why this boundary exists

- Repository/data concerns answer: "how do I get or save the data?"
- Presentation concerns answer: "when should the screen fetch, refetch, invalidate, or reuse cached data?"
- TanStack Query is therefore treated as presentation orchestration, not as a repository abstraction.

### Exceptions: Direct Async Methods
Some repository methods may use direct `async` instead of React Query when:
- **SSE/WebSocket streams** - Persistent connections that don't fit query/mutation patterns (e.g., `getCandidateUpdates`)
- **Imperative one-time fetches** - Called inside `useEffect` for recovery/initialization, not reactive UI (e.g., `getJobProcessingStatus`)

These are exceptional cases. Default to `useQuery` for reads and `useMutation` for writes.

## 8. Avoid Magic Values
- Use named constants for repeated literals (strings, numbers, etc.)
- Place constants in shared locations (e.g., query key factories, config files)

## 9. Type Placement
- Define types/models only in their designated layer directories (e.g., `types/`, `models/`).
- Never define types inline or locally within components, hooks, or service files.

## 10. Feature Folder Structure
```
feature-name/
├── data/
│   ├── mappers/           # Dto → Model mappers
│   ├── repositories/      # Repository implementations
│   ├── services/          # API services
│   └── types/
│       └── dto/           # DTOs (snake_case, matches API)
├── di/
│   ├── index.ts           # Re-exports
│   └── register.ts        # Feature-specific DI registrations
├── domain/
│   ├── interfaces/        # Repository interfaces
│   ├── services/          # Domain services (business logic)
│   ├── usecases/          # Use cases (1:1 with hooks)
│   └── types/
│       └── model/         # Domain models (camelCase)
├── presentation/
│   ├── ui/
│   │   ├── pages/         # Page components (compose smaller components, ~50-150 lines)
│   │   └── components/    # Reusable UI building blocks (single responsibility)
│   ├── hooks/             # Custom hooks (1:1 with use cases)
│   ├── mappers/           # Model → Ui mappers
│   └── types/
│       └── ui/            # UI models with display fields
└── index.ts               # Public API exports
```

### Pages vs Components

The `presentation/ui/` folder has a strict separation between pages and components:

#### Pages (`ui/pages/`)
- **Purpose**: Compose smaller components into a full page view
- **Size**: Target 50-150 lines (orchestration only, no business logic)
- **Responsibility**: Layout, data wiring, passing props to components
- **Naming**: `<FeatureName>Page.tsx` (e.g., `OrganizationDetailsPage.tsx`)

```typescript
// ✅ Correct - Page composes components
export function OrganizationDetailsPage() {
  const { organization, isLoading } = useOrganization();
  const [activeTab, setActiveTab] = useState('overview');

  if (isLoading) return <PageSkeleton />;

  return (
    <PageLayout title="Organization Details">
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      {activeTab === 'overview' && <OrganizationOverview organization={organization} />}
      {activeTab === 'hierarchy' && <OrgHierarchyTree organization={organization} />}
      {activeTab === 'integrations' && <IntegrationsList />}
    </PageLayout>
  );
}
```

#### Components (`ui/components/`)
- **Purpose**: Reusable, single-responsibility UI building blocks
- **Size**: Target 50-200 lines per component
- **Responsibility**: Render one specific piece of UI, receive data via props
- **Naming**: Descriptive of what it renders (e.g., `OrgHierarchyTree.tsx`, `RolePermissionMatrix.tsx`)

```typescript
// ✅ Correct - Component has single responsibility
interface OrgHierarchyTreeProps {
  nodes: OrgHierarchyNode[];
  expandedNodeIds: Set<string>;
  onToggleNode: (nodeId: string) => void;
}

export function OrgHierarchyTree({ nodes, expandedNodeIds, onToggleNode }: OrgHierarchyTreeProps) {
  return (
    <div className="space-y-2">
      {nodes.map(node => (
        <OrgHierarchyNode
          key={node.id}
          node={node}
          isExpanded={expandedNodeIds.has(node.id)}
          onToggle={() => onToggleNode(node.id)}
        />
      ))}
    </div>
  );
}
```

#### When to Extract a Component

| Signal | Action |
|--------|--------|
| Page exceeds 150 lines | Extract sections into components |
| Repeated JSX patterns | Extract into reusable component |
| Complex rendering logic | Extract into dedicated component |
| Tab content sections | Each tab content = separate component |
| Card/panel sections | Each distinct section = component |

#### Anti-patterns

```typescript
// ❌ Wrong - Page with all logic inline (800+ lines)
export function OrganizationDetails() {
  // 50 lines of state declarations
  // 100 lines of handlers
  // 600 lines of JSX with nested conditionals
}

// ❌ Wrong - Component in pages folder
// ui/pages/OrgHierarchyTree.tsx  <- Should be in components/

// ❌ Wrong - Page that's just a wrapper
export function SettingsPage() {
  return <Settings />;  // Just delegates to one component
}
```

## 11. Dependency Injection Rules

The application uses TSyringe for dependency injection, following patterns similar to Hilt in Android.

### Concept Mapping: Hilt ↔ TSyringe

| Concept | Hilt (Android) | TSyringe (This codebase) |
|---------|---------------|--------------------------|
| Container | `@HiltAndroidApp` | `container` from tsyringe |
| Token/Key | `@Named("key")` | `Symbol.for('key')` in `DI_TOKENS` |
| Registration | `@Module` + `@Provides` | `container.register()` in `register.ts` |
| Singleton | `@Singleton` | `container.registerSingleton()` |
| Injectable class | `@Inject constructor` | `@injectable()` decorator |
| Parameter injection | `@Named` on param | `@inject(token)` on param |
| Assisted/Factory | `@AssistedFactory` | `useFactory` pattern |

### Core Principles
- **Never manually construct dependencies in hooks** - This defeats the purpose of DI
- **Inject dependencies via DI hooks** - Use `useInjected*` hooks from `@/shared/di`
- **Use factories for runtime parameters** - When a dependency needs runtime values (like `jobId`), inject a factory
- **All injectable classes must use decorators** - `@injectable()` on class, `@inject(token)` on interface params

### Class Decorators

#### `@injectable()` - Mark Class as Injectable
Every class that will be instantiated by the DI container MUST have `@injectable()`:

```typescript
import { injectable } from 'tsyringe';

// ✅ CORRECT - Class can be instantiated by container
@injectable()
export class JobService implements IJobService {
  // ...
}

// ❌ WRONG - Container cannot instantiate this class
export class JobService implements IJobService {
  // ...
}
```

**Hilt equivalent:** `@Inject constructor`

#### `@inject(token)` - Inject Interface Dependencies
When a constructor parameter is an interface (not a concrete class), use `@inject()` with the DI token:

```typescript
import { injectable, inject } from 'tsyringe';
import { DI_TOKENS } from '@/shared/di/tokens';

// ✅ CORRECT - Interface dependency with token
@injectable()
export class JobRepository implements IJobRepository {
  constructor(
    @inject(DI_TOKENS.JobService) private readonly jobService: IJobService
  ) {}
}

// ❌ WRONG - TSyringe can't resolve interface without token
@injectable()
export class JobRepository implements IJobRepository {
  constructor(private readonly jobService: IJobService) {}
}
```

**Hilt equivalent:** `@Named("JobService")` on constructor parameter

### DI Violations (What NOT to Do)

```typescript
// ❌ WRONG - Manual construction defeats DI
function useJobProcessing(jobId: string) {
  const jobRepository = useInjectedJobRepository();

  // This is a DI violation - manually constructing dependencies
  const context = new JobProcessingContext(jobRepository, () => jobId);
  const stateManager = new ResumeProcessingStateManager(context);
}

// ❌ WRONG - Missing @injectable() decorator
export class MyService implements IMyService {
  constructor(@inject(DI_TOKENS.Repo) private repo: IRepo) {}
}

// ❌ WRONG - Missing @inject() for interface parameter
@injectable()
export class MyService implements IMyService {
  constructor(private repo: IRepo) {}  // TSyringe can't resolve IRepo!
}
```

### Factory Pattern for Runtime Parameters

When a dependency requires runtime parameters (like `jobId`), use the Factory pattern (similar to Hilt's `@AssistedFactory`):

```typescript
// ✅ CORRECT - Factory injection
function useJobProcessing(jobId: string) {
  // Get factory from DI container
  const createStateManager = useInjectedResumeProcessingStateManagerFactory();

  // Factory encapsulates all internal dependencies
  // Only runtime parameter (jobId) is passed
  const stateManager = useMemo(
    () => createStateManager(() => jobId || ''),
    [createStateManager, jobId]
  );
}
```

### Registration in `feature/di/register.ts`

```typescript
import { container } from 'tsyringe';
import { DI_TOKENS } from '@/shared/di/tokens';

export function registerFeatureDependencies(): void {
  // Singleton registration (like @Singleton in Hilt)
  container.registerSingleton<IJobService>(DI_TOKENS.JobService, JobService);
  container.registerSingleton<IJobRepository>(DI_TOKENS.JobRepository, JobRepository);

  // Factory registration (like @AssistedFactory in Hilt)
  container.register<MyServiceFactory>(
    DI_TOKENS.MyServiceFactory,
    {
      useFactory: (dependencyContainer) => {
        // Factory closure captures container for dependency resolution
        return (runtimeParam: string) => {
          // Resolve container-managed dependencies
          const repository = dependencyContainer.resolve<IRepository>(DI_TOKENS.Repository);

          // Create instance with injected deps + runtime param
          return new MyService(repository, runtimeParam);
        };
      },
    }
  );
}
```

### DI File Organization

| File | Purpose | Hilt Equivalent |
|------|---------|-----------------|
| `@/shared/di/tokens.ts` | DI tokens (symbols) | `@Named` annotations |
| `@/shared/di/types.ts` | Factory type definitions | `@AssistedFactory` interfaces |
| `@/shared/di/hooks.ts` | React hooks for injection | `@Inject` in ViewModels |
| `feature/di/register.ts` | Feature registrations | `@Module` + `@Provides` |

### When to Use Factories vs Direct Injection

| Scenario | Pattern |
|----------|---------|
| Singleton service (no runtime params) | Direct injection: `useInjectedJobRepository()` |
| Needs runtime params (jobId, userId) | Factory injection: `useInjectedMyServiceFactory()` |
| Stateful per-component instance | Factory injection |
| Stateless shared instance | Direct injection |

### Complete Example: Adding a New Injectable Service

1. **Define interface** (in `domain/interfaces/`):
```typescript
export interface IMyService {
  doSomething(): void;
}
```

2. **Add token** (in `@/shared/di/tokens.ts`):
```typescript
export const DI_TOKENS = {
  // ...existing tokens
  MyService: Symbol.for('MyService'),
};
```

3. **Implement class with decorators** (in `data/services/`):
```typescript
import { injectable, inject } from 'tsyringe';
import { DI_TOKENS } from '@/shared/di/tokens';

@injectable()
export class MyService implements IMyService {
  constructor(
    @inject(DI_TOKENS.SomeDependency) private dep: ISomeDependency
  ) {}

  doSomething(): void {
    // implementation
  }
}
```

4. **Register in container** (in `feature/di/register.ts`):
```typescript
container.registerSingleton<IMyService>(DI_TOKENS.MyService, MyService);
```

5. **Create injection hook** (in `@/shared/di/hooks.ts`):
```typescript
export function useInjectedMyService(): IMyService {
  return useMemo(() => {
    return container.resolve<IMyService>(DI_TOKENS.MyService);
  }, []);
}
```

6. **Export hook from barrel file** (in `@/shared/di/index.ts`):
```typescript
export {
  // ...existing exports
  useInjectedMyService,  // Add new hook to exports
} from './hooks';
```
**CRITICAL:** Without this step, imports from `@/shared/di` will fail at runtime with "binding name not found".

7. **Use in React hooks**:
```typescript
function useMyFeature() {
  const myService = useInjectedMyService();
  // use myService...
}
```

### Testing with DI Mocks

When testing components that use DI hooks, mock the `@/shared/di` module instead of individual services:

```typescript
// ✅ CORRECT - Mock the DI hook
const mockUpdateCandidate = vi.fn();
vi.mock('@/shared/di', () => ({
  useInjectedJobService: () => ({
    updateCandidate: mockUpdateCandidate,
  }),
}));

// Use in tests
mockUpdateCandidate.mockResolvedValueOnce({});
// ... render component and trigger action
expect(mockUpdateCandidate).toHaveBeenCalledWith('job-id', 'candidate-id', expectedPayload);

// ❌ WRONG - Mocking the service file directly (bypasses DI)
vi.mock('@/features/job-details/data/services/job.service', () => ({
  jobService: { updateCandidate: vi.fn() },
}));
```

**Key points:**
- Define mock functions (`vi.fn()`) before the `vi.mock()` call (hoisting allows this)
- Mock only the methods your test needs
- Reset mocks in `beforeEach`/`afterEach` with `vi.clearAllMocks()` and `vi.resetAllMocks()`
- For multiple DI hooks, include all in the same mock object:
  ```typescript
  vi.mock('@/shared/di', () => ({
    useInjectedJobService: () => ({ updateCandidate: mockUpdateCandidate }),
    useInjectedJobRepository: () => ({ getJob: mockGetJob }),
  }));
  ```

## 12. Domain Services for Business Logic

Extract business logic from hooks into domain services when the logic involves business rules, constants, or is reusable across multiple hooks.

### When to Extract to Domain Service

| Scenario | Extract? | Example |
|----------|----------|---------|
| Business rules with constants | Yes | File size limits, validation rules |
| Reusable across multiple hooks | Yes | Date formatting, status calculations |
| Pure computation/transformation | Yes | Stage counting, filtering logic |
| UI-only state management | No | Dialog open/close, form state |
| Single-use simple logic | No | One-liner conditionals |

### Example: File Validation

```typescript
// ❌ Wrong - Business logic embedded in hook
const MAX_FILE_SIZE = 50 * 1024 * 1024; // Magic number in hook

const processFiles = useCallback((files: File[]) => {
  const oversizedFiles = files.filter(f => f.size > MAX_FILE_SIZE);
  return {
    valid: files.filter(f => f.size <= MAX_FILE_SIZE),
    rejected: oversizedFiles.map(f => ({
      filename: f.name,
      reason: `File too large (${(f.size / (1024 * 1024)).toFixed(1)}MB > 50MB)`
    }))
  };
}, []);

// ✅ Correct - Business logic in domain service
// domain/services/fileValidation.service.ts
export const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024;
export const MAX_FILE_SIZE_MB = 50;

export interface FileValidationResult {
  validFiles: File[];
  rejectedFiles: RejectedFile[];
  hasRejections: boolean;
}

export function validateFileSizes(files: File[]): FileValidationResult {
  const validFiles: File[] = [];
  const rejectedFiles: RejectedFile[] = [];

  for (const file of files) {
    if (file.size > MAX_FILE_SIZE_BYTES) {
      rejectedFiles.push({
        filename: file.name,
        reason: `File too large (${formatFileSize(file.size)} > ${MAX_FILE_SIZE_MB}MB)`
      });
    } else {
      validFiles.push(file);
    }
  }

  return { validFiles, rejectedFiles, hasRejections: rejectedFiles.length > 0 };
}

// Hook uses the service
import { validateFileSizes } from '../../domain/services/fileValidation.service';

const processFiles = useCallback((files: File[]) => {
  const { validFiles, rejectedFiles, hasRejections } = validateFileSizes(files);
  // ... handle results
}, []);
```

### Benefits
- **Testable in isolation** - No React hook testing complexity
- **Reusable** - Same validation logic across upload components
- **Single source of truth** - Constants defined once
- **Clear responsibility** - Hook handles UI state, service handles business rules

## 13. Prefer Derived State Over Local State

When state can be computed from domain data, derive it rather than manage it locally. This prevents state synchronization bugs and reduces complexity.

### Signs of State Duplication

| Anti-pattern | Problem |
|--------------|---------|
| Local state mirrors domain data | State can drift out of sync |
| `useEffect` to sync local state from props | Extra re-renders, race conditions |
| Multiple sources of truth | Confusing, error-prone |

### Example: Job Status

```typescript
// ❌ Wrong - Local state duplicating domain data
function useApplicantOperations() {
  const [isJobInactive, setIsJobInactive] = useState(false);
  const [currentJobStatus, setCurrentJobStatus] = useState<string>('');

  // Effect to sync state - this is a code smell!
  useEffect(() => {
    if (job) {
      setCurrentJobStatus(job.status);
      setIsJobInactive(job.status === 'Paused' || job.status === 'Closed');
    }
  }, [job]);

  return { isJobInactive, currentJobStatus };
}

// ✅ Correct - Derived directly from domain data
function JobDetails() {
  const { job } = useJob(jobId);

  // Derive from authoritative source (domain data)
  const isJobInactive = job?.statusDisplay === 'Paused' ||
                        job?.statusDisplay === 'Closed' ||
                        job?.statusDisplay === 'Cancelled';

  // Use directly in component/pass to children
  return <ResumeUploader isJobInactive={isJobInactive} />;
}
```

### When Local State IS Appropriate

- **UI-only state**: Dialog visibility, form inputs, accordion expansion
- **Optimistic updates**: Temporary state before server confirmation
- **Computed aggregations**: When derived from multiple sources and expensive to compute

## 14. Detecting Dead Code and Incomplete Implementations

Regularly audit hooks for unused or incomplete code that violates architecture patterns.

### Warning Signs

| Pattern | Problem | Solution |
|---------|---------|----------|
| Handlers that only update local state | Missing backend integration | Delete or integrate with use case |
| Hardcoded user values (e.g., `"John Doe"`) | Missing auth context | Use auth hook/context |
| Functions returned but never called | Dead code | Remove from hook |
| State that duplicates domain data | Over-engineering | Derive from domain instead |
| `TODO` comments with no tracking | Forgotten incomplete work | Complete or remove |

### Example: Incomplete Handlers

```typescript
// ❌ Wrong - Handlers only update local state, never persist
function useApplicantOperations() {
  const [currentJobStatus, setCurrentJobStatus] = useState('Active');

  // These look complete but don't actually work!
  const handlePauseJob = () => setCurrentJobStatus('Paused');  // No API call
  const handleResumeJob = () => setCurrentJobStatus('Active'); // No API call

  // Hardcoded user - should come from auth
  const handleOverride = () => ({
    overriddenBy: "John Doe",  // Magic string!
    overriddenAt: new Date()
  });

  return { handlePauseJob, handleResumeJob, handleOverride };
}

// ✅ Correct - Either integrate properly or remove
// Option 1: Proper integration via use case
function useJobStatusUpdate() {
  const updateJobStatusUseCase = useInjectedUpdateJobStatusUseCase();
  const { updateJobStatus } = updateJobStatusUseCase.execute();

  return { updateJobStatus }; // Actually persists to backend
}

// Option 2: If not needed, don't include it
function useApplicantOperations() {
  // Only include what's actually used and working
  const [applicants, setApplicants] = useState([]);
  return { applicants, setApplicants };
}
```

### Audit Checklist

When reviewing hooks, verify:
1. Every handler either updates UI-only state OR calls a use case
2. No hardcoded user/org values - use auth context
3. All returned functions are actually used by consumers
4. No local state that mirrors domain data
5. No `useEffect` that just syncs props to state

## 15. Hook Layering Rules

### Maximum Depth: 1 Layer of Hooks Calling Hooks

The architecture enforces a strict layering rule to prevent deeply nested hook hierarchies that are hard to understand and test:

```
Page Component
  └── Coordination Hook (optional, composes hooks + wires callbacks)
        └── Simple Hooks (each calls use cases or manages 1 concern)
              └── Use Cases / Domain Services (via DI)
```

### Allowed Patterns

```typescript
// ✅ Coordination hook calls simple hooks (1 layer)
function useUploadCoordination(jobId: string) {
  const cancellable = useCancellableJob({ ... });      // Simple hook
  const processing = useJobResumeProcessing(jobId);    // Simple hook
  const upload = useResumeUpload(job, handleBatchStart); // Simple hook
  return { ... };
}

// ✅ Simple hook calls use case via DI
function useResumeUpload(job: Job, onBatchStart: () => void) {
  const uploadUseCase = useInjectedUploadCandidatesUseCase(); // DI
  const validateUseCase = useInjectedValidateResumesUseCase(); // DI
  const [files, setFiles] = useState([]);
  return { ... };
}
```

### Forbidden Patterns

```typescript
// ❌ Hook calling another hook that calls hooks (2+ layers)
function useResumeBatchProcessing(jobId: string) {
  const cancellable = useCancellableJob({ ... });      // Hook
  const processing = useJobResumeProcessing(jobId);    // Hook
  // This is a coordination hook pretending to be a simple hook!
}

function useUploadCoordination(jobId: string) {
  const batch = useResumeBatchProcessing(jobId); // ❌ Creates 2 layers
  const upload = useResumeUpload(job, batch.onStart);
}
```

### Hook Naming Conventions

| Suffix | Purpose | Allowed to call |
|--------|---------|-----------------|
| `use[Entity]` | Data fetching | Use cases via DI |
| `use[Entity]Operations` | Local state CRUD | React state only |
| `use[Feature]Coordination` | Composes 2+ hooks | Simple hooks only |

### Coordination Hooks

**When to use:**
1. Page has 8+ hook calls that create visual noise
2. Multiple hooks have interdependencies (callbacks passed between them)
3. Same hook combinations used in multiple places

**When NOT to use:**
1. Page has <5 hook calls
2. Hooks are independent (no shared state or callbacks)
3. Would be passthrough with no logic

### Verification Checklist

When reviewing hooks:
1. Count layers: Page → Hook → Hook → Use Case = 2 layers (violation)
2. Ensure no hook calls another hook that also calls hooks
3. Coordination hooks should ONLY call simple hooks, never other coordination hooks
4. Simple hooks should ONLY call use cases (via DI) or manage local state

---

## 16. React Query Placement

React Query hooks (`useQuery`, `useMutation`, `useQueryClient`) belong in the **presentation layer**, not in injectable classes.

### Why?
- DI container instantiates classes outside React's render cycle
- React hooks can only be called during rendering
- Query options are just data - safe to return from injectable classes

### Layer Placement

| Layer | Contains | React Hooks? |
|-------|----------|--------------|
| Presentation | Hooks wrapping useQuery/useMutation | ✅ Yes |
| Domain | Use Cases (returns query options) | ❌ No |
| Data | Repository returning query options | ❌ No |
| Infrastructure | Service (HTTP calls) | ❌ No |

### Pattern: Query Options Separation

Based on TkDodo's (TanStack maintainer) recommendation, separate query OPTIONS from hook calls:

```typescript
// ✅ Repository returns query options (injectable, no hooks)
@injectable()
class JobRepository {
  getJobQueryOptions(jobId: string): UseQueryOptions<Job> {
    return {
      queryKey: ['job', jobId],
      queryFn: () => this.service.getJob(jobId).then(mapToModel),
      enabled: !!jobId,
      staleTime: 5 * 60 * 1000,
    };
  }
}

// ✅ Use case returns plain domain data
@injectable()
class GetJobUseCase {
  constructor(
    @inject(DI_TOKENS.JobRepository) private readonly jobRepository: IJobRepository
  ) {}

  execute(jobId: string): Promise<Job> {
    return this.jobRepository.getJob(jobId);
  }
}

// ✅ Presentation hook owns query orchestration
function useJob(jobId: string) {
  const getJobUseCase = useInjectedGetJobUseCase();
  const query = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJobUseCase.execute(jobId),
    staleTime: 30_000,
  });
  return {
    job: query.data,
    isLoading: query.isLoading,
    error: query.error,
  };
}

// ❌ NEVER put useQuery inside injectable class
@injectable()
class BadRepository {
  getJob(jobId: string) {
    return useQuery({ ... }); // BREAKS - Invalid hook call
  }
}
```

### Mutation Pattern

```typescript
// ✅ Repository returns plain async method
@injectable()
class JobRepository {
  async updateJobStatus(jobId: string, status: string): Promise<void> {
    await this.jobService.updateJobStatus(jobId, status);
  }
}

// ✅ Use case stays framework-agnostic
@injectable()
class UpdateJobStatusUseCase {
  constructor(
    @inject(DI_TOKENS.JobRepository) private readonly jobRepository: IJobRepository
  ) {}

  execute(input: { jobId: string; status: string }): Promise<void> {
    return this.jobRepository.updateJobStatus(input.jobId, input.status);
  }
}

// ✅ Presentation hook calls useMutation + cache invalidation
function useJobStatusUpdate({ jobId, onSuccess }) {
  const updateJobStatusUseCase = useInjectedUpdateJobStatusUseCase();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: updateJobStatusUseCase.execute.bind(updateJobStatusUseCase),
    onSuccess: async (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['job', variables.jobId] });
      onSuccess?.();
    },
  });

  return { updateJobStatus: mutation.mutate };
}
```

### Cache Invalidation

Cache invalidation uses `useQueryClient()` - must be in presentation layer:

```typescript
// ✅ Correct - in presentation hook
function useInvalidateCandidatesCache() {
  const queryClient = useQueryClient();
  return useCallback((jobId: string) => {
    queryClient.invalidateQueries({ queryKey: ['candidates', jobId] });
  }, [queryClient]);
}

// ❌ Wrong - in injectable class
@injectable()
class BadRepository {
  invalidate(key: string[]) {
    const queryClient = useQueryClient(); // BREAKS - Invalid hook call
    queryClient.invalidateQueries({ queryKey: key });
  }
}
```

### Summary Table

| Operation | Repository Returns | Presentation Hook Calls |
|-----------|-------------------|------------------------|
| Read | `Promise<T>` | `useQuery({ queryKey, queryFn })` |
| Write | `Promise<Result>` / `Promise<void>` | `useMutation({ mutationFn })` |
| Cache invalidation | N/A | `useQueryClient().invalidateQueries()` |

---

## 17. Completion Checklist

Before considering a task complete, verify:

- [ ] All new code follows the three-layer architecture (Presentation → Domain ← Data)
- [ ] Tests are written and passing (`npm test`)
- [ ] No linting errors (`npm run lint`)
- [ ] Use cases are injectable classes, not plain functions
- [ ] Use cases don't call other use cases (use domain services for shared logic)
- [ ] Mappers exist for all layer boundary crossings
- [ ] DTOs are used in data layer, Ui models in presentation
- [ ] Repository interfaces are in domain layer
- [ ] Hook layering follows the max 1-layer rule
- [ ] `domain/` and `data/` contain no TanStack Query imports
- [ ] No duplicate types created (checked @/shared first)
- [ ] Types in correct layer directories (not inline in components/hooks)
- [ ] @inject() decorators inline with parameters (not on separate lines)
- [ ] Imports from barrel files where available

After completing the task, provide a summary:

```
## Task Summary

### Files Modified
- `path/to/file.ts` - [description of change]

### Files Created
- `path/to/new_file.ts` - [purpose]

### Tests
- `path/to/test.test.ts` - [what it tests]

### Status
- Tests: PASSED/FAILED
- Lint: PASSED/FAILED
- Architecture: COMPLIANT/VIOLATIONS
```

---

## 18. Pre-Implementation Checks

**IMPORTANT:** Before creating new types or modifying existing ones, run these checks:

### 1. Check for existing types in `@/shared/` first
```bash
grep -r "export type YourType\|export interface YourType" frontend/src/shared --include="*.ts"
```
If type exists in shared, import it instead of creating a new one.

### 2. Check for duplicates across features
```bash
grep -r "export type YourType\|export interface YourType" frontend/src/features --include="*.ts"
```
If same type is needed in multiple features, consider moving to `@/shared/types/`.

### 3. Verify type locations
- DTOs belong in `data/types/dto/`
- Domain models belong in `domain/types/model/`
- UI models belong in `presentation/types/ui/`
- **NEVER** define types inline in components or hooks

### 4. Check for @inject decorator placement
Ensure decorators are inline with parameters:
```typescript
// ✅ CORRECT - @inject inline with parameter
constructor(
  @inject(DI_TOKENS.Repo) private readonly repo: IRepo
) {}

// ❌ WRONG - @inject on separate line
constructor(
  @inject(DI_TOKENS.Repo)
  private readonly repo: IRepo
) {}
```

### 5. Verify barrel file usage
```bash
# Check if there's a barrel file you should import from
ls frontend/src/features/<feature>/domain/types/model/index.ts
ls frontend/src/shared/types/index.ts
```

---

## 19. API Contract Output for Backend Continuation

When building frontend features (especially with mocks or as part of a fullstack task), output a structured API contract section at the end of your implementation. This enables seamless handoff to backend implementation.

### Output Format

After completing a frontend implementation, output this section:

```yaml
## EXPECTED_API_CONTRACT

# Auto-generated context for backend phase
endpoints:
  - method: GET
    path: /api/v1/users/{user_id}/settings
    response:
      type: UserSettings
      fields:
        - theme: string ("light" | "dark")
        - notifications: boolean
        - language: string

  - method: PUT
    path: /api/v1/users/{user_id}/settings
    request:
      type: UpdateSettingsRequest
      fields:
        - theme: string (optional)
        - notifications: boolean (optional)
    response:
      type: UserSettings

types_defined:
  - UserSettings: frontend/src/features/settings/domain/types/model/userSettings.ts
  - UpdateSettingsDto: frontend/src/features/settings/data/types/dto/updateSettings.dto.ts

mock_data_location:
  - frontend/src/features/settings/data/mocks/userSettingsMock.ts

notes:
  - All timestamps use ISO 8601 format
  - Pagination uses limit/offset pattern with total_count in response
```

### When to Output This Section

- **Always** when building frontend with mocks
- **Always** when part of a `fullstack` task with `--frontend-first`
- When the frontend defines DTOs that the backend should implement

### What to Include

1. **Endpoints**: HTTP method, path, request body, response body
2. **Types defined**: File locations of DTOs and domain models
3. **Mock data**: Location of mock implementations for reference
4. **Notes**: Any assumptions about data formats, pagination, etc.

This context is parsed by the autonomous task system and passed to the backend phase.
