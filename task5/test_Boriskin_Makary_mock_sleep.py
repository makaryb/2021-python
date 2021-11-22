from unittest.mock import patch

from sleepy import sleep_add, sleep_multiply


@patch("sleepy.sleep")
def test_can_mock_sleepy_sleep_add(mock_sleep):
    outcome = sleep_add(1, 2)
    assert 3 == outcome
    mock_sleep.assert_called_once_with(3)


@patch("time.sleep")
def test_can_mock_tme_sleepy_sleep_multiply(mock_sleep):
    outcome = sleep_multiply(2, 3)
    assert 6 == outcome
    mock_sleep.assert_called_once_with(5)
