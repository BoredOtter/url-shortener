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

## Local Kubernetes (Minikube + Tilt)

W repo jest gotowy setup pod `minikube` + `tilt`:

- `charts/url-shortener/` — chart Helm (`api`, `client`, `redis`, `ingress`)
- `Tiltfile` — build obrazów i deploy do klastra przez `helm template`

### 1) Start Minikube i Ingress

```bash
minikube start
minikube addons enable ingress
```

### 2) Dodaj host lokalny

Pobierz IP klastra:

```bash
minikube ip
```

Dodaj wpis do `/etc/hosts`:

```text
<MINIKUBE_IP> url-shortener.local
```

### 3) Uruchom Tilt

```bash
tilt up
```

Lub ręcznie przez Helm:

```bash
helm upgrade --install url-shortener ./charts/url-shortener --namespace url-shortener --create-namespace
```

Adresy:

- App przez Ingress: `http://url-shortener.local`
- API przez Ingress: `http://url-shortener.local/api`
- Dodatkowo (Tilt port-forward):
  - API: `http://localhost:8000`
  - Client: `http://localhost:5173`

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
- `GET /healthz` lub `GET /livez` — liveness (lekki check procesu)
- `GET /readyz` — readiness (sprawdza Redis)
- `GET /startupz` — startup (czy aplikacja zakończyła inicjalizację)

### Kubernetes probes (recommended)

Przykład dla kontenera API na porcie `8000`:

```yaml
startupProbe:
  httpGet:
    path: /startupz
    port: 8000
  failureThreshold: 30
  periodSeconds: 2
  timeoutSeconds: 1

livenessProbe:
  httpGet:
    path: /livez
    port: 8000
  periodSeconds: 10
  timeoutSeconds: 1
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /readyz
    port: 8000
  periodSeconds: 5
  timeoutSeconds: 1
  failureThreshold: 3
  successThreshold: 1
```

Uwagi:

- `liveness` nie sprawdza zależności zewnętrznych (żeby unikać niepotrzebnych restartów).
- `readiness` weryfikuje Redis i odcina ruch do poda, gdy Redis jest niedostępny.
- Redis health check ma krótki timeout przez `REDIS_CONNECT_TIMEOUT` i `REDIS_SOCKET_TIMEOUT` (domyślnie `1s`).

## Local dev behavior

- `api` startuje z `uv sync --frozen --no-dev` i `uvicorn --reload`.
- `client` używa własnego obrazu developerskiego (`client/Dockerfile.dev`) i startuje z `yarn install --immutable` + `yarn dev`.
- Frontend wysyła żądania bezpośrednio do API (`http://localhost:8000/api` domyślnie), bez proxy Vite.
- URL API można zmienić przez `VITE_API_BASE_URL` (np. `http://localhost:8000/api`).
- W buildzie produkcyjnym domyślny URL API to same-origin `/api` (np. `https://domain.com/api`).

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
