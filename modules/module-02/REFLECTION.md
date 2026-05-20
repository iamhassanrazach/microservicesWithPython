# Module 2 — Reflection

**Team name**: team-alpha
**Branch**: `module-02/team-alpha`
**Submitted**: before Module 3 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

You built a service with distinct layers: models, schemas, repository, service, and routes — each with a single responsibility.

**Why not just put everything in one file and call it done?**

Think about what happens six months later when someone new joins the team, or when you need to swap SQLite for PostgreSQL. What does the layered structure protect you from?

> If everything lived in one file, swapping SQLite for PostgreSQL in Module 8 would mean hunting through endpoint handlers to find every raw query. With the layered structure, that change is contained entirely in `database.py` and `repository.py` — routes and service logic don't know or care what database engine is underneath. The same argument applies to onboarding: a new developer can read `routes.py` and immediately understand the API surface without needing to understand how data is persisted. Each layer has a contract that the adjacent layers depend on, which means you can change an implementation without touching the interface.

---

## 2. Your choice

Each service owns its data exclusively — no other service is allowed to touch its database directly.

**Pick one entity your service owns (e.g. `User`, `Game`). What would go wrong if another service could write to that table directly?**

Give a concrete scenario, not a general principle.

> Imagine `activity-service` were allowed to write directly to the `games` table to update a play count column it added for its own convenience. Now `game-service` runs a migration that renames that column — and `activity-service` breaks silently at runtime with no compile-time warning. Even worse: `activity-service` might skip `game-service`'s validation logic entirely and insert a game with a null `title`, corrupting data that `game-service` returns to the frontend. Data ownership means there is exactly one place where the `games` table schema is defined, one place where writes are validated, and one place to look when something is wrong.

---

## 3. The tradeoff

You now have models, schemas, a repository, a service, and routes — five layers for what is essentially a CRUD service.

**For a system this small, what is the cost of all this structure?**

And at what point does the complexity start to pay off? Where is the tipping point?

> Right now the cost is real: adding a single new field means touching `models.py`, `schemas.py`, and possibly `repository.py` — three files for what could have been one line in a flat script. For a prototype or a weekend project, this is pure overhead. The structure starts paying off the moment the service has more than one developer, or more than one consumer. Once `activity-service` starts calling `game-service`, any change to the `GameOut` schema has downstream consequences that the layered contract makes explicit and testable. In this project the tipping point comes around Module 5 when inter-service communication begins — at that point, having a stable, well-defined API layer is no longer overhead, it is load-bearing.

---

*Keep this file. You will refer back to it during the oral presentation.*
