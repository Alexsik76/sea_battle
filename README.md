# Sea Battle

A modern, responsive, and real-time multiplayer implementation of the classic Sea Battle game. Built with a focus on fluid UX, proportional scaling, and a premium "command center" aesthetic.

## 🚀 Features

- **Real-time Multiplayer**: Powered by WebSockets for instantaneous turn updates and lobby management.
- **Dynamic Proportional Scaling**: The game board uses CSS `min()` functions to ensure it always fits perfectly on any screen size (mobile to ultra-wide) while maintaining a square aspect ratio.
- **Stable 3-Zone Layout**: A specialized 30/50/20 vh layout ensures the UI remains static and "jump-free" during turn transitions.
- **Modern Tech Stack**: 
  - **Frontend**: Vue 3 + Vite + UnoCSS.
  - **Backend**: Python (FastAPI/Uvicorn).
  - **Infrastructure**: Docker Compose + Caddy for secure, performant local development.
- **Premium Visuals**: Custom grid-gap rendering for perfect 1px lines, neon-glow ship indicators, and glassmorphism effects.

## 🛠️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Execution

Simply run the following command in the root directory:

```bash
docker compose up --build
```

The application will be available at `http://localhost` (or the port defined in your `docker-compose.yml`).

## 📁 Project Structure

- `frontend/`: Vue 3 application with UnoCSS for styling and Pinia for state management.
- `backend/`: FastAPI server handling game logic, room management, and WebSocket connections.
- `Caddyfile`: Reverse proxy configuration for local development.

## 🎮 How to Play

1. **Profile Setup**: Enter your Admiral name in the lobby.
2. **Lobby**: Create a new room or join an existing one.
3. **Fleet Setup**: Manually place your ships or click **Randomize Fleet** for quick deployment.
4. **Battle**: Click on the "Target Grid" to fire at your opponent's fleet. First one to sink all ships wins!

## 📜 License

This project is open-source and available under the MIT License.
