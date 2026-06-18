# Module 3 — Reflection

**Team name**: team-alpha
**Branch**: `module-03/<team-name>`
**Submitted**: before Module 4 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

All client requests now go through the gateway. No client ever calls a service directly.

**Why does that single entry point exist? What would the client's life look like without it?**

Think about what the client would need to know and manage if it talked to each service on its own port.

> Having a single entry point decouples the client from our internal microservice network topology and hides system complexity behind a unified API interface. Without the gateway, the client's life would be an administrative nightmare, as it would need to keep track of a complex matrix of separate domain URLs and ports—such as port 8001 for users and port 8002 for games. Every time we scale a service, split an existing bounded context, or migrate a backend node to a new server, the client codebase would break unless updated. By abstracting this with a gateway routing dictionary, we can seamlessly update or move our internal infrastructure while the client continues interacting with a single, stable, and predictable base URL

---

## 2. Your choice

The activity-service makes two outbound calls: one to validate the user (with retry logic), one to fetch game data (with a null fallback if it fails).

**Why are these two calls treated differently? Why does one retry and the other just give up gracefully?**

What is the consequence for the user in each case if the downstream service is unavailable?

> These two calls are handled differently because user validation impacts fundamental data correctness, whereas game data enrichment is non-essential for the operation's survival. User validation is a critical prerequisite; recording an activity for a user ID that does not exist results in broken or orphaned relational data, making it necessary to retry against transient network blips before aborting with an error. Conversely, the lack of game metadata is minor and non-blocking, so fallback logic handles it gracefully by returning a null value and saving the record anyway. Giving up immediately on game enrichment avoids unnecessary delays, allowing the system to accept incoming logs even if the game library service goes offline.

---

## 3. The tradeoff

Every time a client creates an activity, three services are involved synchronously. They all have to be running, healthy, and fast.

**What is the systemic risk of chaining synchronous calls like this?**

What happens to the user experience if the slowest service in the chain takes 3 seconds to respond?

> *The core systemic risk of chaining synchronous calls is tight temporal coupling, where the availability and performance of the entire request chain become dependent on its weakest link. If any downstream service fails or becomes bottlenecked, it triggers a cascading delay that travels backward up through the gateway, locking up server threads and exhausting client-side connection pools. If a single downstream service in this chain experiences high latency and takes 3 seconds to respond, the entire user experience grinds to a halt. This turns an otherwise quick activity-logging request into a sluggish 3+ second execution path, severely impacting the perceived performance of the frontend application.

---

*Keep this file. You will refer back to it during the oral presentation.*
