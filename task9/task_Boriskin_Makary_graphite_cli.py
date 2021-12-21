from argparse import (
    ArgumentParser,
    ArgumentDefaultsHelpFormatter
)
from datetime import datetime
import time
import sys

WIKI_PROXY_LOG_PATH = "wiki_search_app.log"
LOCALHOST = "localhost"
PORT = "2003"


def print_result(response: tuple, host, port):
    """output"""
    print(
        f'echo "wiki_search.article_found {response[0]} {response[2]}" | nc -N {host} {port}',
        file=sys.stdout
    )
    print(
        f'echo "wiki_search.complexity {response[1]:.3f} {response[2]}" | nc -N {host} {port}',
        file=sys.stdout
    )


def process_log_line_by_line(line: str):
    """log line parser"""
    query = ""
    list_log_line = line.split()
    data = [list_log_line[3], datetime.strptime(list_log_line[0], "%Y%m%d_%H%M%S.%f")]
    if list_log_line[2] == 'INFO':
        query = "".join(list_log_line[8:])
        data.append(list_log_line[4])
    elif list_log_line[2] == 'DEBUG':
        query = "".join(list_log_line[6:])
    return query, data


def get_from_logs(logs):
    """return response tuple"""
    time_start = 0
    time_finish = 0
    articles_amount = 0
    for log in logs:
        if log[0] == 'start':
            time_start = log[1]
        elif log[0] == 'finish':
            time_finish = log[1]
        elif log[0] == 'found':
            articles_amount = log[2]
    process_time = (time_finish - time_start).total_seconds()
    unix_time_stamp = int(time.mktime(
        time_finish.timetuple())
    )
    return articles_amount, process_time, unix_time_stamp


def process_response(process, host, port):
    """callback for print response"""
    logs = {}
    with open(process, "r", encoding='utf-8') as fin:
        lines = fin.readlines()
    for line in lines:
        query, parsed_data = process_log_line_by_line(line)
        logs.setdefault(query, []).append(parsed_data)
        if len(logs[query]) == 3:
            response = get_from_logs(logs[query])
            print_result(response, host, port)
            del logs[query]


def callback_process(arguments):
    """cli parser callback"""
    process_response(arguments.process, arguments.host, arguments.port)


def setup_parser(parser):
    """setup simple parser"""

    parser.add_argument(
        "--process",
        default=WIKI_PROXY_LOG_PATH,
        required=True,
        help="wiki proxy web service logs filepath, default is %(default)s",
    )

    parser.add_argument(
        "--host",
        default=LOCALHOST,
        required=True,
        help="host, default is %(default)s",
    )

    parser.add_argument(
        "--port",
        default=PORT,
        required=True,
        help="port, default is %(default)s",
    )

    parser.set_defaults(callback=callback_process)


def main():
    parser = ArgumentParser(
        prog="graphite_cli",
        description="cli tool to parse wiki proxy web service logs",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()
    arguments.callback(arguments)


if __name__ == "__main__":
    main()
