# User‑API Simulator

A lightweight **FastAPI** server + **Python client** that simulates Aqua’s product for automation engineers.  
Features:

* CRUD users (`POST /users`, `GET /users/{id}`, `GET /users`)
* **DELETE /users** — maintenance endpoint (wipes all users)
* Health probe (`GET /health`)
* JWT authentication (`/token`)
* Strict validation (Israeli ID, phone, etc.)
* Structured logging
* Docker‑ready
* Comprehensive tests (unit, integration, E2E)
* A Postman environment file with common operations

---

## QuickStart

### 1 Docker

```bash
docker build -t user-api .
docker run -p 8000:8000 user-api
````

Browse docs at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

### 2 Local dev

```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt        # includes pytest
uvicorn app.main:app --reload
```

> **Credentials:** `admin / admin` (demo only)

### 3 Run tests

```bash
pytest -v            # spins up a real Uvicorn server, runs full suite
```

The session fixture auto‑cleans the DB by calling `DELETE /users` after tests.

---

## Endpoints (JWT required✱)

| Method | Path        | Purpose                          |
| ------ | ----------- | -------------------------------- |
| GET    | /health     | Liveness check (no auth)         |
| POST   | /token      | Obtain JWT (OAuth2 PW flow)      |
| POST   | /users      | Create user                      |
| GET    | /users/{id} | Fetch user                       |
| GET    | /users      | List user IDs                    |
| DELETE | /users      | **Dangerous!** Purge all users▲ |

✱Add header: `Authorization: Bearer <token>`
▲Enabled for simulator/testing; gate or remove in production.

---

## Config (envvars)

| Name                          | Default                | Notes                                      |
| ----------------------------- | ---------------------- | ------------------------------------------ |
| `DATABASE_URL`                | `sqlite:///./users.db` | Any SQLAlchemy URL; tests force `:memory:` |
| `SECRET_KEY`                  | `change-me-in-prod`    | JWT HMAC key– **override in prod**        |
| `ACCESS_TOKEN_EXPIRE_SECONDS` | `3600`                 | Token TTL                                  |

`.env` is supported via *pydantic‑settings*.

---

## ProjectLayout

```
app/
  ├─ main.py        (routes & FastAPI app)
  ├─ models.py      (SQLAlchemy ORM)
  ├─ schemas.py     (Pydantic validation)
  ├─ auth.py        (JWT helpers)
  ├─ client.py      (Python APIClient)
  └─ config.py      (Settings via env / .env)
tests/
  ├─ test_api.py    (E2E CRUD via live Uvicorn)
  └─ test_unit.py   (validation + utils)
das.postman_environment.json
Dockerfile
requirements.txt
README.md
```

---

## DesignNotes

* **FastAPI** for async speed & auto‑docs (OpenAPI/Swagger).
* **SQLite** ships in‑proc ⇒ zero setup; swap to Postgres via `DATABASE_URL`.
* **JWT** == stateless auth → perfect for horizontal scaling.
* Structured **logging** with scope + status in each line.
* Tests share one Uvicorn instance on a random port ⇒ fast and parallel‑safe.
* `DELETE /users` exists only for tests ⇢ restrict/remove in real deployments.

### Road‑map

1. Plug a real user store (Postgres + Alembic migrations).
2. Role‑based auth (admin vs tester).
3. DockerCompose with Traefik + TLS for staging.
4. Metrics middleware (Prometheus) + tracing (OpenTelemetry).
5. Replace SQLAlchemy repo with MongoDB (document model) if flexible user profiles are required.

---

©2025Adi Ghoummed • MIT License

```
```
