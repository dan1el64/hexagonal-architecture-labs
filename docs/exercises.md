# Extension exercises

Use these as interview demonstrations or follow-up projects. They are proposals, not implemented capabilities.

1. Add an HTTP inbound adapter for inventory. Map validation errors to 400, missing stock to 409 and successful reservations to 201 without importing the HTTP framework into the core. Test request replay through HTTP.
2. Add a PostgreSQL reservation adapter and run the same contract tests against it. Verify concurrent reservations and rollback after an insert failure.
3. Implement reservation expiration with an injected clock. Test expiration boundaries without sleeping.
4. Implement the inventory use case again in NestJS or Spring Boot. Keep dependency injection decorators and JPA/ORM entities outside the domain; compare complexity with this small Python version.
5. Add a response provider using an LLM API only after selecting a model, privacy policy and budget. Test it through a local fake server, including timeouts and 429 errors.
6. Build a separate safe code-evaluation environment with synthetic tasks, a versioned rubric and independently reviewed expected results. Explain false positives and false negatives rather than presenting a single unexplained score.

Portfolio case study outline: problem, constraints, diagram, one important tradeoff, reproduction commands, observed test results and remaining limitations. Link the case study from https://www.dan1el64.com/.
