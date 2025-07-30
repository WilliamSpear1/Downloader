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
    url = request.form.get("url")
    scarper = Scarper(url)
    logger.info("Starting download thread for URL: %s", url)
    thread = threading.Thread(target=scarper.run_browser)
    thread.start()
    return redirect(url_for("main.index"))
