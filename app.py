import threading

from flask import Flask, render_template, request, redirect, url_for

import scarper
import logging

app = Flask(__name__)

@app.route("/")
def index():
    logging.info("Rendering index page.")
    return render_template("index.html")

@app.route("/download", methods=['POST'])
def download():
    url = request.form.get("url")
    thread = threading.Thread(target=scarper.run_browser, args=(url, ))
    logging.info("Starting download thread for URL: %s", url)
    thread.start()
    return redirect(url_for("index"))