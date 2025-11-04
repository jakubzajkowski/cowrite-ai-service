# Overall Instructions

You are assisting in developing a **FastAPI backend for an AI chat system**.

Follow the project's architecture, naming conventions, and repository structure.
Prefer **async functions**, **dependency injection** via `Depends`, and **clean, consistent error handling** using `HTTPException` or custom error classes.

Always generate **clear and well-structured docstrings** for:
- modules (`"""Module description."""`)
- classes (`"""Class description and purpose."""`)
- methods and functions (`"""Args, Returns, Raises, Examples."""`)

Use triple double quotes (`"""`) for all Python docstrings, following **PEP 257** and **Google-style docstring format**.

---

# Architecture Overview

This service is a **FastAPI backend** for an AI-powered chat system.

It uses:
- `FastAPI` for API routing, dependency injection, and WebSocket endpoints.
- `SQLAlchemy Async ORM` for asynchronous database operations.
- `ChromaDB` for vector embeddings and semantic search.
- `AWS S3` or `LocalStack` for file upload and storage.
- `WebSockets` for real-time chat streaming.
- `Pydantic` models for validation and schema definitions.
- `Celery` (optional) for background file embedding or long-running tasks.

Keep code modular and organized by layers:
```
/app
  ├── api/            # Routers (REST + WebSocket)
  ├── core/           # Settings, configs, startup events
  ├── db/             # SQLAlchemy engine, models, repositories
  ├── schemas/        # Pydantic models
  ├── services/       # Business logic, AI, file, chat, embeddings
  ├── utils/          # Helpers, tools, constants
  └── main.py         # Entry point
```

---

# Documentation & Code Style Rules

- Every **class**, **function**, and **file** must include a descriptive docstring.
- Use **Google-style** docstrings:

  ```python
  class FileService:
      """Handles file uploads, processing, and embedding creation."""

      async def upload_file(self, file: UploadFile) -> FileResponse:
          """Uploads a file to S3 and stores metadata in the database.

          Args:
              file (UploadFile): Uploaded file object.

          Returns:
              FileResponse: Metadata of the uploaded file.

          Raises:
              HTTPException: If the upload or processing fails.
          """
  ```

- Add short **inline comments** (`#`) for key logic steps inside complex methods.
- Keep line length under 100 characters.

---

# Naming Conventions

- Modules: `snake_case.py`
- Classes: `PascalCase`
- Variables and functions: `snake_case`
- Async functions must start with `async def`.
- Private helpers use leading underscore (e.g., `_process_embedding()`).

---

# Error Handling

- Use FastAPI’s `HTTPException` with clear messages and status codes.
- Log all server-side exceptions with context.
- Return typed `ErrorResponse` schemas for consistency.

---

# AI Chat Context

- Store embeddings in ChromaDB; associate them with `conversation_id`.
- Upload files to S3/LocalStack before processing embeddings.
- Use async background task for embedding generation.
- Maintain message context by conversation ID.
- WebSocket connections handle streaming responses from the AI.

---

# Testing & Maintainability

- Write unit tests with `pytest` using async fixtures.
- Mock S3 and ChromaDB for tests.
- Keep functions small and cohesive.
- Always type annotate all function signatures.

---

# Example Prompt Behavior

When creating a new service class, Copilot should:

1. Include a module-level docstring describing purpose.
2. Generate a class with a clear single responsibility.
3. Add Google-style docstrings for all public methods.
4. Include comments for important steps in logic flow.

---

# Example

```python
"""Service responsible for handling AI chat message processing and response generation."""

class ChatService:
    """Handles message flow between users, AI model, and conversation history."""

    def __init__(self, model_client: AIModelClient, db: AsyncSession):
        """Initialize ChatService.

        Args:
            model_client (AIModelClient): Client for LLM or AI model.
            db (AsyncSession): Database session for persisting chat history.
        """
        self.model_client = model_client
        self.db = db

    async def process_message(self, conversation_id: int, content: str) -> str:
        """Processes an incoming message, sends it to the AI model, and saves the response.

        Args:
            conversation_id (int): The ID of the active conversation.
            content (str): The user message to process.

        Returns:
            str: The AI-generated response message.
        """
        # 1. Save incoming message
        # 2. Call AI model
        # 3. Store AI response in DB
        # 4. Return response text
```

---

# Final Notes

- Be consistent.
- Generate meaningful names.
- Always include docstrings and comments.
- Follow project conventions and keep modules cohesive.
