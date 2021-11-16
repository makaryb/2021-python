import os
import logging
from argparse import Namespace

from asset import process_cli_arguments, setup_logging


def test_debug_logging_level(capsys, caplog):
    with open("asset_example.txt", "w") as fout:
        fout.write("property   1000    0.1")
    with open("asset_example.txt", "r") as fin:
        args = Namespace(asset_fin=fin,
                         periods=[1, 2, 5])
        setup_logging(logging_yaml_config_fpath='task_Boriskin_Makary_asset_log.conf.yml')
        process_cli_arguments(arguments=args)
        with caplog.at_level("DEBUG"):
            assert all(record.levelno <= logging.WARNING for record in caplog.records), (
                "application is unstable, there are WARNING+ level messages in logs"
            )
    clean_tmp_file("asset_example.txt")


def test_process_arguments_call_load_once(capsys, caplog):
    with open("asset_example.txt", "w") as fout:
        fout.write("property   1000    0.1")
    with open("asset_example.txt", "r") as fin:
        args = Namespace(asset_fin=fin, periods=[1, 2, 5])
        process_cli_arguments(arguments=args)
        captured = capsys.readouterr()
        assert "    1:    100.000\n    2:    210.000\n    5:    610.510\n" == captured.out
        with caplog.at_level("DEBUG"):
            assert any("building asset object" in message for message in caplog.messages), (
                "there is no 'building asset object' message in logs"
            )
    clean_tmp_file("asset_example.txt")


def _rm_r(path):
    if os.path.exists(path):
        os.remove(path)


def clean_tmp_file(filepath):
    _rm_r(filepath)

