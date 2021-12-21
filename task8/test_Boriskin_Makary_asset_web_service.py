import pytest

from task_Boriskin_Makary_asset_web_service import (
    app,
    add_asset, cleanup_asset_list, not_found,
    get_cbr_daily, get_cbr_key_indicators
)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_can_cleanup_by_request(client):
    app_response = client.get("/api/asset/cleanup")
    code = app_response.status_code
    assert 200 == code, (
        f"Expected: 200 code. Received: {code}"
    )
    response_text = app_response.data.decode(app_response.charset)
    assert "there are no more assets" == response_text, (
        f"Expected: predefined text. Received: {response_text}"
    )
    assert 'there are no more assets', 200 == cleanup_asset_list()


def test_page_not_found(client):
    app_response = client.get("/api/asset/route/not/exists")
    code = app_response.status_code
    assert 404 == code, (
        f"Expected: 404 code. Received: {code}"
    )
    response_text = app_response.data.decode(app_response.charset)
    assert "This route is not found" == response_text, (
        f"Expected: predefined text. Received: {response_text}"
    )
    assert "This route is not found", 404 == not_found()


def test_add_asset(client):
    asset_name = "sample"
    app_response = client.get(f"/api/asset/add/USD/{asset_name}/5000/0.5")
    code = app_response.status_code
    assert 200 == code, (
        f"Expected: 200 code. Received: {code}"
    )
    response_text = app_response.data.decode(app_response.charset)
    assert f"Asset '{asset_name}' was successfully added" == response_text, (
        f"Expected: Asset '{asset_name}' was successfully added. Received: {response_text}"
    )
    asset_name2 = "sample2"
    assert f"Asset '{asset_name2}' was successfully added", 200 == add_asset(
        char_code="USD",
        name=asset_name2,
        capital=10000,
        interest=0.6
    )

    duplicate_app_response = client.get(f"/api/asset/add/USD/{asset_name}/5000/0.5")
    code = duplicate_app_response.status_code
    assert 403 == code, (
        f"Expected: 403 code. Received: {code}"
    )
    response_text = duplicate_app_response.data.decode(app_response.charset)
    assert f"Asset '{asset_name}' is already exist" == response_text, (
        f"Expected: Asset '{asset_name}' is already exist. Received: {response_text}"
    )
    assert f"Asset '{asset_name2}' is already exist", 403 == add_asset(
        char_code="USD",
        name=asset_name2,
        capital=10000,
        interest=0.6
    )


def test_can_get_list_and_get_json_output(client):
    app_response = client.get("/api/asset/list")
    assert 200 == app_response.status_code
    assert app_response.is_json
    json_response = app_response.get_json()
    # we have already added 1 'sample' asset previously
    assert 1 == len(json_response)


def test_can_get_by_name(client):
    asset_name = "sample"
    app_response = client.get(f"/api/asset/get?name={asset_name}")
    assert 200 == app_response.status_code
    assert app_response.is_json
    json_response = app_response.get_json()
    assert 1 == len(json_response)
    assert asset_name == json_response[0][1]


def test_can_parse_cbr_daily(client):
    assert all(("EUR" in get_cbr_daily(), "GBP" in get_cbr_daily(), "USD" in get_cbr_daily()))
    app_response = client.get("/cbr/daily")
    assert 200 == app_response.status_code
    assert app_response.is_json


def test_can_parse_cbr_key_indicators(client):
    assert all(
        ("EUR" in get_cbr_key_indicators(), "USD" in get_cbr_key_indicators(),
         "Ag" in get_cbr_key_indicators(), "Au" in get_cbr_key_indicators(),
         "Pt" in get_cbr_key_indicators(), "Pd" in get_cbr_key_indicators())
    )
    app_response = client.get("/cbr/key_indicators")
    assert 200 == app_response.status_code
    assert app_response.is_json


def test_calculate_revenue(client):
    app_response = client.get("/api/asset/calculate_revenue?period=1&period=2")
    assert 200 == app_response.status_code
    assert app_response.is_json
