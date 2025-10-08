# Migrations Management

This directory contains database migration scripts managed by Alembic.

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create a new migration (autogenerate based on models)
```bash
alembic revision --autogenerate -m "description of changes"
```

### 3. Apply migrations
```bash
alembic upgrade head
```

### 4. Downgrade migrations
```bash
alembic downgrade -1  # Go back one revision
alembic downgrade base  # Go back to the beginning
```

## Common Commands

- `alembic current` - Show current revision
- `alembic history` - Show migration history
- `alembic upgrade <revision>` - Upgrade to specific revision
- `alembic downgrade <revision>` - Downgrade to specific revision
- `alembic stamp head` - Mark database as up to date without running migrations

## Manual Migration Creation

If you need more control, create an empty migration:
```bash
alembic revision -m "description"
```

Then edit the generated file in `alembic/versions/` to add your custom migration logic.
