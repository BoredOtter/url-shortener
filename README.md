# URL Shortener (FastAPI API + Vite Client + Redis)

Prosty skracacz linków podzielony na backend API i frontend SPA.

## Struktura

- `api/` — backend FastAPI (uv, Redis, redirect)
- `client/` — frontend Vite + React + prawdziwy `shadcn/ui` (Radix)
- `docker-compose.yml` — lokalny stack `api + client + redis`

## Uruchomienie lokalne

Pierwszy start:

```bash
docker compose up --build
```

Kolejne starty:

```bash
docker compose up
```

Adresy:

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`

Frontend używa Yarn Berry (`packageManager: yarn@4.x`).

## Produkcyjny frontend (baked static app)

Frontend ma osobny obraz produkcyjny w `client/Dockerfile`:

- etap build: `yarn install --immutable` + `yarn build` (Vite)
- etap runtime: `nginx` serwujący pliki z `dist/`

Build obrazu:

```bash
docker build -f client/Dockerfile -t url-shortener-client:prod ./client
```

Uruchomienie:

```bash
docker run --rm -p 8080:80 url-shortener-client:prod
```

Przez Compose (profil `prod`):

```bash
docker compose --profile prod up --build client-prod
```

## API

- `POST /api/shorten`
  - body JSON: `{"url":"https://example.com"}`
  - response JSON: `{"short_url":"...","long_url":"..."}`
- `GET /{short_id}` — redirect do oryginalnego URL

## Local dev behavior

- `api` startuje z `uv sync --frozen --no-dev` i `uvicorn --reload`.
- `client` używa własnego obrazu developerskiego (`client/Dockerfile.dev`) i startuje z `yarn install --immutable` + `yarn dev`.
- Frontend używa `VITE_API_BASE_URL=http://localhost:8000` (ustawione w Compose).

## shadcn/ui

Frontend został zainicjalizowany oficjalnym CLI `shadcn` dla Vite i komponenty zostały dodane komendą `yarn dlx shadcn@latest add ...`.

## Produkcyjny obraz API

Build:

```bash
docker build -f api/Dockerfile -t url-shortener-api:prod ./api
```

## Zmienne środowiskowe backendu

- `REDIS_HOST` (domyślnie: `localhost`)
- `REDIS_PORT` (domyślnie: `6379`)
- `REDIS_PASSWORD` (opcjonalnie)
- `CORS_ALLOW_ORIGINS` (CSV; local dev domyślnie port 5173)
