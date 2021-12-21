import pytest
import requests

from task_Boriskin_Makary_web_service_log import (
    app as wiki_app,
    parse_wiki_search_output_for_articles_count,
    not_found,
    WIKI_BASE_SEARCH_URL
)


@pytest.fixture
def client():
    with wiki_app.test_client() as client:
        yield client


def test_page_not_found(client):
    app_response = client.get("/api/route/not/exists")
    code = app_response.status_code
    assert 404 == code, (
        f"Expected: 404 code. Received: {code}"
    )
    response_text = app_response.data.decode(app_response.charset)
    assert "This route is not found" == response_text, (
        f"Expected: predefined text. Received: {response_text}"
    )
    assert "This route is not found", 404 == not_found()


def test_can_proxy_request_to_wiki_and_get_json_output(client):
    app_response = client.get("/api/search?query=python+network")
    assert 200 == app_response.status_code
    assert app_response.is_json


def test_can_parse_wiki_search_output():
    wiki_response = requests.get(WIKI_BASE_SEARCH_URL + "<football>")
    assert 200 == wiki_response.status_code
    result = parse_wiki_search_output_for_articles_count(wiki_response.text)
    assert result > 500000
