# LMS Telegram Bot - Development Plan

## Overview

This document outlines the implementation plan for the LMS Telegram bot across four tasks. The bot allows users to interact with the LMS backend through Telegram, checking system health, browsing labs and scores, and asking questions in plain language using an LLM for intent recognition.

---

## Task 1: Project Scaffold (Current Task)

**Goal:** Create a testable project structure with placeholder handlers.

### Approach

1. **Testable Handler Architecture**: Handlers are pure functions that take input and return text. They have no Telegram dependencies, making them testable via CLI (`--test` mode), unit tests, and reusable in the actual Telegram bot.

2. **Project Structure**:
   - `bot.py` - Entry point with `--test` mode support
   - `handlers/` - Command handlers (no Telegram dependency)
   - `services/` - External API clients (LMS API, LLM)
   - `config.py` - Environment variable loading with pydantic-settings

3. **CLI Test Mode**: The `--test` flag allows offline testing without Telegram. Commands like `uv run bot.py --test "/start"` call handlers directly and print results to stdout.

### Deliverables
- [x] `bot/bot.py` with `--test` mode
- [x] `bot/handlers/commands.py` with placeholder handlers
- [x] `bot/config.py` for configuration
- [x] `bot/services/` directory structure
- [x] `bot/.env.bot.example` template
- [x] `bot/pyproject.toml` with dependencies
- [x] This `PLAN.md`

---

## Task 2: Backend Integration

**Goal:** Connect handlers to the real LMS backend API.

### Approach

1. **API Client Pattern**: Implement `LMSAPIClient` in `services/lms_api.py` with:
   - Bearer token authentication (using `LMS_API_KEY`)
   - Base URL from config (no hardcoded URLs)
   - Methods: `health_check()`, `get_labs()`, `get_scores(lab_id)`
   - Centralized error handling with friendly messages

2. **Update Handlers**: Replace placeholder text in handlers with real API calls:
   - `/health` → `GET /pipeline/health` or similar
   - `/labs` → `GET /items` (filtered for labs)
   - `/scores <lab>` → `GET /analytics/scores?lab=<lab>`

3. **Error Handling**: When the backend is down, return friendly messages like "The LMS backend is currently unavailable. Please try again later." instead of crashing with a traceback.

### Key Decisions
- Use `httpx` for async HTTP requests (non-blocking for Telegram)
- Singleton pattern for API client (one instance shared across handlers)
- Handlers remain testable - mock the API client in tests

---

## Task 3: LLM Intent Routing

**Goal:** Enable natural language queries using LLM tool calling.

### Approach

1. **Tool Definitions**: Define each backend action as an LLM tool with clear descriptions:
   ```python
   {
       "name": "get_labs",
       "description": "List all available labs in the LMS",
       "parameters": {}
   }
   ```

2. **Intent Router**: When a message doesn't start with `/`, send it to the LLM with available tools. The LLM decides which tool to call based on the user's intent.

3. **Tool Execution**: Execute the tool the LLM selects and return the result.

### Why Tool Calling?
- The LLM reads tool descriptions to decide what to call
- No regex or keyword matching in our code
- Flexible: adding a new capability = adding a new tool definition
- The LLM handles variations like "show labs", "what labs exist", "list available labs"

### Key Insight
If the LLM picks the wrong tool, fix the tool description - don't add regex routing. The description quality determines routing accuracy.

---

## Task 4: Docker Deployment

**Goal:** Containerize the bot and deploy alongside the backend.

### Approach

1. **Dockerfile**: Create a multi-stage build:
   - Stage 1: Install dependencies with `uv`
   - Stage 2: Copy only necessary files, run with minimal image

2. **docker-compose.yml**: Add bot as a new service:
   ```yaml
   services:
     bot:
       build: ./bot
       env_file: .env.docker.secret
       depends_on: [backend]
   ```

3. **Docker Networking**: Containers communicate via service names (`backend`, not `localhost`). Update `LMS_API_BASE_URL` to `http://backend:42002`.

4. **Health Checks**: Add Docker health checks to ensure the bot is responsive.

### Deployment Steps
1. Build: `docker compose build`
2. Start: `docker compose up -d`
3. Verify: `docker compose logs bot`
4. Test in Telegram

---

## Testing Strategy

### Unit Tests
- Test handlers with mocked API clients
- Test config loading
- Test API client error handling

### Integration Tests
- `--test` mode for manual CLI testing
- End-to-end tests with real backend (staging environment)

### Telegram Testing
- Manual testing with real bot token
- Verify all commands work in the Telegram app

---

## Git Workflow

For each task:
1. Create issue on GitHub
2. Branch: `task-1-scaffold`, `task-2-backend`, etc.
3. Commit incrementally with clear messages
4. PR with "Closes #..." in description
5. Partner review
6. Merge to main

---

## Success Criteria

- **Task 1**: `uv run bot.py --test "/start"` returns welcome message
- **Task 2**: `/health` returns real backend status, `/labs` shows actual labs
- **Task 3**: "what labs are available" triggers the get_labs tool via LLM
- **Task 4**: Bot runs in Docker, responds in Telegram
