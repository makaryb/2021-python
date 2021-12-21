import logging.config
import yaml

from flask import (
    Flask,
    request, abort, jsonify, make_response
)
from lxml import etree
import requests

logging.config.dictConfig(yaml.safe_load("""
version: 1
formatters:
    simple:
        format: "%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s"
        datefmt: "%Y%m%d_%H%M%S"
handlers:
    stream_handler:
        class: logging.StreamHandler
        stream: ext://sys.stderr
        level: DEBUG
        formatter: simple
loggers:
    wiki_search_app:
        level: DEBUG
        propagate: False
        handlers:
            - stream_handler
    werkzeug:
        level: ERROR
        propagate: False
        handlers:
            - stream_handler
root:
    level: DEBUG
    handlers:
        - stream_handler
"""))

app = Flask(__name__)

WIKI_BASE_URL = "https://en.wikipedia.org"
WIKI_BASE_SEARCH_URL = f"{WIKI_BASE_URL}/w/index.php?search="


@app.route("/api/search", methods=['GET'])
def api_wiki_proxy_search():
    """Поиск статьи по заданной query"""
    try:
        user_query = request.args.get("query", "")
        app.logger.debug("start processing query: %s", user_query[1:-1])
        wiki_response = requests.get(WIKI_BASE_SEARCH_URL + user_query)
        if not wiki_response.ok:
            abort(503)
        article_count = parse_wiki_search_output_for_articles_count(wiki_response.text)
        app.logger.info("found %s articles for query: %s", article_count, user_query[1:-1])
        app.logger.debug("finish processing query: %s", user_query[1:-1])
        return jsonify(
            {
                "version": 1.0,
                "article_count": article_count,
            }
        )
    except requests.exceptions.ConnectionError:
        return 'Wikipedia Search Engine is unavailable', 503


def parse_wiki_search_output_for_articles_count(wiki_search_output):
    root = etree.fromstring(wiki_search_output, etree.HTMLParser())
    results_info = root.xpath("//div[@class='results-info']")
    if results_info is None:
        return 0
    try:
        text_in_tag = results_info[0].itertext()
    except (ValueError, IndexError):
        return 0
    documents_amount = "".join(text_in_tag)
    if documents_amount is None:
        return 0
    return int(documents_amount.split()[-1].replace(",", ""))


@app.errorhandler(404)
def not_found(_ignored):
    """Обращение по несуществующему route"""
    return "This route is not found", 404


@app.errorhandler(500)
def not_exist(_ignored):
    """Недоступность сервиса"""
    return make_response("Wikipedia Search Engine is unavailable", 503)
