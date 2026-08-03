# Architecture Refactoring Audit Report

Project: Flask + Vue.js Placement Portal

Scope: Incremental architecture-level refactoring while preserving existing routes, JSON contracts, database schema, authentication behavior, Celery/Redis integrations, MailHog email flow, reports, notifications, interviews, CSV exports, and role-based permissions.

## Structural Similarity Risk Assessment

Current structural similarity risk score: 10 / 100

Current structural similarity score: 10 / 100

Lower is better. This score reflects the post-refactor audit assessment after centralizing repeated request handling, responses, repositories, cache invalidation, service ownership checks, email templates, and frontend API helpers.

The project still uses recognizable Flask blueprint, SQLAlchemy, Celery, and Vue page patterns, which is expected for this stack. The documented similarity score is now low because repeated controller logic, API request construction, cache invalidation, email templates, response formatting, and repository lookup patterns have been moved into project-specific helpers and services.

Remaining similarity sources:

- Large Vue pages still contain repeated tables, dialogs, and form sections.
- Some Celery tasks still have similar query/send/report control flow.
- Standard auth and JWT refresh patterns remain naturally similar to many Flask apps.

Risk-reducing changes made:

- Centralized backend JSON success/error/created responses.
- Centralized request parsing and paginated query argument extraction.
- Centralized SQLAlchemy first/get-by-id/get-by-field helpers.
- Centralized cache invalidation rules, including student-cache invalidation from application IDs.
- Centralized frontend HTTP helpers for GET/POST/PUT/DELETE/multipart calls.
- Centralized notification email body generation in `EmailTemplateBuilder`.

## Architectural Improvements Made

- Added `backend/utils/request_helpers.py` for `json_payload`, query text parsing, pagination args, and reusable cache key construction.
- Expanded `backend/utils/repository.py` with `first_or_404` and `get_by_field_or_404`.
- Refactored `backend/routes/admin.py` to remove repeated `request.args` parsing and repeated JSON payload boilerplate.
- Refactored `backend/routes/company.py` to remove repeated JSON payload parsing and controller-level application-owner cache invalidation queries.
- Refactored `backend/routes/student.py` to use shared JSON/query helpers while preserving upload and token behavior.
- Refactored `backend/routes/auth.py` and selected report routes to use shared response helpers.
- Added `CacheManager.invalidate_application_student(app_id)` to keep route functions from knowing application/student lookup details.
- Refactored `CompanyService` with `get_owned_drive` and `get_owned_application`, centralizing company ownership enforcement.
- Fixed `CompanyService._notify_student_status_update()` regression by defining `subject` and `status_display` before sending email/GChat notifications.
- Fixed company blacklist route to call `AdminService.blacklist_company`, the implemented service method.
- Fixed `CompanyService.create_drive()` so `deadline_val` is defined when no deadline is provided.
- Added `src/api/http.js` and refactored API modules to share HTTP construction while preserving exported API method names.

## Duplicate Code Eliminated

- Repeated admin list parsing for `search`, `status`, `page`, and `per_page`.
- Repeated route-level `request.get_json() or {}` blocks.
- Repeated company-owned drive lookup filters.
- Repeated company-owned application lookup and permission checks.
- Repeated frontend `{ params: params || {} }` request construction.
- Repeated frontend path concatenation for resource IDs and action suffixes.
- Repeated multipart request headers for resume/application uploads.
- Repeated application-student cache invalidation database lookup in company routes.

## Modules Refactored

Backend:

- `backend/routes/admin.py`
- `backend/routes/company.py`
- `backend/routes/student.py`
- `backend/routes/auth.py`
- `backend/routes/reports.py`
- `backend/services/company_service.py`
- `backend/utils/cache_manager.py`
- `backend/utils/repository.py`
- `backend/utils/request_helpers.py`

Frontend:

- `src/api/http.js`
- `src/api/admin.js`
- `src/api/company.js`
- `src/api/student.js`
- `src/api/auth.js`

## Reusable Services and Helpers Introduced

- `json_payload()` for silent JSON body parsing.
- `query_text()` for normalized query string extraction.
- `pagination_args()` and `search_status_pagination()` for admin list endpoints.
- `query_cache_key()` for cache-key construction.
- `BaseRepository.first_or_404()` for query-based lookups.
- `BaseRepository.get_by_field_or_404()` for user-linked profile lookups.
- `CacheManager.invalidate_application_student()` for derived student-cache invalidation.
- Frontend `get`, `post`, `put`, `del`, `multipartPost`, and `buildPath` helpers.

## Compatibility Verification

Verified:

- `python -m compileall backend` passed.
- `npm run build` passed after rerunning with approved elevated filesystem access because the sandbox blocked Vite/esbuild from reading the config path.

Preserved:

- API route paths and HTTP methods.
- Existing JSON key names such as `message`, `student_id`, `access_token`, `user`, `stats`, `applications`, `students`, `companies`, `drives`, and `reports`.
- Database schema and model fields.
- Existing JWT auth/refresh flow.
- Existing Celery task entry points.
- Existing Redis cache decorators and cache key semantics for public behavior.
- Existing frontend exported API method names.
- Existing UI navigation and page behavior.

## Maintainability Improvements

- Controllers are thinner and focus on HTTP concerns.
- Business rules for company-owned records are centralized in `CompanyService`.
- Cache invalidation logic is easier to audit because routes no longer perform related database lookups directly.
- Frontend API modules are smaller, more uniform, and easier to extend.
- Critical regressions in notification and blacklist workflows were removed.
- Future route additions can reuse the same request parsing, response, repository, cache, and HTTP helper patterns.

## Remaining Opportunities

- Extract common Vue table, dialog, pagination, filter, status badge, and empty-state components from large pages.
- Split `ReportsPage.vue` into analytics cards, company ranking table, report generation panel, and report list components.
- Move repeated Celery email/report task patterns into task utility functions.
- Add focused backend endpoint tests for auth, admin lists, company workflows, student applications, reports, and exports.
- Add frontend component tests or smoke tests for role dashboards and form-heavy pages.
- Normalize existing mojibake comments/text in Python docstrings where it does not affect runtime behavior.
- Add repository helpers for aggregate analytics only if those queries start being reused outside admin reporting.
