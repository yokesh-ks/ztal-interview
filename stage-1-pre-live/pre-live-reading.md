# Pre-Live Reading

This document is the required pre-read for the live session.

You do not need to memorize the full standards before the session. The full standards remain available in the sibling `repo/` folder as reference material. The goal of this pre-read is to help you enter the live exercise with enough context to work effectively in a mature codebase.

Suggested preparation time:

- 15 to 25 minutes is enough

## What This Repo Simulates

This mini-repo simulates a recruiting product with:

- existing frontend and backend code
- existing standards and architectural constraints
- a runnable demo app
- an intentionally incomplete chatbot/agent feature
- existing product tradeoffs and architectural constraints you will need to recognize

Use this pre-read together with the sibling `repo/` folder so you can familiarize yourself with the structure and patterns in context before the session.

## Start Here In The Repo

If you want a concrete path through the codebase before the session, start with these files:

- frontend UI entry:
  [repo/frontend/src/features/chat/presentation/ui/components/ChatExperience.tsx](/Users/raghav/Codes/ztal/interview/stage-1-pre-live/repo/frontend/src/features/chat/presentation/ui/components/ChatExperience.tsx)
- frontend DI/provider wiring:
  [repo/frontend/src/shared/di/ChatDependenciesProvider.tsx](/Users/raghav/Codes/ztal/interview/stage-1-pre-live/repo/frontend/src/shared/di/ChatDependenciesProvider.tsx)
- frontend hook and state flow:
  [repo/frontend/src/features/chat/presentation/hooks/useChat.ts](/Users/raghav/Codes/ztal/interview/stage-1-pre-live/repo/frontend/src/features/chat/presentation/hooks/useChat.ts)
- backend app/container wiring:
  [repo/backend/recruitment_agent/container.py](/Users/raghav/Codes/ztal/interview/stage-1-pre-live/repo/backend/recruitment_agent/container.py)
- backend HTTP entrypoint:
  [repo/backend/recruitment_agent/adapters/inbound/http/chat_routes.py](/Users/raghav/Codes/ztal/interview/stage-1-pre-live/repo/backend/recruitment_agent/adapters/inbound/http/chat_routes.py)
- backend use case example:
  [repo/backend/recruitment_agent/application/use_cases/list_visible_jobs.py](/Users/raghav/Codes/ztal/interview/stage-1-pre-live/repo/backend/recruitment_agent/application/use_cases/list_visible_jobs.py)

Those files are not the only important ones, but they give you a good starting path for:

- how a request reaches the frontend UI
- how frontend dependencies are wired
- how backend dependencies are wired
- where use cases sit relative to routes and adapters

## Repo Map

### Frontend

Relevant folders:

- `frontend/src/features/chat/data/`
- `frontend/src/features/chat/domain/`
- `frontend/src/features/chat/presentation/`
- `frontend/src/shared/di/`
- `frontend/tests/`

High-level direction:

- `presentation` should talk to `domain`
- `domain` should depend on ports/interfaces
- `data` should implement those ports
- dependencies should be wired through DI rather than constructed ad hoc in presentation code
- the DI/provider layer is where concrete implementations should usually be introduced

What "dependency wiring" means here:

- where a component or hook gets the use case it needs
- where that use case gets its repository implementation from
- which parts depend on abstractions and which parts provide the concrete implementations
- where the provider tree creates the concrete instances and passes them down

### Backend

Relevant folders:

- `backend/recruitment_agent/adapters/inbound/`
- `backend/recruitment_agent/application/use_cases/`
- `backend/recruitment_agent/domain/`
- `backend/recruitment_agent/adapters/outbound/`
- `backend/recruitment_agent/container.py`
- `backend/tests/`

High-level direction:

- inbound adapters receive requests
- use cases orchestrate work
- domain services own business rules
- outbound adapters talk to data or external systems
- dependencies should be wired through the container
- the container/bootstrap layer is where concrete implementations should usually be introduced

What "dependency wiring" means here:

- where the HTTP route gets the use cases it calls
- where those use cases get repositories or services from
- how the container connects ports/interfaces to concrete adapters

Dependency direction:

- `inbound -> application -> domain`
- application/domain depend on ports or interfaces, not on concrete outbound adapters
- outbound adapters are integration details that implement those ports from the outside
- domain code must not depend on inbound or outbound adapter code

## Core Working Principles

### Frontend

- Respect layering: `presentation -> domain <- data`
- Presentation code should not reach directly into infrastructure when a use case/DI path exists
- Prefer creating concrete repositories/use cases in the DI/provider layer rather than inside hooks or components
- Components should stay thin
- Explicit UI models are preferred over pushing raw domain models directly into components
- Business-state persistence in `sessionStorage` or `localStorage` is a smell unless it is clearly pure UI state
- For bug fixes, prefer writing a failing test first

### Backend

- Use cases should orchestrate, not own business rules
- Domain services should hold reusable business rules and validations
- Inbound adapters should not contain real business logic
- Prefer creating concrete repositories/services in the container/bootstrap layer rather than inside routes or use cases
- Respect dependency direction: inbound should not skip into domain via ad hoc logic, and domain should not depend on adapters
- Follow dependency direction; do not let layers leak into each other
- For bug fixes, prefer writing a failing test first

### Review Mindset

- Look for behavior bugs first
- Then look for architecture violations and missing tests
- Keep changes narrow and intentional

## Reference Material

The following full references remain available:

- `standards/frontend.md`
- `standards/backend.md`
- `standards/pr-review.md`

Use them when you want to confirm a detail while getting familiar with the repo. You do not need to read them end to end before the session.
