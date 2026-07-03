# Here is the  Repository for SafeAgent a multi-layered defense system for AI cognitive firewall

## project architecture here🏗️:
[🏗️View Project Architecture](./docs/architecture.md)

[🏗️View Performance Example](./performance.png)


*Progress so far for prompt endpoint:*
- Prompt endpoint creation
- leetspeak stripping and prompt normalization
- Some Block Policies
- ReGo engine for OPA evaluation
- Testing of various prompt Cases
- sanitization and detection
- merge sanitize and block to one object
- add AsyncClient and YAML loading to api lifespan
- Creating of PostgreSQL database and async logging
- Creation of PostgreSQL models and integration with FastAPI using SQLAlchemy 2.0 and psycopg3
- Redis integration for LLM memory
- Tool output detection endpoint
- prompt output endpoint to ensure LLM does not spit out sensitive information
- Injection and Jailbreak dataset cleaned and ready for ML


*up next:*
- Train logistic regression algorithm to catch more prompt injection and jailbreak attempts
- creating UDS for OPA and API

- create frontend 
### *WARNING⚠️⚠️:* Created a list of sanitized words the entropy redacts to append into the PostgreSQL for analysis later on. This will help us see and confirm that entropy is working as intended although it has been working as expected so far. This is for development purposes only and will be removed once it is ready to go into production. PS: do not use real secret words in testing phase as they might be logged in database



