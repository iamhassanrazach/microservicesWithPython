# Module 6 — Reflection

**Team name**: team-alpha
**Branch**: `module-06/<team-alpha>`
**Submitted**: before Module 7 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

1. The "why"
The gateway now validates every JWT before forwarding a request. Individual services no longer need to check identity themselves.

What does centralising authentication at the gateway buy you?

Centralizing authentication at the gateway offloads the burden of identity verification from downstream services, preventing unauthenticated traffic from wasting internal network and compute resources. The gateway acts as a perimeter guard that handles global token validation, meaning that if a secret key needs to be rotated, it only needs to be updated in one configuration rather than across ten separate codebases. This separation of concerns allows individual downstream services to focus entirely on fine-grained, domain-specific authorization—such as checking specific admin roles for a DELETE route—while remaining decoupled from the underlying authentication mechanism.

2. Your choice
When activity-service calls user-service internally, it uses a Machine-to-Machine (M2M) token — not a user's token.

Why can't it just reuse the user's token that arrived in the original request?

Reusing a user's token for internal service-to-service communication creates severe security risks and fragile request lifecycles. If a user logs out or their session expires mid-way through a complex, multi-service asynchronous call chain, the forwarded token becomes invalid, causing subsequent internal steps to unexpectedly fail. Utilizing dedicated Machine-to-Machine tokens establishes distinct service identities, enabling precise audit logging, targeted rate-limiting, and independent access revocation between microservices without conflating system-level operations with individual user actions.

3. The tradeoff
The gateway and the auth-service share the same SECRET_KEY to verify tokens without making a network call on every request.

What is the security risk of sharing this key?

Sharing a single secret key across the gateway and downstream services introduces a single point of failure where a leak exposes the entire ecosystem; an attacker possessing the key could forge valid tokens with administrative privileges that any service would trust implicitly without validation. However, the alternative of making a synchronous network call to the authentication service for every single incoming request introduces significant network latency and turns the auth service into a massive performance bottleneck. Local verification via the shared secret maximizes system availability and speed by eliminating these costly internal HTTP roundtrips, representing a conscious tradeoff of increased security risk for vastly superior performance.

*Keep this file. You will refer back to it during the oral presentation.*
