import pytest

from web_hello import (
    DEFAULT_GREETING_COUNT,
    MAX_GREETING_COUNT,
    REALLY_TOO_MANY_GREETING_COUNT,
    app as hello_app
)


@pytest.fixture
def client():
    with hello_app.test_client() as client:
        yield client


def test_service_reply_to_root_path(client):
    response = client.get("/")
    assert "Hello" in response.data.decode(response.charset)


def test_service_reply_to_username(client):
    response = client.get("/hello/Vasya")
    assert "Vasya" in response.data.decode(response.charset)


def test_service_reply_to_username_with_default_num(client):
    username = "Vasya"
    response = client.get(f"/hello/{username}", follow_redirects=True)
    response_text = response.data.decode(response.charset)
    vasya_count = response_text.count(username)
    assert DEFAULT_GREETING_COUNT == vasya_count


def test_service_reply_to_username_several_times(client):
    username = "Petya"
    expected_greeting_count = 15
    response = client.get(f"/hello/{username}/{expected_greeting_count}")
    response_text = response.data.decode(response.charset)
    petya_count = response_text.count(username)
    assert expected_greeting_count == petya_count


def test_service_reply_to_escaped_username(client):
    non_escaped_tag = "<br>"
    username = "Petya"
    expected_greeting_count = 15
    response = client.get(f"/hello/{non_escaped_tag}{username}/{expected_greeting_count}")
    response_text = response.data.decode(response.charset)
    petya_count = response_text.count(username)
    assert expected_greeting_count == petya_count
    assert 0 == response_text.count(non_escaped_tag)


def test_service_hello_to_username_with_slash(client):
    username = "Vasya"
    response = client.get(f"/hello/{username}/")
    assert 200 == response.status_code


def test_service_reply_to_username_with_too_many_num(client):
    username = "Petya"
    expected_greeting_count = DEFAULT_GREETING_COUNT
    supplied_greeting_count = MAX_GREETING_COUNT + 1
    response = client.get(f"/hello/{username}/{supplied_greeting_count}", follow_redirects=True)
    response_text = response.data.decode(response.charset)
    petya_count = response_text.count(username)
    assert expected_greeting_count == petya_count


def test_service_reply_to_username_with_really_too_many_num(client):
    username = "Petya"
    supplied_greeting_count = REALLY_TOO_MANY_GREETING_COUNT
    response = client.get(f"/hello/{username}/{supplied_greeting_count}", follow_redirects=True)
    assert 404 == response.status_code

    response_text = response.data.decode(response.charset)
    petya_count = response_text.count(username)
    assert 0 == petya_count
