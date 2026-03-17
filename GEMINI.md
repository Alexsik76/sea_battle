# Sea Battle - Project Context

## Project Overview
Sea Battle is a full-stack, real-time multiplayer implementation of the classic board game. It is designed with a responsive UI and uses WebSockets for instantaneous turn updates and lobby management.

The architecture is split into two main components:
- **Frontend**: A Vue 3 application built with Vite. It utilizes Pinia for state management and UnoCSS for fast, utility-first styling.
- **Backend**: A Python server built with FastAPI. It handles core game logic, player sessions, room management, and WebSocket connections.
- **Infrastructure**: The application is fully containerized using Docker and Docker Compose. Caddy acts as a reverse proxy, seamlessly routing `/api*` and `/ws*` requests to the backend while serving the frontend on the root path.

## Building and Running

### Using Docker (Production & Full-stack testing)
To build and run the complete application environment, run the following from the root directory:
```bash
docker compose up --build
```
The application will be accessible at `http://localhost` (or `https://localhost` depending on Caddy's auto-HTTPS).

### Local Frontend Development
To develop the frontend independently with hot-module replacement (HMR):
```bash
cd frontend
npm install
npm run dev
```
*(Note: You will also need to run the backend separately for full functionality, or point your API requests to the Dockerized backend).*

### Local Backend Development
To develop the backend independently:
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
# On Linux use: ./venv/bin/activate
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Development Conventions

- **Frontend**:
  - Uses **Vue 3** with the **Composition API** and `<script setup>` syntax.
  - State management is handled centrally via **Pinia** (e.g., `stores/gameStore.js`).
  - **UnoCSS** is configured for utility classes, maintaining an aesthetic "command center" visual style and responsive grid-based layouts.
- **Backend**:
  - **FastAPI** drives the API and WebSocket handlers.
  - Core game state and connections are abstracted (e.g., `connection_manager.py` for WebSockets, `models.py` for game entities).
  - Validation and data structuring are handled by **Pydantic** models (found in the `dto/` package).
  - Never install Python packages globally. Always create and activate a virtual environment (`python -m venv venv`) before using `pip`.
- **Networking**:
  - The `Caddyfile` handles local reverse proxy rules: `/api*` and `/ws*` map to the FastAPI backend at port 8000. All other routes try to match frontend files or fallback to `/index.html`.
