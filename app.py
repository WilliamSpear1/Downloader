import os
import threading
from subprocess import check_call

from flask import Blueprint, render_template, request, url_for, redirect, Response, Flask, jsonify

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
        check_task(task_id, parent_directory, url)

    return redirect(url_for("index"))

@app.route("/upload", methods=['POST'])
def upload() -> tuple[Response, int]:
    route_handler = RouteHandler(Properties())

    uploaded_file = request.files["file"]
    parent_directory = request.form.get("parent_directory")

    if not uploaded_file:
        return jsonify({"error": "file_path required"}), 400
    if not parent_directory:
        return jsonify({"error": "parent_directory required"}), 400

    task_id = route_handler.handle_upload(uploaded_file)
    logger.info(f"Task Id In Flask Route: {task_id}")

    check_task(task_id,parent_directory)

    return jsonify({"task_id": task_id, "status": "processing"}), 202

def check_task(task_id:str,parent_directory,url:str="",) -> None:
    properties = Properties()

    check_url = properties.get_check_url()
    logger.info(f"Check URL: {check_url}")
    monitor = Monitor(task_id, check_url)
    thread = threading.Thread(target=monitor.probe, args=(url, parent_directory,), daemon=True)
    thread.start()

def process_urls(file_path: str) -> list:
    urls = []
    with open(file_path, "r") as file:
        for line in file:
            urls.append(line)
    return urls