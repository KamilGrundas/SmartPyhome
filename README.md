# SmartPyhome

A home lab management application for managing devices, services, and infrastructure on your local network.

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com) + [SQLModel](https://sqlmodel.tiangolo.com) + [PostgreSQL](https://www.postgresql.org)
- **Frontend**: [React](https://react.dev) + TypeScript + [Vite](https://vitejs.dev) + [Tailwind CSS](https://tailwindcss.com)
- **Auth**: JWT-based authentication with role-based access (admin / user)
- **Serving**: FastAPI serves the built frontend directly via `app.frontend()` — no separate nginx container

## Architecture

```
Browser → FastAPI :8000 → /api/v1/...   (REST API)
                        → /             (React SPA — built Vite dist)
```

The backend Dockerfile is a multi-stage build: Node compiles the frontend in the first stage, Python picks up the `dist/` in the second stage.

## Getting Started

### Requirements

- [Docker](https://www.docker.com) with Docker Compose

### Run on Linux / Raspberry Pi (production)

```bash
docker compose -f compose.yml -f compose.prod.yml up --build -d
```

`compose.prod.yml` switches to `network_mode: host` so Wake-on-LAN magic packets reach the physical LAN.

### Run on Mac / Windows (development)

```bash
docker compose up --build
```

| URL                        | Description        |
|----------------------------|--------------------|
| http://localhost:8000      | App (UI + API)     |
| http://localhost:8000/docs | OpenAPI docs       |
| http://localhost:5432      | PostgreSQL (direct)|

Default credentials: see `.env` (`FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD`).

> Wake-on-LAN won't work from Mac/Windows because Docker Desktop runs inside
> a VM — packets can't reach your physical LAN. Deploy to a Linux machine on
> the same network as the computers you want to wake.

### Configuration

Copy `.env.example` to `.env` and fill in:

```bash
SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(32))">
FIRST_SUPERUSER_PASSWORD=<strong password>
POSTGRES_PASSWORD=<strong password>
RFID_HMAC_SECRET=<random string, min 32 chars — must match ESP32 firmware>
DOCKER_IMAGE_APP=app
```

## Features

### Wake-on-LAN

Manage computers by MAC address and wake them remotely from the Computers tab.

### RFID Access Cards

Manage physical access via RFID cards and an ESP32 reader. Requires [`esp_test`](https://github.com/kamilgrundas/esp_test) firmware.

#### How it works

```
ESP32 reader  →  POST /api/v1/access  (HMAC-SHA256 signed)
                      ↓
              FastAPI verifies signature + checks DB
                      ↓
              200 OK → LED on 3 s (access granted)
              403    → LED blinks 3× (denied)
```

Every request is signed with a shared secret (`HMAC_SECRET` in firmware = `RFID_HMAC_SECRET` in `.env`) and a Unix timestamp to prevent replay attacks (±5 min window; timestamp=0 skips the window check when SNTP is unavailable).

#### Setup

1. **Add a Location** (Access Cards → Locations tab)
   Name must match `GATE_NAME` in the ESP32 firmware exactly (default: `Brama`).

2. **Add a Card** (Access Cards → Cards tab)
   Enter the RFID UID shown in ESP32 logs (`Karta: AA:BB:**.**`). Optionally assign to a user.

3. **Grant access** — two options:
   - **Direct**: in the card's "Manage Access" dialog, tick the location.
   - **Via group**: create a group (Groups tab), assign locations to the group, then add the card to the group.

4. **Match secrets** — set the same value in both:
   - `.env`: `RFID_HMAC_SECRET=<your secret>`
   - `src/bin/rfid.rs`: `const HMAC_SECRET: &str = "<your secret>";`
   Then rebuild and reflash the ESP32.

## Development

### Backend

```bash
cd backend
uv sync
fastapi dev app/main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # Vite dev server on :5173
```

> When developing the frontend outside Docker, point `VITE_API_URL=http://localhost:8000`
> so API calls reach the backend.

### Generate frontend API client

After changing backend routes:

```bash
bash scripts/generate-client.sh
```

## License

MIT
