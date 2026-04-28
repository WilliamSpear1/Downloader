# Downloader
A robust **asynchronous video downloader** service built with Flask, Celery, and Selenium.
It supports scraping and downloading multiple video requests through the use of yt-dlp downloader.

## Prerequisites
- **Python 3.12**
- **Docker & Docker Compose**
- **Redis**
- **Google Chrome** (Included in Docker Image)

## Installation
1. Create a virtual environment
  - python3.12 -m venv .venv
  - source .vevn/bin/activate # On Windows
2. Install dependencies
  - pip install -r requirements.txt
3. cp env.exmaple .env
4. docker run -d -p 6379:6379 redis:latest
5.
    - python -m flask --app src.api run --host 0.0.0.0 --port 5000
    - celery -A src.configuration.celery_app worker -Q downloader_queue -l info

## Docker Deployment
1. docker network create app-net
2. cp env.example .env
3. docker-compose build
4. docker-compose up -d
5. docker-compose logs -f downloader
6. docker-compose logs -f downloader-celery-worker
