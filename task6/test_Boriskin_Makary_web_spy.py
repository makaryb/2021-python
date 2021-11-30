import json
from json import JSONDecodeError
from contextlib import nullcontext as do_not_raise_exception
from getpass import getpass
from unittest.mock import patch, MagicMock

import pytest
import requests
from requests import exceptions

from task_Boriskin_Makary_web_spy import get_free_products, get_enterprise_products, process_gitlab_features

DEFAULT_ENCODING = "utf-8"
DEFAULT_STATUS_CODE = 200
URL_GITHUB_API = "https://api.github.com/"
URL_GITLAB_FEATURES = "https://about.gitlab.com/features/"
URL_AUTH_TEST = "https://jigsaw.w3.org/HTTP/Basic/"
URL_UNKNOWN = "http://it-should-not-exists.com"
GITHUB_API_RESPONSE_FILEPATH = "github_api.txt"
GITLAB_FEATURES_EXPECTED_FILEPATH = "gitlab_features_expected.html"
GITLAB_FEATURES_FILEPATH = "gitlab_features.html"


@pytest.mark.integration_test
@pytest.mark.parametrize(
    "target_url, expected_outcome",
    [
        (URL_GITLAB_FEATURES, True),
        (URL_AUTH_TEST, False)
    ]
)
def test_gitlab_feature_request_is_successful(target_url, expected_outcome):
    response = requests.get(target_url)
    assert expected_outcome == bool(response), (
        f"Expected: {expected_outcome}, but got: {bool(response)}"
    )


@pytest.mark.integration_test
def test_auth_website_requires_correct_credentials():
    response = requests.get(URL_AUTH_TEST, auth=("user", "wrong_password"))
    assert 400 <= response.status_code <= 500, (
        f"Expected: in 400..500, but got: {response.status_code}"
    )


@pytest.mark.integration_test
@patch("test_Boriskin_Makary_web_spy.getpass")
def test_auth_website_accept_correct_credentials(mock_getpass):
    mock_getpass.return_value = "guest"
    response = requests.get(URL_AUTH_TEST, auth=("guest", getpass()))
    assert bool(response)


def build_response_mock_from_content(content, encoding=DEFAULT_ENCODING, status_code=DEFAULT_STATUS_CODE):
    text = content.decode(encoding)
    response = MagicMock(
        content=content,
        encoding=encoding,
        text=text,
        status_code=status_code
    )
    response.json.side_effect = lambda: json.loads(text)
    return response


@pytest.mark.integration_test
@patch("requests.get")
@pytest.mark.parametrize(
    "target_url, expectation",
    [
        (URL_GITHUB_API, do_not_raise_exception()),
        pytest.param(URL_GITLAB_FEATURES, pytest.raises(JSONDecodeError), id="raise-JSONDecodeError"),
        (URL_UNKNOWN, pytest.raises(exceptions.ConnectionError))
    ]
)
def test_we_can_mock_web(mock_requests_get, target_url, expectation):
    mock_requests_get.side_effect = callback_requests_get

    with expectation:
        response = requests.get(target_url)
        assert 200 == response.status_code, (
            f"Expected: {200}, but got: {response.status_code}"
        )
        assert "url" in response.text, (
            f"Expected: 'url' word in response text, but there is not"
        )
        assert isinstance(response.json(), dict), (
            f"Expected: response.json() as dict, but it is not"
        )


def callback_requests_get(url):
    url_mapping = {
        URL_GITHUB_API: GITHUB_API_RESPONSE_FILEPATH,
        URL_GITLAB_FEATURES: GITLAB_FEATURES_EXPECTED_FILEPATH
    }
    if url in url_mapping:
        mock_content_filepath = url_mapping[url]
        with open(mock_content_filepath, "rb") as content_fin:
            content = content_fin.read()
        mock_response = build_response_mock_from_content(content=content)
        return mock_response
    raise exceptions.ConnectionError(f"exceeded max trial connection to {url}")


@pytest.mark.slow
def test_dump_original_gitlab_features(capsys):
    expected_free_stdout = "351"
    expected_enterprise_stdout = "218"
    process_gitlab_features(html_url=URL_GITLAB_FEATURES, html_filepath=GITLAB_FEATURES_FILEPATH)
    captured = capsys.readouterr()
    assert (expected_free_stdout in captured.out) and (expected_enterprise_stdout in captured.out), (
        f"expected: {expected_free_stdout} and {expected_enterprise_stdout}, while you calculated: {captured.out}"
    )


@pytest.mark.integration_test
def test_dump_up_to_date_gitlab_features():
    logging_html = open(GITLAB_FEATURES_EXPECTED_FILEPATH).read()
    expected_free = get_free_products(expected_html=logging_html)
    expected_enterprise = get_enterprise_products(expected_html=logging_html)

    response = requests.get(URL_GITLAB_FEATURES)
    text = response.content.decode(DEFAULT_ENCODING)
    real_free = get_free_products(expected_html=text)
    real_enterprise = get_enterprise_products(expected_html=text)

    assert (expected_free == real_free) and (expected_enterprise == real_enterprise), (
        f'expected free product count is {expected_free}, while you calculated {real_free}; expected enterprise product count is {expected_enterprise}, while you calculated {real_enterprise}'
    )
