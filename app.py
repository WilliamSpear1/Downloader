import threading

from flask import Flask, Response, request, jsonify

from src.configuration.logger_config import setup_logging
from src.service.monitor_service import MonitorService
from properties import Properties
from src.service.route_service import RouteService
from flask_cors import CORS

logger = setup_logging(__name__)
app = Flask( __name__)
CORS(app)

@app.route("/download", methods=['POST'])
def download() -> tuple[Response, int]:
    route_handler = RouteService(Properties())

    # Form Data
    url = request.json.get("url")
    parent_directory = request.json.get("parent_directory")
    number_of_pages = int(request.json.get("number_of_pages") or 1)

    if url is None:
        return jsonify({"error": "url required"}), 400

    task_id = route_handler.route_url(url, parent_directory, number_of_pages)
    logger.info(f"Task Id In Flask Route: {task_id}")

    if 'hits' in url:
        logger.debug("URL contains 'hits', skipping task monitoring.")
        check_task(task_id, url)

    return jsonify({"status": "success"}), 202

def check_task(task_id:str,url:str="") -> None:
    properties = Properties()

    check_url = properties.get_check_url()
    monitor = MonitorService(task_id, check_url)
    thread = threading.Thread(target=monitor.probe, args=(url,), daemon=True)
    thread.start()