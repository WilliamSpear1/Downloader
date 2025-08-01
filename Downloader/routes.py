import threading

from flask import Blueprint, render_template, request, url_for, redirect, Response

from Downloader.scarper import Scarper
from Downloader.logs.logger_config import setup_logging

logger = setup_logging(__name__)
bp = Blueprint('main', __name__)

@bp.route("/")
def index() -> str:
    logger.info("Rendering index page.")
    return render_template("index.html")

@bp.route("/download", methods=['POST'])
def download() -> Response:
    #TODO: Update method to determine url matches
    # if match is made to specific url then add request to external app.
    # Then poll for result.
    # Will most likely need to add video_dto.py
    # And additional method here in method to poll in javascript.
    url = request.form.get("url")
    parent_directory = request.form.get("parent_directory")
    number_of_pages = int(request.form.get("number_of_pages"))

    logger.info(f"URL: {parent_directory}")
    logger.info(f"Parent Directory: {parent_directory}")
    logger.info(f"Number of Pages: {number_of_pages}")

    scarper = Scarper(url, number_of_pages, parent_directory)
    logger.info("Starting download thread for URL: %s", url)
    thread = threading.Thread(target=scarper.run_browser)
    thread.start()
    return redirect(url_for("main.index"))
