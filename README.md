# SmartPyhome

A home lab management application for managing devices, services, and infrastructure on your local network.

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com) + [SQLModel](https://sqlmodel.tiangolo.com) + [PostgreSQL](https://www.postgresql.org)
- **Frontend**: [React](https://react.dev) + TypeScript + [Vite](https://vitejs.dev) + [Tailwind CSS](https://tailwindcss.com)
- **Auth**: JWT-based authentication with role-based access (admin / user)
- **Database admin**: Adminer at `http://localhost:8080`

## Getting Started

### Requirements

- [Docker](https://www.docker.com) with Docker Compose

### Run on Linux / Raspberry Pi (production)

```bash
docker compose -f compose.yml -f compose.prod.yml up --build -d
```

`compose.prod.yml` switches the backend to `network_mode: host` so Wake-on-LAN magic packets reach the physical LAN.

### Run on Mac / Windows (development)

```bash
docker compose up --build
```

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:5173      |
| Backend  | http://localhost:8000      |
| API docs | http://localhost:8000/docs |
| Adminer  | http://localhost:8080      |

Default credentials: see `.env` (`FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD`).

> Wake-on-LAN won't work from Mac/Windows because Docker Desktop runs inside
> a VM — packets can't reach your physical LAN. Deploy to a Linux machine on
> the same network as the computers you want to wake.

### Configuration

Copy `.env.example` to `.env` and adjust. Change at minimum before deploying:

```bash
SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(32))">
FIRST_SUPERUSER_PASSWORD=<strong password>
POSTGRES_PASSWORD=<strong password>
```

## Development

### Backend

See [backend/README.md](./backend/README.md).

### Frontend

See [frontend/README.md](./frontend/README.md).

### Generate frontend API client

After changing backend routes:

```bash
bash scripts/generate-client.sh
```

## License

MIT
