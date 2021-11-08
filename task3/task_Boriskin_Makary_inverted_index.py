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

import os
from io import TextIOWrapper
import json
import re
import sys
from struct import pack, unpack, calcsize
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType, ArgumentTypeError
from typing import Dict, List

DEFAULT_DATASET_PATH = "wikipedia_sample"
DEFAULT_INVERTED_INDEX_STORE_PATH = "inverted.index"


class EncodedFileType(FileType):
    def __call__(self, string):
        # the special argument "-" means sys.std{in,out} in right encoding
        if string == '-':
            if 'r' in self._mode:
                stdin = TextIOWrapper(sys.stdin.buffer, encoding=self._encoding)
                return stdin
            elif 'w' in self._mode:
                stdout = TextIOWrapper(sys.stdout.buffer, encoding=self._encoding)
                return stdout
            else:
                msg = 'argument "-" with mode %r' % self._mode
                raise ValueError(msg)

        # all other arguments are used as file names
        try:
            return open(string, self._mode, self._bufsize, self._encoding, self._errors)
        except OSError as e:
            message = "can't open '%s': %s"
            raise ArgumentTypeError(message % (string, e))


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
            self.index = dict()

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        assert isinstance(words, list), (
            "query should be provided with a list of words, but user provided: "
            f"{repr(words)}"
        )

        docs_list = []
        for term in words:
            if term in self.index:
                docs_list.append(self.index[term])
            else:
                docs_list.append([])
        result = []
        for doc in docs_list[0]:
            if all(doc in docs for docs in docs_list[1:]):
                if doc not in result:
                    result.append(doc)
        return result

    def dump(self, filepath: str) -> None:
        """Dumps the inverted index dict to the given path"""
        with open(filepath, 'wb') as fout:
            for word in self.index:
                word_and_docs_count = {}
                doc_ids = self.index[word]
                word_and_docs_count[word] = len(doc_ids)
                header: bytes = json.dumps(word_and_docs_count).encode('utf-8')
                meta: int = len(header)
                fout.write(pack('>I', meta))
                fout.write(header)
                fout.write(pack(f'>{len(doc_ids)}H', *doc_ids))

    @classmethod
    def load(cls, filepath: str) -> InvertedIndex:
        """Loads the inverted index dict by the given path"""
        print(f"load inverted index from filepath {filepath}", file=sys.stderr)

        size = os.path.getsize(filepath)
        inverted_index = dict()
        fin = open(filepath, 'rb')
        while fin.tell() < size:
            meta = unpack('>I', fin.read(calcsize('>I')))[0]
            header = unpack(f'{meta}s', fin.read(calcsize(f'{meta}s')))[0].decode('utf-8')
            word_and_docs_count = json.loads(header)
            for word in word_and_docs_count:
                docs_count = word_and_docs_count[word]
                doc_ids = list(
                    unpack(f'>{docs_count}H', fin.read(calcsize(f'>{docs_count}H')))
                )
                inverted_index[word] = doc_ids
        fin.close()

        inverted = InvertedIndex()
        inverted.index = inverted_index
        return inverted

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
    return process_build(arguments.strategy,
                         arguments.dataset_filepath,
                         arguments.inverted_index_filepath)


def process_build(strategy, dataset_filepath, inverted_index_filepath):
    if strategy == "json":
        documents = load_documents(dataset_filepath)
        inverted_index = build_inverted_index(documents)
        inverted_index.dump(inverted_index_filepath)
    elif strategy == "struct":
        print("pickle strategy not implemented yet")


def callback_query(arguments):
    """Callback for query specifier: documents with words"""
    print(f"call query subcommand with arguments: {arguments}", file=sys.stderr)
    return process_queries(inverted_index_filepath=arguments.inverted_index_filepath,
                           query=arguments.query,
                           query_file=arguments.query_file)


def process_queries(inverted_index_filepath, query_file, query=None):
    """Read queries from filepath specified in arguments"""
    inverted_index = InvertedIndex.load(inverted_index_filepath)
    if not query:
        for q in query_file:
            q = q.strip()
            q = re.findall(r'\w+', q)
            print(f"use the following query to run against InvertedIndex: {q}", file=sys.stderr)
            document_ids = inverted_index.query(q)
            print(','.join(map(str, document_ids)))
    else:
        for q in query:
            document_ids = inverted_index.query(q)
            print(','.join(map(str, document_ids)))


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
        choices=["json", "struct"],
        default="struct",
        help="choose the strategy: json or struct (by default)",
    )
    build_parser.add_argument(
        "-d", "--dataset",
        dest='dataset_filepath',
        default=DEFAULT_DATASET_PATH,
        help="path to dataset to load, default path is %(default)s",
    )
    build_parser.add_argument(
        "-o", "--output",
        dest='inverted_index_filepath',
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
        "--index",
        default=DEFAULT_INVERTED_INDEX_STORE_PATH,
        dest='inverted_index_filepath',
        help="path to read inverted index in a binary format, default path is %(default)s",
    )
    query_parser.add_argument(
        "-s", "--strategy",
        choices=["json", "struct"],
        default="struct",
        help="choose the strategy: json or struct (by default)",
    )
    query_file_group = query_parser.add_mutually_exclusive_group(required=True)
    query_file_group.add_argument(
        "--query-file-utf8", dest="query_file",
        type=EncodedFileType('r', encoding='utf-8'),
        default=TextIOWrapper(sys.stdin.buffer, encoding='utf-8'),
        help="query file in utf8 to get queries for inverted index",
    )
    query_file_group.add_argument(
        "--query-file-cp1251", dest="query_file",
        type=EncodedFileType('r', encoding='cp1251'),
        default=TextIOWrapper(sys.stdin.buffer, encoding='cp1251'),
        help="query file in cp1251 to get queries for inverted index",
    )
    query_file_group.add_argument(
        "-q", "--query", nargs="+",
        action="append",
        help="query to run against inverted index",
    )
    query_parser.set_defaults(callback=callback_query)


def main():
    """For example"""
    parser = ArgumentParser(
        prog="Inverted Index CLI",
        description="tool to build, dump, load and query inverted index",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
