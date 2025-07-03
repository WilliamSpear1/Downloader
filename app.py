import threading

from flask import Flask, render_template, request, redirect, url_for

import scarper

from logs.logger_config import setup_logging

app = Flask(__name__)

logger = setup_logging()

@app.route("/")
def index():
    logger.info("Rendering index page.")
    return render_template("index.html")

@app.route("/download", methods=['POST'])
def download():
    url = request.form.get("url")
    thread = threading.Thread(target=scarper.run_browser, args=(url, ))
    logger.info("Starting download thread for URL: %s", url)
    thread.start()
    return redirect(url_for("index"))