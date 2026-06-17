## YOU NEED TO COMMIT THIS FILE BEFORE MOVING ON TO THE NEXT MODULE ! 🚨

**feel free to delete this comment**

# Module 1 — Reflection

**Team name**: team-alpha
**Branch**: `module-01/<team-alpha>`
**Submitted**: before Module 2 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

1. The "why"You started from a painful monolith. Now you're splitting it into separate services.What concrete problem does that split solve: and for whom?Splitting the monolith primarily solves the blast-radius problem for the end-user while dramatically speeding up delivery for deployment teams. In a monolith, a memory leak or an unhandled crash in a heavy, low-priority background process—like the activity logging or notifications system—could take down the entire application, preventing users from logging in or playing games. By decomposing the system, a failure in a secondary service remains isolated, allowing core services like identity and the game library to stay up and running flawlessly. Furthermore, deployment teams no longer face the logistical nightmare of coordinating a massive, slow release cycle just to update a single feature, as each microservice can now be deployed independently and continuously without risk to the rest of the application.  2. Your choiceLook at your service map. Every arrow between two services is a decision someone made.Pick one boundary, one place where you decided service A should not be part of service B. Explain why that line exists.We chose to draw a strict boundary between the activity-service and the logging-service, keeping them entirely isolated from one another. If these two services were merged back together, the high-throughput, latency-sensitive task of capturing real-time player actions would be tightly coupled to the heavy, compliance-heavy persistence layer required for long-term audit logs. Merging them would force the activity-service to deal directly with blocking disk operations or GDPR consent checks synchronously, destroying system performance and throughput. Separating them allows the activity-service to instantly offload events asynchronously via RabbitMQ, ensuring that logging bottlenecks or database maintenance windows never hinder the snappy responsiveness of live player tracking.  3. The tradeoffMicroservices solve the monolith's problems. But they create new ones.Name one thing that was simpler in the monolith and is now harder in your distributed design.The single hardest thing that was straightforward in the monolith but is now complex in our distributed design is managing consistent data flow and system observability across service boundaries. In a monolith, tracing a user action was a single synchronous execution path, and database transactions inherently guaranteed that data stayed uniform across all tables. Now, because requests enter through a centralized gateway and fan out asynchronously across multiple databases and protocols like REST and RabbitMQ, tracking down errors requires distributed tracing, while managing data means dealing with the administrative overhead of network failures, retries, and eventual consistency.  

_Keep this file. You will refer back to it during the oral presentation._
