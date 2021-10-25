#!/usr/bin/env python3

""" InvertedIndex implementation.
InvertedIndex provides functionality to a database index storing a mapping from
content, such as words or numbers, to its locations in a set of documents.

use InvertedIndex.query(self, words: List[str]) -> List[int] to get list of
documents in which query presented;
use InvertedIndex.dump(self, filepath: str) -> None to write created
InvertedIndex (dictionary) on disc;
use InvertedIndex.load(cls, filepath: str) -> InvertedIndex to get loaded
from disc InvertedIndex;
use load_documents(filepath: str) -> Dict[int, str] to load set of documents
from dataset to dictionary;
use build_inverted_index(load_documents(filepath: str)) -> InvertedIndex to
create an InvertedIndex object from the set of documents imported previously
from dataset.
"""

from __future__ import annotations

import json
import re
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import Dict, List

DEFAULT_DATASET_PATH = "wikipedia_sample"
DEFAULT_INVERTED_INDEX_STORE_PATH = "inverted.index"


class InvertedIndex:
    """one-liner description

    @param :name: -
    === Header level 3
    I want to say that:
    - $index is an optional parameter;
    - by default $index is None;
    - in this method $index = {}.

    $index - is an "inverted index" instance which is a dictionary with int keys and str values
    """

    def __init__(self, index: Dict[str, List[int]] = None):
        if index:
            self.index = index
        else:
            self.index = {}

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        assert isinstance(words, list), (
            "query should be provided with a list of words, but user provided: "
            f"{repr(words)}"
        )
        if len(words) == 1:
            term = words[0]
            return self.index[term] if term in self.index else []

        result_for_each = {term: self.index[term] for term in words if term in self.index}
        docs_list = list(result_for_each.values())
        result = []
        for next_list in docs_list[1:]:
            for doc in docs_list[0]:
                if doc in next_list:
                    result.append(doc)
        return result

    def dump(self, filepath: str) -> None:
        """Dumps the inverted index dict to the given path"""
        with open(filepath, 'w', encoding='utf8') as fout:
            json.dump(self.index, fout)

    @classmethod
    def load(cls, filepath: str) -> InvertedIndex:
        """Loads the inverted index dict by the given path"""
        with open(filepath, 'r', encoding='utf8') as fin:
            return cls(index=json.load(fin))

    def __eq__(self, other):
        outcome = (
            self.index == other.index
        )
        return outcome


def load_documents(filepath: str) -> Dict[int, str]:
    """
    Loads the documents dataset by the given path.
    Return the dict with articles' ids as keys and articles' contents as values.
    """
    print(f"loading documents from path {filepath} to build inverted index...", file=sys.stderr)
    with open(filepath, 'r', encoding='utf8') as dataset:
        lines = dataset.readlines()
    documents: Dict[int, str] = {}
    for line in lines:
        content: str
        doc_id, content = line.lower().split("\t", 1)
        doc_id = int(doc_id)
        documents[doc_id] = content.strip()
    return documents


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """
    Build the InvertedIndex object by the given dict of documents.
    Return the InvertedIndex object.
    """
    print("building inverted index for provided documents", file=sys.stderr)
    inverted = InvertedIndex()
    doc_id: int
    for doc_id, content in documents.items():
        terms: List[str] = re.split(r"\W+", content)
        filtered_terms = list(dict.fromkeys(terms))
        for term in filtered_terms:
            if term not in inverted.index:
                inverted.index[term] = [doc_id]
            else:
                inverted.index[term].append(doc_id)
    return inverted


def callback_build(arguments):
    """Callback for build specifier: dump inverted index on hard drive"""
    if arguments.strategy == "json":
        documents = load_documents(arguments.dataset)
        inverted_index = build_inverted_index(documents)
        inverted_index.dump(arguments.output)
    elif arguments.strategy == "pickle":
        print("pickle strategy not implemented yet")


def callback_query(arguments):
    """Callback for query specifier: documents with words"""
    inverted_index = InvertedIndex.load(arguments.json_index)
    for query in arguments.query:
        document_ids = inverted_index.query(query)
        print(', '.join(map(str, document_ids)))


def setup_parser(parser):
    """Setup arguments parser"""
    subparsers = parser.add_subparsers(
        help="choose command"
    )

    build_parser = subparsers.add_parser(
        "build",
        help="build inverted index and save in binary format into hard drive",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    build_parser.add_argument(
        "-s", "--strategy",
        choices=["json", "pickle"],
        default="json",
        help="choose the strategy: json or pickle (not implemented yet)",
    )
    build_parser.add_argument(
        "-d", "--dataset",
        default=DEFAULT_DATASET_PATH,
        help="path to dataset to load, default path is %(default)s",
    )
    build_parser.add_argument(
        "-o", "--output",
        default=DEFAULT_INVERTED_INDEX_STORE_PATH,
        help="path to store inverted index in a binary format, default path is %(default)s",
    )
    build_parser.set_defaults(callback=callback_build)

    query_parser = subparsers.add_parser(
        "query",
        help="query inverted index",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    query_parser.add_argument(
        "-ji", "--json-index", dest="json_index",
        default=DEFAULT_INVERTED_INDEX_STORE_PATH,
        help="path to read inverted index in a binary format, default path is %(default)s",
    )
    query_parser.add_argument(
        "-q", "--query", required=True, nargs="+",
        action="append",
        help="query to run against inverted index",
    )
    query_parser.set_defaults(callback=callback_query)


def main():
    """For example"""
    parser = ArgumentParser(
        prog="inverted-index",
        description="tool to build, dump, load and query inverted index",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
