================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js, CommonJS)
Framework:     Express 4.22.1 (manifest ^4.18.2, resolved in package-lock)
Dependencies:  express 4.22.1, sqlite3 5.1.7
Domain:        LMS / course platform with a checkout flow (courses, enrollments, payments, users, admin financial report)
Architecture:  Monolithic — 3 loose files in src/, no layer folders; AppManager.js (141 lines) does DB setup, seeding, routing, and business logic for 3 domains
Source files:  3 files analyzed (src/app.js, src/AppManager.js, src/utils.js)
DB tables:     users, courses, enrollments, payments, audit_logs (SQLite :memory:)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.22.1 / sqlite3 5.1.7
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] God Class / God File
File: src/AppManager.js:1-141
Description: The AppManager class opens the DB connection (7), creates the schema and seeds data (10-23), and defines all HTTP routes with their SQL and business rules for checkout (28-78), the financial report (80-129) and users (131-137).
Impact: You can't test checkout, the report, or user deletion without bringing up Express and SQLite together. Any change to one domain risks breaking the other two, and the file only grows.
Recommendation: Split into config/database, models (User, Course, Enrollment, Payment, AuditLog), services (Checkout, Report), controllers and routes per domain. See Playbook #1.

### [CRITICAL] Hardcoded credentials / secrets
File: src/utils.js:2-4, src/AppManager.js:45, src/AppManager.js:18
Description: dbUser/dbPass ("senha_super_secreta_prod_123") and paymentGatewayKey ("pk_live_…") are string literals in the code. Line 45 of AppManager prints the full card number and the gateway key to stdout, and the seed at line 18 stores the password '123' in plain text.
Impact: Anyone with repo access, or access to the logs, gets the live payment gateway key and full card numbers (a PCI-DSS violation). Rotating the key means a code deploy.
Recommendation: Move secrets into a config module that reads from environment variables (process.env) with no production defaults. Stop logging card data and the key; mask the card to its last 4 digits. See Playbook #2.

### [CRITICAL] Weak or homemade cryptography
File: src/utils.js:17-23, src/AppManager.js:68
Description: badCrypto repeats the first 2 base64 characters of the password 10,000 times and truncates to 10 characters. It's reversible encoding with no salt, and it collides for any passwords that share their first 1-2 bytes. The checkout also falls back to the default password "123456" when pwd is missing (line 68).
Impact: A DB leak exposes (and makes trivial to guess) every user's password. Different passwords turn into the same "hash", and accounts get created with a predictable default password.
Recommendation: Replace it with crypto.scrypt plus a random salt (native to Node, no new dependency) and compare with crypto.timingSafeEqual. Remove the default password. See Playbook #5.

### [HIGH] Heavy business logic in the Controller/Route
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: The POST /api/checkout handler orchestrates finding the course, creating the user, approving the payment (the `cc.startsWith("4")` rule at 46), enrolling, recording the payment and auditing, all with no transaction. GET /api/admin/financial-report builds the revenue aggregation inside the handler.
Impact: If the payment insert fails after the enrollment insert, you get an unpaid enrollment (inconsistent state). None of these rules can be unit tested or reused outside HTTP.
Recommendation: Extract a CheckoutService (with a transaction: BEGIN/COMMIT/ROLLBACK) and a ReportService. Controllers only translate request↔response. See Playbook #6.

### [HIGH] Tight coupling / no dependency injection
File: src/AppManager.js:7, src/app.js:8-10
Description: AppManager creates its own connection with `new sqlite3.Database(':memory:')` in the constructor, and app.js wires everything by instantiating the manager directly.
Impact: You can't swap the DB for a fake or an isolated DB in tests, or reuse the connection in other modules. The whole data layer is locked into the God Class.
Recommendation: Create the connection in config/database and inject it into models/services through factories (createXModel(db)), wiring everything in app.js. See Playbook #7.

### [HIGH] Mutable global state
File: src/utils.js:9-10, src/utils.js:12-15, src/utils.js:25, src/AppManager.js:2, src/AppManager.js:59
Description: globalCache is a module-level object that every checkout writes to (line 59) and that never expires. totalRevenue is exported and imported but never used (dead code that invites mutation).
Impact: Unbounded memory growth, since there's one key per user. The state is shared between requests and gets lost or diverges when running more than one instance.
Recommendation: Remove the cache (nothing reads it) and totalRevenue. If a cache is really needed, encapsulate it in an injected service with a limit/TTL. See Playbook #8.

### [MEDIUM] N+1 queries
File: src/AppManager.js:83, src/AppManager.js:92, src/AppManager.js:104, src/AppManager.js:106
Description: For each course, the report runs a query for its enrollments, and for each enrollment it runs 2 more queries (user and payment). That's 1 + C + 2E queries, coordinated with manual counters.
Impact: Response time grows linearly with the number of enrollments. The manual counters also make response ordering nondeterministic and are fragile (see the crash in the LOW finding).
Recommendation: Replace them with a single SELECT using LEFT JOINs across courses/enrollments/users/payments, and aggregate in the Service. See Playbook #9.

### [MEDIUM] Missing or inconsistent validation
File: src/AppManager.js:35, src/AppManager.js:131-137
Description: Checkout only checks that fields are present (no check on the card format, email, or c_id type, and pwd is optional). DELETE /api/users/:id doesn't validate the id, doesn't return 404 for a missing user, and leaves orphaned enrollments/payments.
Impact: Invalid data gets into the DB (a `card` that isn't a string crashes on `.startsWith`), and deleting a user leaves financial records pointing at a user that no longer exists.
Recommendation: Put validation in a dedicated function or module for checkout, and validate the id plus return 404 on delete. Handle the orphans (delete payments/enrollments in a transaction) inside the model. See Playbooks #6/#10.

### [MEDIUM] Configuration mixed with code
File: src/utils.js:1-7, src/AppManager.js:7
Description: The port (3000) and the DB path (':memory:') are hardcoded, mixed into the same object as the secrets, in a generic "utils" module.
Impact: You can't configure dev/test/prod without editing code, and there's no single config point.
Recommendation: Create src/config/index.js reading PORT, DB_PATH, PAYMENT_GATEWAY_KEY, etc. from process.env, with safe defaults only for non-secrets. See Playbook #2.

### [MEDIUM] Deprecated API/library in use
File: src/AppManager.js:11-137, package.json:10-11
Description: All data access uses the sqlite3 driver's pure callback API, which produces the 5-level callback pyramid in checkout and the report. Express is also on major 4 while Express 5 is the current stable line.
Impact: Errors get lost in the callbacks (there's no promise chaining or try/catch), transactions are impractical, and readability suffers.
Recommendation: Wrap the driver in a small promise adapter (util.promisify / new Promise around run/get/all), and use async/await in models and services. The modern equivalents are node:sqlite (Node ≥22.5) or better-sqlite3. Plan the move to Express 5 separately. See Playbook #12.

### [LOW] Generic exception swallowing errors
File: src/AppManager.js:38, src/AppManager.js:57, src/AppManager.js:92, src/AppManager.js:104, src/AppManager.js:106, src/AppManager.js:133
Description: DB errors are ignored (57, 104, 106, 133) or folded into a misleading response (38 returns 404 for a DB error). At 92, `err` is ignored and `enrollments.length` blows up with a TypeError if the query fails. The delete always answers success.
Impact: Real failures show up as success or as "not found", with nothing logged, and a DB failure in the report takes down the process.
Recommendation: Use async/await with a central error-handling middleware that logs and returns 500, plus a typed error (NotFound/Validation → 404/400). See Playbook #11.

### [LOW] Magic numbers/strings and poor naming
File: src/AppManager.js:26, src/AppManager.js:29-33, src/AppManager.js:46, src/AppManager.js:48, src/AppManager.js:108, src/utils.js:17-19
Description: One-letter or cryptic variables (u, e, p, cid, cc), the `self = this` workaround, the status literals "PAID"/"DENIED" scattered around, the rule "card starting with '4'" with no name, and the function name `badCrypto` with its magic 10000.
Impact: Readability suffers, a typo in a status silently breaks the report, and the payment rule is invisible to anyone reading the code.
Recommendation: Add constants (PAYMENT_STATUS.PAID/DENIED), a named function like isCardApproved(card) in the payment service, and descriptive names. Keep the JSON contract (usr/eml/pwd/c_id/card) and map only in the controller. See Playbook #10.

================================
Total: 12 findings
================================
