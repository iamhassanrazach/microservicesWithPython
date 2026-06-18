# Module 2 — Reflection

**Team name**: team-alpha
**Branch**: `module-02/<team-name>`
**Submitted**: before Module 3 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

Here are the completed reflection answers for Module 2 — FastAPI Service Design based on your implementation exercise. They are written in clean, cohesive paragraphs with no bullet points, ready to be added to your REFLECTION.md file.

Module 2 — Reflection
Team name: team-alpha

Branch: module-02/team-alpha

Submitted: before Module 3 lesson

1. The "why"
You built a service with distinct layers: models, schemas, repository, service, and routes — each with a single responsibility.

Why not just put everything in one file and call it done?

Putting everything into a single file quickly creates highly coupled, fragile code that becomes difficult to maintain as a team grows. The layered structure enforces strict boundaries that protect the application from cascading failures during refactoring. For example, if we need to swap SQLite for PostgreSQL, the repository layer abstracts all database-specific code, allowing us to update the data access logic without touching our business rules (service layer) or HTTP endpoints (routes layer). This separation of concerns means a new team member can confidently work on fixing an API response validation bug in the schema layer without needing to understand or risking breaking the underlying database queries.

2. Your choice
Each service owns its data exclusively — no other service is allowed to touch its database directly.

Pick one entity your service owns (e.g. User, Game). What would go wrong if another service could write to that table directly?

If an external service like the activity-service could bypass our API boundaries and write directly to the Game table, it would break data integrity and bypass critical business logic validation. For instance, our game-service might run business logic ensuring that every new Game entry must have a valid, reachable cover_url formatting check before saving. If another service inserts a row directly into the database with a null or corrupted URL string, it creates bad data that will cause the game-service to crash later when executing a standard GET /v1/games/{id} request, leaving the game-service team to debug a data corruption issue they did not cause.

3. The tradeoff
You now have models, schemas, a repository, a service, and routes — five layers for what is essentially a CRUD service.

For a system this small, what is the cost of all this structure?

For a minimal service with only four basic endpoints, this architecture introduces a heavy tax of boilerplate code and cognitive overhead. We are forced to write and maintain five different files, map data structures back and forth between Pydantic schemas and SQLAlchemy models, and pass variables through long call chains just to execute a simple database lookup. The tipping point where this complexity pays off occurs when business logic grows beyond basic CRUD, or when multiple developers begin committing code simultaneously. Once you introduce complex operations—such as multi-step validation, event publishing, or external third-party API dependencies—having dedicated layers ensures the codebase scales cleanly without turning the route handlers into an unmaintainable mess.

*Keep this file. You will refer back to it during the oral presentation.*
