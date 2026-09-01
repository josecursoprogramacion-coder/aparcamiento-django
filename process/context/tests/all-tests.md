# {{project_name}} - All Tests

Last updated: 2026-09-01

Attach this file first when the task involves testing, verification, or test debugging.

This is the fast operator guide for the testing surface:

- which runner to use
- what command to start with
- how to quickly debug common failures
- which deeper file to read next

Do not load the whole `process/context/tests/` folder by default. Start here, then drill down.

---

## How This File Works

This is the `all-tests.md` entrypoint for the `tests/` context group. It follows the `all-*.md` routing convention:

1. Agents read `all-context.md` first and get routed here for testing tasks
2. This file gives quick decision rules and commands
3. For deeper details, agents follow the routing table below to specific docs

As the project grows, add deeper docs to this group (e.g., `e2e-tests.md`, `debugging-and-pitfalls.md`) and add routing entries below. This file stays the fast-start entrypoint.

---

## What This Covers

- test runner selection
- quick commands by package
- fast debugging procedures
- current testing gaps worth remembering

---

## Read This When

Use this file when you need to:

- run tests after implementation
- decide between test runners
- debug failing tests

---

## Quick Routing

<!-- STUDY: Replace with routing entries to deeper test docs as they are created. -->
<!-- Start with an empty table. Add rows as deeper docs are created during the project lifecycle. -->

<!-- Example of what a filled-in routing table looks like (from a mature project): -->

<!--
| If you need... | Read next |
|---|---|
| commands and scripts by package | `scripts-and-commands.md` |
| architecture, mocks, auth model, and runner split | `architecture-and-patterns.md` |
| Playwright setup, auth flow, and current specs | `e2e-tests.md` |
| failing-test triage and runtime debugging | `debugging-and-pitfalls.md` |
| known gaps and future test-system fixes | `known-issues.md` |
-->

(No deeper test docs yet. Add routing entries here as they are created.)

---

## Quick Decision Guide

<!-- STUDY: Replace with actual test runner names and when to use each. -->
<!-- For monorepos with multiple runners, list each runner with its scope. -->

<!-- Example of what this looks like filled in (monorepo with Vitest + Bun + Playwright): -->

<!--
### Use `vitest` when

- the change is in React components, hooks, stores, or plugin logic
- the package already has a vitest config and unit-test surface

### Use `bun test` when

- the change is in `packages/api`
- the behavior is router, route, auth-helper, or model logic

### Use Playwright when

- the behavior depends on real navigation, auth redirects, rendering, or full-screen browser flows

### Use container verification when

- the issue is about runtime services, gateway WebSocket behavior, or proxy state
-->

<!-- Example for a simpler single-app project: -->

<!--
### Use `vitest` for everything

- all tests run through vitest
- `vitest run` for CI, `vitest` (watch mode) for development
- Playwright tests also use vitest as the runner via `@playwright/test`

### Use container verification when

- the issue is about runtime services, gateway WebSocket behavior, or proxy state
-->

## Default Verification Order

Unless the task clearly needs a different path:

1. run the narrowest existing automated test
2. use unit/integration tests before browser tests
3. use end-to-end tests only when the real UI is the thing being verified

## Commands

<!-- STUDY: Replace with actual test commands per package/workspace. -->
<!-- For monorepos, use a table showing package name, runner, and command. -->

<!-- Example of what this looks like filled in (monorepo): -->

<!--
| Package | Runner | Command | Notes |
|---|---|---|---|
| `apps/web` | vitest | `pnpm --filter web test` | jsdom environment |
| `packages/api` | bun test | `pnpm --filter @acme/api test` | needs `.env.test` |
| `packages/db` | bun test | `pnpm --filter @acme/db test` | needs running database |
| `apps/web` (e2e) | Playwright | `pnpm --filter web test:e2e` | needs dev server running |
| root | all | `pnpm test` | runs all packages |

**Typecheck (not a test runner, but often needed for verification):**
```bash
pnpm typecheck          # all packages
pnpm --filter web typecheck  # single package
```

**Lint:**
```bash
pnpm lint               # all packages
pnpm lint:verified      # lint + typecheck together
```
-->

| Package | Runner | Command |
|---|---|---|
| (pending) | (pending) | (pending) |

## Debugging Quick Reference

<!-- STUDY: Replace with actual test config quirks found during analysis. -->
<!-- Examples: "uses jsdom environment", "needs .env.test", "requires running database" -->

<!-- Example of what this looks like filled in: -->

<!--
- **jsdom quirks:** `apps/web` uses jsdom -- Canvas/Image APIs unavailable, mock them in test setup
- **env files:** `packages/api` tests require `.env.test` with `DATABASE_URL` pointing to test DB
- **database state:** API tests use PGlite for isolated test databases, no external DB needed
- **auth mocking:** Clerk is mocked via `vi.mock("@clerk/nextjs")` in web tests
- **port conflicts:** dev server must be stopped before running e2e tests (both use port 3000)
-->

- **jsdom quirks:** Django test runner uses `SimpleTestCase`/`TestCase`; no jsdom
- **env files:** `settings.py` uses PostgreSQL localhost:5433; tests need DB access or mock
- **database state:** Tests will query PostgreSQL; no external DB needed beyond the configured server
- **auth mocking:** Django auth tests use `User.objects` and group filters; no OAuth mocking yet
- **port conflicts:** Dev server on port 8000; separate from test execution

## Known Gaps

<!-- STUDY: Leave empty after populating, but remove this comment. -->
<!-- Track gaps that agents should know about to avoid wasting time on tests that don't exist yet. -->

<!-- Example: -->

<!--
- No integration tests for the billing webhook handler
- E2E tests do not cover the admin dashboard (only the main web app)
- Container runtime tests require manual Docker setup (not in CI yet)
-->

- No tests exist yet (`clientes/tests.py` is empty, `core/` has no test files)
- No test runner configured (would need `pytest` or Django test suite setup)
- No CI/CD pipeline defined for test execution
- No test database setup (PostgreSQL credentials needed: `jose`/`1234` on `localhost:5433`)
- No fixtures or test data defined
- No coverage goals or reporting configured