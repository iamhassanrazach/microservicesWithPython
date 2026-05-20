# Module 1 — Service Decomposition

**Duration**: 2h in class
**Branch to submit**: `module-01/<team-name>`

---

## Objective

Before writing a single line of code, you need to design the system on paper. Every decision you make here: where to draw service boundaries, who owns what data, how services talk to each other, is hard to reverse once you start coding.

This module is about slowing down and thinking like an architect, not a developer.

Read these two documents before doing anything else:

- `docs/domain.md` — what GameHub is and who uses it
- `docs/specs.md` — the tech stack and key architectural decisions

> The CTO has already laid out the `services/` folder structure. Use it as a starting point, but your job is to **justify** why each folder deserves to be its own service — not just accept it.

---

## Task 1 — Identify bounded contexts _(~40 min)_

A bounded context is a part of the system that has a clear responsibility and owns its data exclusively. No other service should reach into its database.

For each bounded context you identify, fill in the table:

| Bounded Context | Responsibilities | Owned Entities | Team |
| --------------- | ---------------- | -------------- | ---- |
| Identity | Manages who users are, handles registration and profiles | User, Session | Platform |
| Game Library | Manages the game catalogue: adding games, searching by title or genre, serving game metadata to other services | Game | Catalogue |
| Activity Tracking | Records what users do with games (played, completed, reviewed, wishlisted); owns the activity feed and per-user history; enriches activities with game data fetched at request time | Activity | Engagement |
| Notifications | Receives activity events asynchronously and stores in-app notifications; marks notifications as read | Notification | Messaging |
| Audit & Compliance | Records user activity for legal traceability; enforces GDPR consent before storing any event; handles right-to-erasure requests | ConsentRecord, ActivityLog | Legal / Platform |
| Authentication | Issues and validates JWT tokens; stores credentials; cross-cutting concern consumed by every other service and the gateway | Credential, Token | Platform |

There is no single correct answer: what matters is that you can justify each row.

---

## Task 2 — Define service contracts _(~30 min)_

For each pair of services that need to communicate, define:

- **Direction**: A → B
- **Trigger**: what causes the call
- **Protocol**: REST or event (async)
- **Payload**: key fields exchanged

---

**Contract 1**

```
gateway → auth-service
Trigger: every inbound request carrying an Authorization header
Protocol: REST (synchronous — the request cannot proceed until the token is validated)
Payload: { token: "<jwt>" }
Response: { sub, role, exp } or 401
```

**Contract 2**

```
activity-service → game-service
Trigger: a POST /v1/activities request arrives; activity-service needs game metadata to enrich its response
Protocol: REST via httpx (synchronous — but degraded gracefully: if game-service is unreachable, return activity with "game": null)
Payload: GET /v1/games/{game_id}
Response: { id, title, genre, platform, cover_url }
```

**Contract 3**

```
activity-service → notification-service  (via RabbitMQ)
Trigger: an activity is successfully persisted
Protocol: RabbitMQ message, queue "gamehub.notifications" (async — logging must not block the HTTP response; a slow or crashed notification consumer should not affect the caller)
Payload: { user_id, message }
```

**Contract 4**

```
activity-service → logging-service  (via RabbitMQ)
Trigger: an activity is successfully persisted
Protocol: RabbitMQ message (async — same reasoning as above; additionally, logging-service must check consent before writing, which is a side-effect that should not block the primary flow)
Payload: { activity_id, user_id, action, game_id, timestamp }
```

**Contract 5**

```
gateway → user-service / game-service / activity-service
Trigger: client makes any CRUD request after authentication
Protocol: REST (synchronous — path-based routing: /v1/users → user-service, /v1/games → game-service, /v1/activities → activity-service)
Payload: forwarded verbatim from the client, with the validated JWT claims optionally injected as a header
```

Focus on the flows that feel non-obvious. You do not need to document every possible pair.

---

## Task 3 — Draw the service map _(~20 min)_

Draw the full GameHub service map:

- One box per service
- Arrows between services (solid line = synchronous REST, dashed line = async event)
- Label each arrow with its protocol
- One box at the top labelled **gateway** — all client requests enter here, no client ever calls a service directly

```
                         ┌─────────────────────────────┐
     HTTP ──────────────▶│  gateway  (port 8000)       │
                         │  JWT validation             │
                         │  path-based routing         │
                         │  circuit breakers           │
                         └──────┬───────┬──────┬───────┘
                                │ REST  │      │ REST
                    ┌───────────┘       │      └──────────────┐
                    ▼                   ▼                      ▼
             ┌────────────┐    ┌────────────────┐    ┌──────────────┐
             │user-service│    │  game-service  │    │auth-service  │
             │ port 8001  │    │  port 8002     │    │  port 8005   │
             └────────────┘    └────────────────┘    └──────────────┘
                                       ▲ REST (httpx)
                                       │
                         ┌─────────────────────────┐
                         │   activity-service      │
                         │   port 8003             │
                         └────────────┬────────────┘
                                      │
                          RabbitMQ (async publish)
                        ┌─────────────┴──────────────┐
                        ▼                             ▼
          ┌─────────────────────┐     ┌───────────────────────┐
          │ notification-service│     │   logging-service     │
          │ port 8004  Node.js  │     │   port 8006  Flask    │
          │ RabbitMQ consumer   │     │   GDPR consent check  │
          └─────────────────────┘     └───────────────────────┘
```

Solid arrows = synchronous REST. Dashed / labelled arrows = async RabbitMQ events.

---

## Discussion _(~15 min)_

Three questions to discuss as a team before you leave:

1. Why does `notification-service` use Node.js instead of Python like the rest? What does that tell you about microservices and technology choices?
2. What is the risk of `activity-service` calling `logging-service` synchronously — why might you prefer an async event instead?
3. Why does `logging-service` need a GDPR consent check before recording any activity?

You do not need to write these answers down — they are warm-up for your REFLECTION.md.

**Discussion notes:**

1. `notification-service` uses Node.js to demonstrate that microservices decouple technology choices from the rest of the system. Each service is a black box behind an API contract — the rest of the system doesn't care what language runs inside it. In practice, a team with existing Node.js expertise or a library that only exists in the Node ecosystem can own their service without dragging everyone else onto a new stack.

2. If `activity-service` called `logging-service` synchronously, every activity write would block on the logging network round-trip. A slow or temporarily down `logging-service` would cause activity writes to time out or fail — a GDPR audit concern leaking into user-facing latency. With an async event, `activity-service` publishes and returns immediately; `logging-service` processes at its own pace. The two services fail independently.

3. Recording user activity without consent violates GDPR Article 6 (lawfulness of processing). The logging-service must check consent before persisting any event so that a user who has opted out is never tracked, even if the upstream services fire events for their actions. This also supports the right-to-erasure endpoint: if consent is withdrawn, the service knows exactly which records to delete.

---

## Minimum to submit this branch

- [x] Bounded context table filled in (at least 4 services justified)
- [x] At least 3 service contracts defined
- [x] Service map committed (sketch, photo, or ASCII)
- [x] `REFLECTION.md` completed and committed

The map does not need to be perfect. It needs to be yours.
