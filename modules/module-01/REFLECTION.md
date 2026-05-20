## YOU NEED TO COMMIT THIS FILE BEFORE MOVING ON TO THE NEXT MODULE ! 🚨

**feel free to delete this comment**

# Module 1 — Reflection

**Team name**: **team-alpha**
**Branch**: `module-01/team-alpha`
**Submitted**: before Module 2 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

You started from a painful monolith. Now you're splitting it into separate services.

**What concrete problem does that split solve: and for whom?**

Think about it from three angles: the developer who has to change code, the team that has to deploy it, and the user who has to live with its failures. You don't need to cover all three, pick the one that felt most real to you today.

> From the team's perspective, the split solves the problem of deployment coupling. In a monolith, a bug fix in the notification logic forces you to redeploy the entire application — including the user registration and game catalogue code that had nothing to do with the change. In GameHub, we can push a fix to `notification-service` without touching anything else. The team owning that service can ship independently without coordinating with three other teams or risking a regression in unrelated features. That autonomy is what makes the architecture worth its added complexity.

---

## 2. Your choice

Look at your service map. Every arrow between two services is a decision someone made.

**Pick one boundary, one place where you decided service A should not be part of service B. Explain why that line exists.**

What would break, slow down, or become harder to manage if you merged those two services back together?

> We kept `auth-service` separate from `user-service`, even though both deal with "users" in some sense. The line exists because authentication (issuing and validating JWT tokens) is a cross-cutting concern — every other service needs to verify tokens, and none of them should have to call `user-service` to do it. If we merged the two, every service would take a runtime dependency on the user database just to check a bearer token. Changing the password-hashing strategy or rotating the secret key would require coordinating a deploy of the combined service at the exact moment every consumer is ready. Keeping `auth-service` isolated means the token contract is stable and small, and the user profile logic can evolve independently.

---

## 3. The tradeoff

Microservices solve the monolith's problems. But they create new ones.

**Name one thing that was simpler in the monolith and is now harder in your distributed design.**

No need to solve it: just name it honestly. This is exactly the tension the rest of the course is about.

> Tracing a single user action end-to-end. In the monolith, a stack trace in a log file told you everything — one process, one call stack. In GameHub, a user logging an activity triggers a REST call to `game-service`, an async publish to RabbitMQ consumed by both `notification-service` and `logging-service`, and a JWT check against `auth-service`. If something goes wrong, those events are scattered across at least four separate log streams with no shared thread ID. Correlating them requires distributed tracing tooling (which is exactly why Jaeger is in the infra stack) — but that's infrastructure and discipline that the monolith simply didn't need.

---

_Keep this file. You will refer back to it during the oral presentation._
