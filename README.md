# Downloader

An asynchronous video scraping and downloading service built with **Flask**, **Celery**, and **Selenium**. It accepts a video page URL via a REST API, scrapes video links using a headless Chrome browser, and downloads the videos using **yt-dlp**. Videos shorter than 20 minutes are automatically skipped.

## Architecture

```
Client (POST /download)
        │
        ▼
  ┌──────────┐
  │  Flask    │  ← HTTP API (port 5000), served by Gunicorn
  │  (api.py) │
  └────┬─────┘
       │  dispatches Celery task
       ▼
  ┌──────────────┐
  │   Celery      │  ← Async task queue (Redis broker + backend)
  │   Worker      │     Queue: downloader_queue
  └────┬─────────┘
       │
       ▼
  ┌──────────────────┐
  │  Selenium +       │  ← Headless Chrome browser
  │  ScraperService   │     Scrapes video titles and links
  └────┬─────────────┘
       │
       ▼
  ┌──────────────────┐
  │  Downloader       │  ← yt-dlp downloads each video
  │  Service          │     Filters out videos < 20 min
  └──────────────────┘
```

## Technology Stack

| Component          | Technology                          |
|--------------------|-------------------------------------|
| Language           | Python 3.12                         |
| Web Framework      | Flask + Flask-CORS                  |
| WSGI Server        | Gunicorn (3 workers, 8 threads)     |
| Task Queue         | Celery (Redis broker)               |
| Browser Automation | Selenium WebDriver (Chrome headless) |
| Video Downloader   | yt-dlp + ffmpeg                     |
| Containerization   | Docker + Docker Compose             |
| CI/CD              | Jenkins                             |
| Testing            | unittest (pytest)                   |

## API Usage

Send a `POST` request to `/download` with a JSON body:

```json
{
  "url": "https://example.com/videos",
  "parent_directory": "MyDownloads",
  "number_of_pages": 3
}
```

| Field              | Type   | Required | Default | Description                              |
|--------------------|--------|----------|---------|------------------------------------------|
| `url`              | string | Yes      | —       | The video page URL to scrape and download |
| `parent_directory` | string | No       | `""`    | Parent folder for downloaded videos      |
| `number_of_pages`  | int    | No       | `1`     | Number of pages to scrape (pagination)   |

**Response:**

- `202 Accepted` — Task queued successfully: `{"status": "success"}`
- `400 Bad Request` — Missing `url` field: `{"error": "url required"}`
- `500 Internal Server Error` — Routing failed: `{"error": "Could not process url request"}`

Example request:

```bash
curl -X POST http://localhost:5000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/videos", "number_of_pages": 2}'
```

## Environment Variables

Copy `env.example` to `.env` and configure the following variables:

| Variable              | Description                                  | Example                              |
|-----------------------|----------------------------------------------|--------------------------------------|
| `CELERY_BROKER_URL`   | Redis/RabbitMQ broker connection URL         | `redis://localhost:6379/0`           |
| `CELERY_RESULT_BACKEND` | Celery result backend URL                  | `redis://localhost:6379/0`           |
| `CHECK_URL`           | External URL processor task status endpoint  | `http://url_processor:5001/task-status` |
| `UPLOAD_URL`          | External URL processor upload endpoint       | `http://url_processor:501/upload`    |
| `URL_PROCESSOR`       | External URL processor fetch endpoint        | `http://url_processor:5001/fetch-urls` |
| `HITS`                | Comma-separated list of "hits" site domains  | `hits`                               |
| `FREE`                | Comma-separated list of "free" site domains  | `free`                               |
| `MANY`                | Comma-separated list of "many" site domains  | `many`                               |
| `ENVIRONMENT`         | Environment name (`dev` or `prod`)           | `dev`                                |

The site domain lists (`HITS`, `FREE`, `MANY`) determine how incoming URLs are routed:
- **Hits** sites are sent to an external URL processor for status polling.
- **Free** sites are processed directly by the Celery worker.
- **Many** sites are handled by both handlers.

## Installation

### Prerequisites

- **Python 3.12**
- **Redis** (task broker)
- **Google Chrome** (included in Docker image)

### Local Development

1. Create a virtual environment:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp env.example .env
   # Edit .env with your broker URLs and site configurations
   ```

4. Start Redis:
   ```bash
   docker run -d -p 6379:6379 redis:latest
   ```

5. Start the Flask API:
   ```bash
   python -m flask --app src.api run --host 0.0.0.0 --port 5000
   ```

6. In a separate terminal, start the Celery worker:
   ```bash
   celery -A src.configuration.celery_app worker -Q downloader_queue -l info
   ```

## Docker Deployment

1. Create the Docker network:
   ```bash
   docker network create app-net
   ```

2. Configure environment:
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

3. Build and start services:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. View logs:
   ```bash
   docker-compose logs -f downloader
   docker-compose logs -f downloader-celery-worker
   ```

Two containers are started:
- **`downloader`** — Flask API server on port 5000
- **`downloader-celery-worker`** — Celery background worker processing download tasks

Volumes are mounted for downloaded videos (`/home/wilabeast/videos`) and logs (`/home/wilabeast/logs`).

## Project Structure

```
Downloader/
├── Dockerfile                    # Multi-stage build: builder + runtime
├── docker-compose.yaml           # Flask app + Celery worker services
├── Jenkinsfile                   # CI/CD pipeline (build & push Docker image)
├── requirements.txt              # Python dependencies
├── env.example                   # Environment variable template
├── README.md                     # This file
├── docs/                         # Documentation
│   ├── CONTEXT.md                # Project context and coding conventions
│   └── download/
│       └── workflow.md           # Download pipeline workflow diagram
├── src/
│   ├── api.py                    # Flask app & /download endpoint
│   ├── configuration/
│   │   ├── celery_app.py         # Celery app factory
│   │   ├── celery_conf.py        # Celery config (broker, queue, serialization)
│   │   ├── gunicorn.conf.py      # Gunicorn server config
│   │   ├── logger_config.py      # Logging setup (dev/prod JSON configs)
│   │   ├── properties.py         # Environment property loader
│   │   └── yt_dlp.json           # yt-dlp download options
│   ├── model/
│   │   ├── chrome_driver.py      # Headless Chrome WebDriver setup
│   │   └── video.py              # Video data model (title, link, path)
│   └── service/
│       ├── directory_service.py  # Directory creation & URL parsing
│       ├── downloader_service.py # yt-dlp video download logic
│       ├── monitor_service.py    # Polls external URL processor for task status
│       ├── page_nav_service.py   # Celery task: orchestrates scrape → download
│       ├── route_service.py      # Routes requests to free or hits handlers
│       └── scraper_service.py    # Selenium-based video link scraping
└── test/                         # Unit tests
    ├── test_directory_handler.py
    ├── test_page_nav_service.py
    ├── test_route_service.py
    ├── test_scraper_service.py
    └── test_video.py
```

## Testing

Run the test suite with pytest:

```bash
pytest test/ -v
```

## Documentation

- **[docs/CONTEXT.md](docs/CONTEXT.md)** — Full project context, architecture, coding style, and development rules.
- **[docs/download/workflow.md](docs/download/workflow.md)** — Detailed download pipeline workflow diagram and step-by-step breakdown.
