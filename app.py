import threading

from flask import Flask, render_template, request, redirect, url_for

import scarper

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=['POST'])
def download():
    url = request.form.get("url")
    thread = threading.Thread(target=scarper.run_browser, args=(url, ))
    thread.start()
    return redirect(url_for("index"))