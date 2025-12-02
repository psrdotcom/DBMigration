## Contributing to DBMigration

Thank you for your interest in improving DBMigration. This document describes the
basic workflow for working on the project in a professional, consistent way.

### 1. Project Layout

- `agents/` – Agent system and LLM integration
- `src/` – Core migration logic and utilities
- `frontend/` – User interfaces (Streamlit chatbot, NL CLI wrapper)
- `scripts/` – Operational scripts for local setup and testing
- `infra/` – Infrastructure-as-code for AWS (Terraform, ECS task defs, secrets)
- `docs/` – Extended documentation and architecture notes
- `tests/` – Automated tests

### 2. Development Environment

1. Use a recent Python 3 (3.10+ recommended).
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

If you need LLM features:

```bash
pip install openai anthropic
```

### 3. Running the App Locally

- Interactive CLI:

```bash
python migrate.py --interactive
```

- Streamlit chatbot UI:

```bash
streamlit run frontend/chat_ui.py
```

### 4. Code Style & Quality

- Follow **PEP 8** and idiomatic Python practices.
- Prefer small, composable functions and clear docstrings.
- Log meaningful events using the existing `logging` setup.
- Avoid introducing breaking changes to the public CLI without updating docs.

### 5. Tests

- Place tests under `tests/`.
- Run the test suite before opening a PR:

```bash
python tests/test_basic.py
```

If you add new functionality, include or update tests to cover it.

### 6. Git & Pull Requests

- Use descriptive branch names, e.g. `feature/chatbot-enhancements` or `fix/oracle-connection`.
- Keep commits focused and well-described.
- In PR descriptions, briefly explain:
  - What you changed
  - Why you changed it
  - Any breaking changes or migration steps

### 7. Infrastructure Changes

- Place Terraform changes under `infra/terraform/`.
- Place ECS task definition examples under `infra/ecs/`.
- Do **not** commit real secrets; use placeholders and document required values.

### 8. Documentation

- Update `README.md` for user-facing changes.
- Use `docs/` for deeper architectural or setup guides.

By following these guidelines, we keep DBMigration maintainable, production-ready,
and approachable for new contributors.


