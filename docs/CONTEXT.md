# Downloader — Project Context

## Overview

**Downloader** is an asynchronous video scraping and downloading service built with **Flask**, **Celery**, and **Selenium**. It accepts a URL via a REST API, scrapes video links from the target website using a headless Chrome browser, and downloads the videos using **yt-dlp**. The service is containerized with Docker and orchestrated via Docker Compose, with Jenkins handling CI/CD.

---

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

---

## Technology Stack

| Component       | Technology              |
|----------------|-------------------------|
| Language        | Python 3.12             |
| Web Framework   | Flask + Flask-CORS      |
| WSGI Server     | Gunicorn (3 workers, 8 threads each) |
| Task Queue      | Celery (Redis broker)   |
| Browser Automation | Selenium WebDriver (Chrome headless) |
| Video Downloader | yt-dlp + ffmpeg         |
| Containerization | Docker + Docker Compose |
| CI/CD           | Jenkins                 |
| Testing         | unittest (pytest available) |

---

## Project Structure

```
Downloader/
├── Dockerfile                    # Multi-stage build: builder + runtime
├── docker-compose.yaml           # Flask app + Celery worker services
├── Jenkinsfile                   # CI/CD pipeline (build & push Docker image)
├── requirements.txt              # Python dependencies
├── env.example                   # Environment variable template
├── README.md                     # Project readme
├── docs/                         # Documentation (this file)
├── src/
│   ├── __init__.py
│   ├── api.py                    # Flask app & /download endpoint
│   ├── configuration/
│   │   ├── __init__.py
│   │   ├── celery_app.py         # Celery app factory
│   │   ├── celery_conf.py        # Celery config (broker, queue, serialization)
│   │   ├── gunicorn.conf.py      # Gunicorn server config
│   │   ├── logger_config.py      # Logging setup (dev/prod JSON configs)
│   │   ├── logging_config_dev.json   # Dev logging (DEBUG level)
│   │   ├── logging_config_prod.json  # Prod logging (INFO level)
│   │   ├── properties.py         # Environment property loader (HITS, FREE, MANY, URLs)
│   │   └── yt_dlp.json           # yt-dlp download options
│   ├── model/
│   │   ├── __init__.py
│   │   ├── chrome_driver.py      # Headless Chrome WebDriver setup
│   │   └── video.py              # Video data model (title, link, path)
│   └── service/
│       ├── __init__.py
│       ├── directory_service.py  # Directory creation & URL parsing
│       ├── downloader_service.py # yt-dlp video download logic
│       ├── monitor_service.py    # Polls external URL processor for task status
│       ├── page_nav_service.py   # Celery task: orchestrates scrape → download
│       ├── route_service.py      # Routes requests to free or hits handlers
│       └── scraper_service.py    # Selenium-based video link scraping
└── test/
    ├── __init__.py
    ├── test_directory_handler.py
    ├── test_page_nav_service.py
    ├── test_route_service.py
    ├── test_scraper_service.py
    └── test_video.py
```

---

## Core Flow

The complete download workflow — from API request through scraping to download — is documented in a dedicated file:

📄 **[docs/download/workflow.md](download/workflow.md)** — Mermaid diagram and step-by-step breakdown of the entire pipeline.

---

## Configuration

### Environment Variables

| Variable              | Description                                  |
|-----------------------|----------------------------------------------|
| `CELERY_BROKER_URL`   | Redis broker URL for Celery                  |
| `CELERY_RESULT_BACKEND` | Redis result backend URL                   |
| `ENVIRONMENT`         | `dev` or `prod` — selects logging config     |
| `HITS`                | Identifier for "hits" website type           |
| `FREE`                | Identifier for "free" website type           |
| `MANY`                | Identifier for "many" website type           |
| `URL_PROCESSOR`       | External URL processor service endpoint      |
| `CHECK_URL`           | External task status check endpoint          |
| `UPLOAD_URL`          | External upload endpoint                     |

### yt-dlp Options (`yt_dlp.json`)

Key settings:
- **Format**: Best 720p+ MP4 with AAC audio, fallback to best available.
- **Retries**: 10 retries, 20 fragment retries, 5 retry streams.
- **Downloader**: ffmpeg for both default and m3u8.
- **Archive**: `/app/log/downloaded_videos.txt` — skips already-downloaded videos.
- **Error handling**: Ignores errors, does not abort on failure.

### Gunicorn (`gunicorn.conf.py`)

- **Bind**: `0.0.0.0:5000`
- **Workers**: 3 threaded workers, 8 threads each.
- **Max requests**: 1000 per worker (with 50 jitter for staggered restarts).

### Celery (`celery_conf.py`)

- **Queue**: `downloader_queue`
- **Serialization**: JSON (tasks, results, accepted content).
- **Worker prefetch**: 1 (processes one task at a time).
- **Late acks**: Enabled (acks after task completion).
- **Broker transport**: Message TTL 60s, max queue length 1000.

---

## Docker Setup

### Dockerfile

Multi-stage build:
1. **Builder stage**: Installs Python dependencies as wheels.
2. **Runtime stage**: Installs Chrome, system libraries, ffmpeg, and Python wheels. Runs as non-root user (`appuser`, UID 1000).

### Docker Compose

Two services:
- **`downloader`** — Flask app served by Gunicorn on port 5000.
- **`downloader-celery-worker`** — Celery worker consuming tasks from `downloader_queue`.

Shared volumes:
- `/home/wilabeast/videos` → `/app/videos` (downloaded videos)
- `/home/wilabeast/logs` → `/app/log/` (logs and download archive)

---

## CI/CD (Jenkins)

Pipeline stages:
1. **Checkout** — pulls source code from SCM.
2. **Build Docker image** — builds image tagged with `BUILD_ID`.
3. **Push to registry** — pushes to `registry.spearmanwm.dev` with both `BUILD_ID` and `prod` tags.

---

## Key Design Decisions

- **Headless Chrome** is used for scraping because target sites likely require JavaScript rendering.
- **Celery** decouples the HTTP request from the long-running scrape/download process, enabling async processing.
- **yt-dlp** is the download engine, configured for robustness (retries, error tolerance, format selection).
- **20-minute minimum** filter ensures only longer-form content is downloaded.
- **Non-root Docker user** for security.
- **Queue-based logging** with rotating file handler for production-safe log management.
- **Download archive** prevents re-downloading the same videos.

---

## Known Quirks & Notes

- `ScraperService` is misspelled as `ScarperService` in the class name (typo in source).
- The `handle_hits` path (external URL processor) exists but is not the default route — `handle_free` is used.
- `MonitorService` polls an external service with a 60-second interval and 20 max retries (up to 20 minutes).
- Directory names are sanitized and uppercased for filesystem safety.
- The "hits" URL pattern extracts directory names from query parameters (`ps` or `spon`).
- Chrome options disable QUIC, HTTP/2, and GPU — likely to work around proxy or headless rendering issues.

---

## Coding Style

### Type Hints

- **All function and method parameters are type-annotated.** Every public and private method signature includes explicit parameter types.
- **Return types are always annotated.** Every function and method specifies its return type, including `-> None` for void functions.
- **Python 3.10+ union syntax** is used with the `|` operator instead of `typing.Union`:
  - `str | None` instead of `Optional[str]`
  - `dict | None` instead of `Optional[dict]`
  - `str|None` (no spaces around `|` in some places)
- **`typing.Any`** is imported and used where a specific type is not applicable (e.g., yt-dlp options dict).
- **No type aliases or `TypeDef` patterns** are used — types are specified inline at each signature.
- **Bare `list`** is used in some return annotations instead of `list[Video]` (e.g., `-> list` in `ScraperService`).

Examples from the codebase:
```python
def route_url(self, url:str, parent_directory:str, number_of_pages:int = 0) -> str:
def create_directory(self, url: str, parent_directory: str | None = None) -> str:
def monitor_task(self) -> dict | None:
def skip_short_videos(self, info_dict, *, incomplete) -> str|None:
def download_video(self, video:Video, opts:Any) -> None:
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `RouteService`, `DirectoryService`, `ChromeDriver`).
- **Functions and methods**: `snake_case` (e.g., `route_url`, `create_directory`, `safe_dir_name`).
- **Private attributes**: prefixed with single underscore `_` (e.g., `self._task_id`, `self._title`).
- **Private methods**: prefixed with single underscore `_` (e.g., `_get_end`, `_is_valid_end`, `_clean_title`).
- **Constants**: `UPPER_SNAKE_CASE` defined inline in methods or as class attributes (e.g., `MAX_RETRIES = 20`, `URL_MOST_POP = "most-popular"`).
- **Module-level variables**: `snake_case` (e.g., `logger`, `api`, `celery_app`).

### Import Organization

- **Standard library** imports first (e.g., `import os`, `import logging`, `import re`).
- **Third-party** imports next (e.g., `import requests`, `from selenium import webdriver`).
- **Local** imports last, using relative imports with dot notation (e.g., `from ..configuration.logger_config import setup_logging`).
- **Blank lines** separate the three groups (standard library, third-party, local).
- Some files have inconsistent import ordering within groups (e.g., `selenium.webdriver.common.by` imported after local imports in `page_nav_service.py`).

### Class Design

- **Properties with getters/setters** are used for encapsulated attributes (e.g., `Video.title`, `RouteService.task_id`, `Properties.url`).
- **`@staticmethod`** decorator is used for methods that don't access instance state (e.g., `ScarperService.scrape_multiple_videos`, `DirectoryService.safe_dir_name`, `RouteService.handle_free`).
- **Class-level constants** are defined directly on the class (e.g., `MonitorService.MAX_RETRIES = 20`).
- **Service classes** follow a single-responsibility pattern — each service handles one domain concern.

### Comments & Documentation

- **Inline comments** explain the purpose of specific lines or arguments (e.g., Chrome options, regex patterns).
- **Docstrings** use the Google style with `Args:` and `Returns:` sections (e.g., `Video.get_videos_title`).
- **Short one-line docstrings** describe method purpose (e.g., `"Extract Video Elements (title + link) from current page."`).
- **No KDoc-style or reStructuredText** docstrings are used.

### Docstring Style (Edited Comments)

Every method and test receives a multi-paragraph docstring that answers three questions: **what it does**, **what goes in**, and **what comes out**.

- **Source code methods**: A one-sentence purpose statement followed by `Args:` and `Returns:` sections listing each parameter's role and the return value's meaning.
- **Test methods**: A three-paragraph structure:
  1. **Purpose** — what the test verifies (e.g., "Test that route_url correctly routes a Hits website URL to handle_hits.").
  2. **Setup/Inputs** — what is mocked or configured and how (e.g., "Mocks Properties to recognize a Hits URL and handle_hits to return a task ID.").
  3. **Assertions** — what is verified (e.g., "Asserts the returned task ID matches and both handle_hits and check_task are called.").
- **Test classes**: A one-line class docstring summarizing the scope (e.g., "Tests for RouteService covering URL routing, task ID management, and external service integration.").
- **`setUp`/`tearDown` methods**: A one-sentence description of what is prepared or cleaned up.
- **Format**: Triple-quoted strings, no blank lines between paragraphs within the same docstring block.

### Logging

- **`setup_logging(__name__)`** is called at module level in every file to create a logger instance.
- **Logger variable** is always named `logger` at module scope.
- **F-strings** are used for log messages with variable interpolation.
- **Log levels**: `info` for normal flow, `warning` for non-critical issues, `error` for failures, `exc_info=True` for exceptions.

### Spacing & Formatting

- **Inconsistent spacing** around type annotation colons — some use `url:str` (no space), others use `url: str` (space after colon).
- **Default parameter spacing** — `number_of_pages:int = 0` (space around `=`).
- **4-space indentation** throughout.

---

## Development Rules

- **All changes must be manually approved** before occurring. No automated or unapproved modifications should be applied to the codebase.
- **Nothing should ever be committed or pushed.** Under no circumstances should code be committed to version control or pushed to any remote repository.
- **Keep solutions and responses simple and concise.** Avoid over-engineering; prefer the simplest approach that satisfies the requirement.
