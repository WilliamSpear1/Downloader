from flask import Flask, Response, request, jsonify

from .configuration.logger_config import setup_logging
from .service.route_service import RouteService
from flask_cors import CORS

logger = setup_logging(__name__)
api = Flask( __name__)
CORS(api)

@api.route("/download", methods=['POST'])
def download() -> tuple[Response, int]:
    route_service = RouteService()

    # Form Data
    url = request.json.get("url")
    parent_directory = request.json.get("parent_directory")
    number_of_pages = int(request.json.get("number_of_pages") or 1)

    if url is None:
        return jsonify({"error": "url required"}), 400

    task_id = route_service.route_url(url, parent_directory, number_of_pages)
    logger.info(f"Task Id In Flask Route: {task_id}")

    if task_id in None:
        return jsonify({"error": "Could not process url request"}), 500
    else:
        return jsonify({"status": "success"}), 202
