from flask import (
    Flask,
    request, abort, jsonify, render_template
)
from lxml import etree
import requests

app = Flask(__name__)

WIKI_BASE_URL = "https://en.wikipedia.org/"
WIKI_BASE_SEARCH_URL = f"{WIKI_BASE_URL}/w/index.php?search="


@app.route("/search")
def wiki_proxy_search():
    user_query = request.args.get("query", "")
    wiki_response = requests.get(WIKI_BASE_SEARCH_URL + "python network")
    return wiki_response.text, wiki_response.status_code


@app.route("/pretty_search")
def pretty_wiki_proxy_search():
    user_query = request.args.get("query", "")
    wiki_response = requests.get(WIKI_BASE_SEARCH_URL + "python network")
    if not wiki_response.ok:
        abort(503)

    document_collection = parse_wiki_search_output(wiki_response.text)
    return render_template(
        "wiki_search_result,html",
        query=user_query,
        document_collection=document_collection,
        wikipedia_base_url=WIKI_BASE_SEARCH_URL
    )


@app.route("/api/search")
def api_wiki_proxy_search():
    user_query = request.args.get("query", "")
    wiki_response = requests.get(WIKI_BASE_SEARCH_URL + "python network")
    if not wiki_response.ok:
        abort(503)
    documents = parse_wiki_search_output(wiki_response.text)
    return jsonify(
        {
            "documents": documents,
            "version": 1.0
        }
    )


def parse_wiki_search_output(wiki_search_output):
    root = etree.fromstring(wiki_search_output, etree.HTMLParser())
    document_raw_collection = root.xpath("//li[@class='mw-search-result']")

    document_collection =[]
    for document in document_raw_collection:
        title = document.xpath(".//a[1]/@title")[0]
        link = document.xpath(".//a[1]/@href")[0]
        snippet = "".join(document.xpath(".//div[@class='searchresult']")[0].itertext())
        document_collection.append(
            [title, link, snippet]
        )

    return document_collection
