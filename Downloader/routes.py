import threading
from string import Template

from flask import Blueprint, render_template, request, url_for, redirect, Response

from Downloader import scarper
from logs.logger_config import setup_logging

logger = setup_logging(__name__)
bp = Blueprint('main', __name__)

@bp.route("/")
def index() -> str:
    logger.info("Rendering index page.")
    return render_template("index.html")

@bp.route("/download", methods=['POST'])
def download() -> Response:
    url = request.form.get("url")
    thread = threading.Thread(target=scarper.run_browser, args=(url,))
    logger.info("Starting download thread for URL: %s", url)
    thread.start()
    return redirect(url_for("index"))
