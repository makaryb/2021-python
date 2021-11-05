import os.path
from argparse import Namespace

import pytest

from task_Boriskin_Makary_inverted_index_cli import InvertedIndex, load_documents, build_inverted_index
from task_Boriskin_Makary_inverted_index_cli import callback_query, process_queries
from task_Boriskin_Makary_inverted_index_cli import callback_build, process_build
from task_Boriskin_Makary_inverted_index_cli import DEFAULT_INVERTED_INDEX_STORE_PATH

DEFAULT_TEST_INVERTED_INDEX_STORE_PATH = 'inverted_index_test.txt'
DEFAULT_TEST_QUERIES_STORE_PATH = 'queries.txt'

DATASET_BIG_FILEPATH = 'wikipedia_sample'
DATASET_SMALL_FILEPATH = 'test_dataset.txt'


def test_can_instantiate_inverted_index():
    InvertedIndex()
    InvertedIndex(
        index={"butterfly": [1], "the": [1, 2], "bright": [1, 3], "blue": [1, 3]}
    )


def test_load_dataset_into_dict():
    documents = load_documents(filepath='test_dataset.txt')
    butterfly_expected_value = "butterfly	the bright blue butterfly hangs on the breeze"
    forget_expected_value = "forget	it is better to forget the great sky and to retire from every wind"
    sunlight_expected_value = "sunlight	under blue sky, in bright sunlight, one need not search around"
    assert butterfly_expected_value == documents[1], (
        f"\nExpected:\n{butterfly_expected_value}\nYou got:\n{documents[1]}"
    )
    assert forget_expected_value == documents[2], (
        f"\nExpected:\n{forget_expected_value}\nYou got:\n{documents[2]}"
    )
    assert sunlight_expected_value == documents[3], (
        f"\nExpected:\n{sunlight_expected_value}\nYou got:\n{documents[3]}"
    )


def test_build_inverted_index():
    documents = load_documents(filepath='test_dataset.txt')
    inverted = build_inverted_index(documents=documents)
    butterfly_expected_values = [1]
    bright_expected_values = [1, 3]
    blue_expected_values = [1, 3]
    forget_expected_values = [2]
    sky_expected_values = [2, 3]
    assert butterfly_expected_values == inverted.index['butterfly'], (
        f"\nExpected: {butterfly_expected_values}\nYou got: {inverted.index['butterfly']}"
    )
    assert bright_expected_values == inverted.index['bright'], (
        f"\nExpected: {bright_expected_values}\nYou got: {inverted.index['bright']}"
    )
    assert blue_expected_values == inverted.index['blue'], (
        f"\nExpected: {blue_expected_values}\nYou got: {inverted.index['blue']}"
    )
    assert forget_expected_values == inverted.index['forget'], (
        f"\nExpected: {forget_expected_values}\nYou got: {inverted.index['forget']}"
    )
    assert sky_expected_values == inverted.index['sky'], (
        f"\nExpected: {sky_expected_values}\nYou got: {inverted.index['sky']}"
    )


def test_dump_inverted_index_on_disc():
    documents = load_documents(filepath='test_dataset.txt')
    inverted = build_inverted_index(documents=documents)
    inverted.dump(filepath="inverted_index_test.txt")
    assert os.path.exists('inverted_index_test.txt') is True


def test_get_inverted_index_from_disc():
    documents = load_documents(filepath='test_dataset.txt')
    inverted = build_inverted_index(documents=documents)
    inverted.dump(filepath="inverted_index_test.txt")
    inverted2 = InvertedIndex.load(filepath='inverted_index_test.txt')
    assert inverted == inverted2, (
        "InvertedIndex made with build function and by load a dump file are not the same"
    )
    butterfly_expected_values = [1]
    bright_expected_values = [1, 3]
    blue_expected_values = [1, 3]
    forget_expected_values = [2]
    sky_expected_values = [2, 3]
    assert butterfly_expected_values == inverted.index['butterfly'], (
        f"\nExpected: {butterfly_expected_values}\nYou got: {inverted.index['butterfly']}"
    )
    assert bright_expected_values == inverted.index['bright'], (
        f"\nExpected: {bright_expected_values}\nYou got: {inverted.index['bright']}"
    )
    assert blue_expected_values == inverted.index['blue'], (
        f"\nExpected: {blue_expected_values}\nYou got: {inverted.index['blue']}"
    )
    assert forget_expected_values == inverted.index['forget'], (
        f"\nExpected: {forget_expected_values}\nYou got: {inverted.index['forget']}"
    )
    assert sky_expected_values == inverted.index['sky'], (
        f"\nExpected: {sky_expected_values}\nYou got: {inverted.index['sky']}"
    )


def test_find_documents_by_specified_words():
    documents = load_documents(filepath='test_dataset.txt')
    inverted = build_inverted_index(documents=documents)
    butterfly_expected_values = [1]
    bright_expected_values = [1, 3]
    blue_expected_values = [1, 3]
    forget_expected_values = [2]
    sky_expected_values = [2, 3]
    blue_sky_expected_value = [3]
    butterfly_forget_expected_value = []
    bright_blue_forget_expected_value = [1, 3]
    assert butterfly_expected_values == inverted.query(['butterfly']), (
        f"\nExpected: {butterfly_expected_values}\nYou got: {inverted.query(['butterfly'])}"
    )
    assert bright_expected_values == inverted.query(['bright']), (
        f"\nExpected: {bright_expected_values}\nYou got: {inverted.query(['bright'])}"
    )
    assert blue_expected_values == inverted.query(['blue']), (
        f"\nExpected: {blue_expected_values}\nYou got: {inverted.query(['blue'])}"
    )
    assert forget_expected_values == inverted.query(['forget']), (
        f"\nExpected: {forget_expected_values}\nYou got: {inverted.query(['forget'])}"
    )
    assert sky_expected_values == inverted.query(['sky']), (
        f"\nExpected: {sky_expected_values}\nYou got: {inverted.query(['sky'])}"
    )
    assert butterfly_forget_expected_value == inverted.query(['butterfly', 'forget']), (
        f"\nExpected: {butterfly_forget_expected_value}\nYou got: {inverted.query(['butterfly', 'forget'])}"
    )
    assert blue_sky_expected_value == inverted.query(['blue', 'sky']), (
        f"\nExpected: {blue_sky_expected_value}\nYou got: {inverted.query(['blue', 'sky'])}"
    )
    assert bright_blue_forget_expected_value == inverted.query(['bright', 'blue']), (
        f"\nExpected: {bright_blue_forget_expected_value}\nYou got: {inverted.query(['bright', 'blue'])}"
    )


def test_process_queries_can_process_all_queries_from_correct_file(capsys):
    with open(DEFAULT_TEST_QUERIES_STORE_PATH) as queries_fin:
        process_queries(inverted_index_filepath=DEFAULT_TEST_INVERTED_INDEX_STORE_PATH,
                        query_file=queries_fin,
                        query=None)
        captured = capsys.readouterr()
        assert "load inverted index" not in captured.out, (
            f"\nExpected: not in stdout\nYou got: in stdout"
        )
        assert "load inverted index" in captured.err, (
            f"\nExpected: in stderr\nYou got: not in stderr"
        )
        assert "1,3" in captured.out, (
            f"\nExpected: 1,3 in stdout\nYou got: 1,3 not in stdout"
        )


def test_callback_query_can_process_all_queries_from_correct_file(capsys):
    with open(DEFAULT_TEST_QUERIES_STORE_PATH) as queries_fin:
        query_arguments = Namespace(inverted_index_filepath=DEFAULT_TEST_INVERTED_INDEX_STORE_PATH,
                                    query_file=queries_fin,
                                    query=None)
        callback_query(query_arguments)
        captured = capsys.readouterr()
        assert "load inverted index" not in captured.out, (
            f"\nExpected: not in stdout\nYou got: in stdout"
        )
        assert "load inverted index" in captured.err, (
            f"\nExpected: in stderr\nYou got: not in stderr"
        )
        assert "1,3" in captured.out, (
            f"\nExpected: 1,3 in stdout\nYou got: 1,3 not in stdout"
        )


@pytest.mark.slow
@pytest.mark.parametrize(
    'dataset_filepath',
    [
        pytest.param(DATASET_BIG_FILEPATH, marks=[pytest.mark.slow]),
        DATASET_SMALL_FILEPATH
    ]
)
def test_process_build_can_load_documents(dataset_filepath):
    process_build(strategy='json',
                  dataset_filepath=dataset_filepath,
                  inverted_index_filepath=DEFAULT_INVERTED_INDEX_STORE_PATH)


@pytest.mark.slow
@pytest.mark.parametrize(
    'dataset_filepath',
    [
        pytest.param(DATASET_BIG_FILEPATH, marks=[pytest.mark.slow]),
        DATASET_SMALL_FILEPATH
    ]
)
def test_callback_build_can_load_documents(dataset_filepath):
    build_arguments = Namespace(strategy='json',
                                dataset_filepath=dataset_filepath,
                                inverted_index_filepath=DEFAULT_INVERTED_INDEX_STORE_PATH)
    callback_build(build_arguments)
