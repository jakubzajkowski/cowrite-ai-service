# AI Service

The **AI Service** is a core microservice of the **CoWrite** platform.  
Its main responsibility is to manage communication with AI models and provide asynchronous, low-latency responses back to the client through **WebSockets**.  

This service is designed for scalability and maintainability, with strict development workflows, automated migrations, and CI/CD pipelines.

---

## 🚀 Features

- **AI Integration**: Handles requests to AI models (e.g., Gemini API) and streams results back to clients.
- **WebSockets**: Provides real-time, asynchronous communication for faster and interactive user experiences.
- **Database Support**: Uses PostgreSQL with **SQLAlchemy** and **Alembic** for migrations.
- **CI/CD Ready**: Includes GitHub Actions for linting, formatting, and running tests.
- **Developer-Friendly**: Enforces code style (Black, Pylint) and test coverage (Pytest).

---

## ⚙️ Tech Stack

- **Python 3.11+**
- **FastAPI** with Uvicorn ASGI server
- **WebSockets** for async streaming
- **PostgreSQL** with `asyncpg` driver
- **SQLAlchemy** ORM + **Alembic** migrations
- **Pytest** for testing
- **Black** + **Pylint** for code quality
- **GitHub Actions** for automation

---

## 📦 Environment Variables

Create a `.env` file or export these variables before running:

```env
GEMINI_API_KEY=your_api_key_here
USER_SERVICE_URL=http://localhost:8080
USER_COOKIE_NAME=COWRITE_SESSION_ID
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:5432/db_name
```

# 🛠️ Development

### Run the service
```bash
uvicorn app.main:app --reload
```
### Run tests
```bash
pytest
```
### Linting
```bash
pylint app/ tests/
black --check app/ tests/
```
### Auto-format code
```bash
black app/ tests/
```
## 📂 Database Migrations (Alembic)
```bash
alembic revision --autogenerate -m "your message"
alembic upgrade head
alembic downgrade -1
alembic history
Show current revision
alembic current
python -m app.db.migrations
```
## ✅ CI/CD
GitHub Actions pipeline runs automatically on each push and pull request:

Code linting (Pylint + Black)
Test suite (Pytest)
Build verification
Docker image build and push to Docker Hub

This ensures that code merged into the main branch is clean, consistent, stable, and available as a container image on Docker Hub.