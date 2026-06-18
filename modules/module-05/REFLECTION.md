# Module 5 — Reflection

**Team name**: team-alpha
**Branch**: `module-05/<team-alpha>`
**Submitted**: before Module 6 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

1. The "why"
The game-service now has two models for the same data: SQLite for writes, Redis for reads. They store the same games in two different shapes.

Why go through the trouble of maintaining two representations of the same data?

Maintaining two separate representations allows us to optimize for entirely different system demands. The write model (SQLite) ensures transactional consistency and stores a complete, comprehensive record of the data on disk, including operational metadata like creation timestamps. In contrast, the read model (Redis) is highly optimized for high-traffic, low-latency lookups by keeping a stripped-down, lightweight summary shape entirely in memory. Eliminating unnecessary fields and avoiding heavy relational joins or disk I/O drastically reduces payload sizes and CPU overhead, allowing the system to easily handle thousands of concurrent read requests—such as a leaderboard hit—without bottlenecking the primary database.

2. Your choice
The logging-service checks GDPR consent before recording any activity. If a user has not opted in, the log is silently dropped.

What does this consent check force you to accept about your data?

This design forces us to accept that our analytical data is permanently incomplete by design, meaning we must tolerate gaps in user activity trails for compliance reasons. Enforcing this compliance check within the logging-service consumer is highly resilient because it serves as a final, secure gatekeeper right before the database write, preventing accidental persistence regardless of how the activity data was produced. Moving the check earlier to the activity-service before publishing to RabbitMQ would save network and message broker bandwidth, but it couples the activity-service tightly to compliance logic. Doing it at the gateway is impractical because the gateway typically handles synchronous HTTP requests and lacks the contextual awareness or direct asynchronous database access required to evaluate transient event streams efficiently.

3. The tradeoff
With CQRS, your write model and read model can drift out of sync — a game is updated in SQLite but the Redis projection still shows the old data.

In what scenario does this inconsistency matter to the user? In what scenario is it completely acceptable?

Data drift and temporary inconsistency are perfectly acceptable for non-critical informational fields, such as a game's genre or platform details, where a slight delay in updating the public UI has virtually zero negative business impact. However, this inconsistency becomes completely unacceptable in scenarios where accurate real-time states dictate critical operations, such as financial transactions, account balances, or e-commerce inventory counts where selling out-of-stock items causes immediate failure. For applications dealing with financial ledger integrity, healthcare records, or safety-critical tracking, strong consistency is mandatory because reading stale data can result in severe financial or operational damage.

---

*Keep this file. You will refer back to it during the oral presentation.*
