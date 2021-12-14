#!/usr/bin/env python3
from typing import Dict

import requests

from flask import (
    Flask,
    request, abort, jsonify
)
from bs4 import BeautifulSoup as bs

CBR_BASE_URL = "https://www.cbr.ru/eng"
CBR_DAILY_URL = f"{CBR_BASE_URL}/currency_base/daily/"
CBR_KEY_INDICATORS_URL = f"{CBR_BASE_URL}/key-indicators/"

app = Flask(__name__)


class Asset:
    def __init__(self, name: str, capital: float, interest: float, char_code: str):
        self.name = name
        self.capital = capital
        self.interest = interest
        self.char_code = char_code

    def calculate_revenue(self, years: int, rate: float) -> float:
        """Сам расчёт"""
        revenue = rate * self.capital * ((1.0 + self.interest) ** years - 1.0)
        return revenue


def parse_cbr_currency_base_daily(html_data: str) -> Dict[str, float]:
    """Парсим html-ку с ежедневными значениями"""
    curr_rate = {}
    beautiful_soup = bs(html_data, 'html.parser')
    html = beautiful_soup.find('html')
    body = html.find('body')
    main = body.find('main', id='content')

    div_1 = main.find('div', class_='offsetMenu')
    div_2 = div_1.find('div', class_='container-fluid')
    div_3 = div_2.find('div', class_='col-md-23 offset-md-1')
    div_4 = div_3.find('div', class_='table-wrapper')
    div_5 = div_4.find('div', class_='table')
    table = div_5.find('table', class_='data')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for i in range(1, len(rows)):
        row = rows[i]
        tds = row.find_all('td')
        char_code = tds[1].string
        unit = float(tds[2].string.replace(",", ""))
        rate = float(tds[4].string.replace(",", ""))
        curr_rate[char_code] = rate / unit
    return curr_rate


def parse_cbr_key_indicators(html_data: str) -> Dict[str, float]:
    """Парсим html-ку с ключевыми индикаторами"""
    curr_rate = {}
    beautiful_soup = bs(html_data, 'html.parser')
    html = beautiful_soup.find('html')
    body = html.find('body')
    main = body.find('main', id='content')

    div_1 = main.find('div', class_='offsetMenu')
    div_2 = div_1.find('div', class_='container-fluid')
    div_3 = div_2.find('div', class_='col-md-23 offset-md-1')
    div_4 = div_3.find('div', class_='dropdown')
    div_5 = div_4.find('div', class_='dropdown_content')
    div_6 = div_5.find_all('div', class_='key-indicator_content offset-md-2')
    for k in range(3):
        div_7 = div_6[k].find('div', class_='key-indicator_table_wrapper')
        div_8 = div_7.find('div', class_='table key-indicator_table')
        table = div_8.find('table')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for i in range(1, len(rows)):
            row = rows[i]
            tds = row.find_all('td')
            div_1 = tds[0].find('div')
            if div_1:
                div_2 = div_1.find_all('div')
                char_code = div_2[1].string
                if tds[-1].string:
                    try:
                        value_2 = float(tds[-1].string.replace(",", ""))
                        curr_rate[char_code] = value_2
                    except ValueError:
                        pass
    return curr_rate


class AssetList:
    def __init__(self, name):
        self.name = name
        self.asset_dict = {}

    def cleanup(self):
        """cleanup"""
        self.asset_dict = {}

    def calculate_all_revenue(self, period: int) -> float:
        """calculate_revenue"""
        cbr_daily_response = requests.get(CBR_DAILY_URL)
        cbr_key_indicators_response = requests.get(CBR_KEY_INDICATORS_URL)
        if not (cbr_daily_response.ok or cbr_key_indicators_response.ok):
            raise ValueError()
        currency_dict = parse_cbr_currency_base_daily(cbr_daily_response.text)
        metal_dict = parse_cbr_key_indicators(cbr_key_indicators_response.text)

        total_revenue = 0
        for asset in self.asset_dict.values():
            if asset.char_code in metal_dict:
                rate = metal_dict[asset.char_code]
            else:
                rate = currency_dict.get(asset.char_code, 0)
            revenue = asset.calculate_revenue(period, rate)
            total_revenue += revenue

        return total_revenue

    def get_asset_list(self, name_list=None):
        m_asset_list = []
        for asset in self.asset_dict.values():
            if name_list is None or asset.name in name_list:
                asset_repr = [asset.char_code, asset.name, asset.capital, asset.interest]
                m_asset_list.append(asset_repr)
        m_asset_list = sorted(m_asset_list, key=lambda x: x[1])
        m_asset_list = sorted(m_asset_list, key=lambda x: x[0])
        return m_asset_list


@app.errorhandler(404)
def page_not_found(_ignored):
    """Обращение по несуществующему route"""
    return "This route is not found", 404


@app.errorhandler(503)
def page_do_not_exist(_ignored):
    """Недоступность cbr.ru"""
    return 'CBR service is unavailable', 503


@app.route("/api/asset/cleanup")
def cleanup_asset_list():
    """Очистить список активов."""
    asset_list.cleanup()
    return 'there are no more assets', 200


@app.route("/api/asset/calculate_revenue")
def calculate_revenue():
    """Оценочная инвестиционная доходность"""
    try:
        user_period = request.args.getlist("period")
        revenues = {}
        for period in user_period:
            revenue = asset_list.calculate_all_revenue(int(period))
            revenues[str(int(period))] = revenue
        return jsonify(revenues)
    except:
        abort(503)


@app.route("/api/asset/get")
def get_asset_list_by_name():
    """Список всех перечисленных активов"""
    user_name_list = request.args.getlist("name")
    m_asset_list = asset_list.get_asset_list(user_name_list)
    return jsonify(m_asset_list)


@app.route("/api/asset/list")
def get_asset_list():
    """Список всех доступных активов"""
    m_asset_list = asset_list.get_asset_list()
    return jsonify(m_asset_list)


@app.route("/api/asset/add/<char_code>/<name>/<float:capital>/<float:interest>")
@app.route("/api/asset/add/<char_code>/<name>/<float:capital>/<int:interest>")
@app.route("/api/asset/add/<char_code>/<name>/<int:capital>/<float:interest>")
@app.route("/api/asset/add/<char_code>/<name>/<int:capital>/<int:interest>")
def add_asset(char_code, name, capital, interest):
    """Возможность работать с портфелем активов в формате Web-сервиса"""
    if name not in asset_list.asset_dict:
        new_asset = Asset(name, float(capital), float(interest), char_code)
        asset_list.asset_dict[name] = new_asset
        return f"Asset '{name}' was successfully added", 200
    return f"Asset '{name}' is already exist", 403


@app.route("/cbr/daily")
def cbr_daily():
    """Запрос на страницу “daily” (взять курсы валют), ответ: {“char_code”: rate}"""
    try:
        cbr_daily_response = requests.get(CBR_DAILY_URL)
        if not cbr_daily_response.ok:
            abort(503)
        currency_dict = parse_cbr_currency_base_daily(cbr_daily_response.text)
        return currency_dict
    except:
        abort(503)


@app.route("/cbr/key_indicators")
def cbr_key_indicators():
    """Запрос на страницу “key-indicators” (взять USD, EUR и драг металлы), ответ {“char_code”: rate}"""
    try:
        cbr_key_indicators_response = requests.get(CBR_KEY_INDICATORS_URL)
        if not cbr_key_indicators_response.ok:
            abort(503)
        metal_dict = parse_cbr_key_indicators(cbr_key_indicators_response.text)
        return metal_dict
    except:
        abort(503)


asset_list = AssetList("global_list")
