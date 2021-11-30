#!/usr/bin/env python3

""" HTML dump parser implementation.

use `python3 task_*web_spy.py gitlab` to get amount of free and enterprise Gitlab products
"""

import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import requests
from bs4 import BeautifulSoup

GITLAB_FEATURES_FILEPATH = "gitlab_features.html"
URL_GITLAB_FEATURES = "https://about.gitlab.com/features/"
DEFAULT_ENCODING = "utf-8"


def callback_gitlab():
    """Callback for gitlab specifier: parse HTML dump of gitlab features web-page"""
    process_gitlab_features(html_url=URL_GITLAB_FEATURES)


def process_gitlab_features(html_url: str, html_filepath=None):

    if not html_filepath:
        response = requests.get(html_url)
        text = response.content.decode(DEFAULT_ENCODING)

        free_products = get_free_products(expected_html=text)
        enterprise_products = get_enterprise_products(expected_html=text)
    else:
        logging_html = open(html_filepath).read()

        free_products = get_free_products(expected_html=logging_html)
        enterprise_products = get_enterprise_products(expected_html=logging_html)

    print(f'free products: {free_products}\nenterprise products: {enterprise_products}')


def get_free_products(expected_html):
    logging_soup = BeautifulSoup(expected_html, features="html.parser")
    return len(logging_soup.find_all("a", attrs={'title': "Available in GitLab SaaS Free"}))


def get_enterprise_products(expected_html):
    logging_soup = BeautifulSoup(expected_html, features="html.parser")
    return len(logging_soup.find_all("a", attrs={'title': "Not available in SaaS Free"}))


def setup_parser(parser):
    """Setup arguments parser"""
    subparsers = parser.add_subparsers(
        help="choose command"
    )

    gitlab_parser = subparsers.add_parser(
        "gitlab",
        help="info about free and enterprise Gitlab products to STDOUT",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    gitlab_parser.set_defaults(callback=callback_gitlab)


def main():
    """For example"""
    parser = ArgumentParser(
        prog="HTML dump parser CLI",
        description="tool to parse htmp dump",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback()


if __name__ == "__main__":
    main()
