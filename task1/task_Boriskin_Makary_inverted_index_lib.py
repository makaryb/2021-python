from __future__ import annotations

import json
import re
from typing import Dict, List


class InvertedIndex:
    def __init__(self, index: Dict[str, List[int]] = None):
        if index:
            self.index = index
        else:
            self.index = dict()

    def query(self, words: List[str]) -> List[int]:
        """Return the list of relevant documents for the given query"""
        if len(words) == 1:
            term = words[0]
            return self.index[term] if term in self.index else []
        else:
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
        with open(filepath, 'w') as fout:
            json.dump(self.index, fout)

    @classmethod
    def load(cls, filepath: str) -> InvertedIndex:
        """Loads the inverted index dict by the given path"""
        with open(filepath, "r") as fin:
            return cls(index=json.load(fin))

    def __eq__(self, other):
        outcome = (
            self.index == other.index
        )
        return outcome


def load_documents(filepath: str) -> Dict[int, str]:
    """Loads the documents dataset by the given path.
    Return the dict with articles' ids as keys and articles' contents as values."""
    with open(filepath, encoding='utf8') as dataset:
        lines = dataset.readlines()
    documents: Dict[int, str] = {}
    for line in lines:
        content: str
        doc_id, content = line.lower().split("\t", 1)
        doc_id = int(doc_id)
        documents[doc_id] = content.strip()
    return documents


def build_inverted_index(documents: Dict[int, str]) -> InvertedIndex:
    """Build the InvertedIndex object by the given dict of documents.
    Return the InvertedIndex object."""
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


def main():
    documents = load_documents("wikipedia_sample")
    inverted_index = build_inverted_index(documents)
    inverted_index.dump("inverted.index")
    inverted_index = InvertedIndex.load("inverted.index")
    document_ids = inverted_index.query(["two", "words"])


if __name__ == "__main__":
    main()
