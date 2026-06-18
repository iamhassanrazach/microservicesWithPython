# Module 4 — Reflection

**Team name**: team-alpha
**Branch**: `module-04/team-alpha`
**Submitted**: before Module 5 lesson

---

## 1. The "why"

In Module 3, activity-service had to wait for every downstream call to complete before returning a response. If notification-service were slow or temporarily down, the whole activity creation would block or fail along with it.

By publishing to RabbitMQ instead, activity-service saves the activity and returns 201 immediately — it doesn't care whether notification-service is running. Under load, this means activity creation latency stays flat regardless of how many notifications are queued. From notification-service's side, it gets to consume messages whenever it's ready: if it crashes and restarts, the messages are still sitting durably in the queue waiting for it. Neither service is held hostage by the other's availability.

---

## 2. Your choice

We already knew how to call a service over HTTP — we did it for user validation and game enrichment in Module 3. The difference is that those calls are *part of the response*: if user-service is down, the request should fail. Notifications are different — they're a side effect, not part of the answer.

A direct HTTP call to notification-service would mean: if it's slow, our endpoint is slow. If it crashes mid-request, the notification is silently lost with no way to retry. The broker gives us two things HTTP can't: **durability** (the message survives a crash because RabbitMQ stores it on disk) and **decoupling** (notification-service can be down for an hour and catch up when it comes back). With HTTP, the window to deliver is the duration of the request. With a broker, that window is "whenever the consumer is ready."

---

## 3. The tradeoff

With a synchronous REST call we get an HTTP status code — success or failure, right now. With async messaging we get nothing back. The activity is saved and the message is published, but we have no confirmation it was ever consumed, let alone that the notification was stored.

From the user's perspective: they will never see an error if a notification fails to deliver — the 201 response looks identical whether the message was consumed or dropped. From the developer's perspective: you'd only notice a missing notification by manually querying the notification-service DB or watching consumer logs. 

To recover this visibility you need: **consumer acknowledgements** (so RabbitMQ knows the message was handled, not just received), a **dead-letter queue** (to catch messages that failed processing), and **structured logging or metrics** on the consumer side. Without those three things, a dropped notification leaves no trace anywhere in the system.

---

*Keep this file. You will refer back to it during the oral presentation.*
