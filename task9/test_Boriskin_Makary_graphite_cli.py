from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter
)

from task_Boriskin_Makary_graphite_cli import (
    setup_parser,
    process_response,
    print_result,
    LOCALHOST, PORT,
    WIKI_PROXY_LOG_PATH
)


def test_print_result(capsys):
    print_result(response=('28', 0.1, 123), host=LOCALHOST, port=PORT)
    outcome = capsys.readouterr()
    expected = 'echo "wiki_search.article_found 28 123" | nc -N localhost 2003\n' \
               'echo "wiki_search.complexity 0.100 123" | nc -N localhost 2003\n'
    assert expected == outcome.out


def test_parser_can_make_correct_response(capsys):
    process_response(WIKI_PROXY_LOG_PATH, LOCALHOST, PORT)
    captured = capsys.readouterr()
    assert LOCALHOST, PORT in captured.out


def test_parser_to_process_pytest_cov():
    parser = ArgumentParser(
        prog="graphite_cli",
        description="tool to convert log file",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
