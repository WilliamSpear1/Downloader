import os
import threading
from subprocess import check_call

from flask import Blueprint, render_template, request, url_for, redirect, Response, Flask

from monitor import Monitor
from properties import Properties
from route_handler import RouteHandler
from logs.logger_config import setup_logging

logger = setup_logging(__name__)
app = Flask( __name__)

@app.route("/")
def index() -> str:
    logger.info("Rendering index page.")
    return render_template("index.html")

@app.route("/download", methods=['POST'])
def download() -> Response:
    route_handler = RouteHandler(Properties())

    # Form Data
    url = request.form.get("url")
    parent_directory = request.form.get("parent_directory")
    number_of_pages = int(request.form.get("number_of_pages") or 0)

    logger.info(f"URL: {url}")
    logger.info(f"Parent Directory: {parent_directory}")
    logger.info(f"Number of Pages: {number_of_pages}")

    task_id = route_handler.route_url(url, parent_directory, number_of_pages)
    logger.info(f"Task Id In Flask Route: {task_id}")

    if 'hits' in url:
        #check_url = os.environ.get('URL_CHECK')
        check_url = "http://url_processor:5001/task-status"
        logger.info(f"Check URL: {check_url}")
        monitor = Monitor(task_id, check_url)
        thread = threading.Thread(target=monitor.probe, args=(parent_directory,), daemon=True)
        thread.start()

    return redirect(url_for("index"))