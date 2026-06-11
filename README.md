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

### Run

```bash
docker compose up --build
```

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:5173      |
| Backend  | http://localhost:8000      |
| API docs | http://localhost:8000/docs |
| Adminer  | http://localhost:8080      |

Default credentials are set in `.env` (`FIRST_SUPERUSER` / `FIRST_SUPERUSER_PASSWORD`).

### Configuration

Adjust values in `.env` as needed. For any non-local deployment, change at minimum:

```bash
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
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
