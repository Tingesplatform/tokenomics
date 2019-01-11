from datetime import datetime, timedelta
from unittest.mock import Mock
import pytest

from models.dao import Tap


@pytest.fixture
def bucket():
    return Mock()


@pytest.fixture
def tap(account, bucket):
    return Tap(
        description='Test tap',
        withdrawer=account,
        bucket=bucket,
        rate=10000
    )


def test_tap_creation(account, bucket):
    tap = Tap(
        description='Test tap',
        withdrawer=account,
        bucket=bucket,
        rate=10000
    )

    assert tap.withdrawer == account
    assert tap.bucket == bucket
    assert tap.description == 'Test tap'
    assert tap.rate == 10000
    assert tap.last_withdraw is None
    assert tap.excess_amount is None
    assert tap.active is False
    assert tap.activate.caller_name == 'Governance'
    assert tap.deactivate.caller_name == 'Governance'
    assert tap.set_rate.caller_name == 'Governance'
    assert tap.withdraw.caller_name == 'withdrawer'
    assert tap.withdraw_all.caller_name == 'withdrawer'


@pytest.mark.freeze_time
def test_tap_activation(tap):
    tap.activate()

    assert tap.last_withdraw == datetime.now()
    assert tap.excess_amount == 0
    assert tap.active


def test_set_tap_rate(tap):
    tap.set_rate(25000)

    assert tap.rate == 25000


@pytest.mark.freeze_time
def test_zero_total_available(tap):
    tap.activate()

    assert tap.total_available == 0


@pytest.mark.freeze_time
def test_total_available_after_day(tap, freezer):
    tap.activate()
    freezer.move_to(datetime.now() + timedelta(days=1))

    assert tap.total_available == 864000000


@pytest.mark.freeze_time
def test_tap_withdraw(tap, freezer):
    tap.activate()
    freezer.move_to(datetime.now() + timedelta(days=1))
    tap.withdraw(64000000)

    tap.bucket.withdraw.assert_called_once_with(tap.withdrawer, 64000000)
    assert tap.last_withdraw == datetime.now()
    assert tap.excess_amount == 800000000
    assert tap.total_available == 800000000


@pytest.mark.freeze_time
def test_tap_withdraw_all(tap, freezer):
    tap.activate()
    freezer.move_to(datetime.now() + timedelta(days=1))
    tap.withdraw_all()

    tap.bucket.withdraw.assert_called_once_with(tap.withdrawer, 864000000)
    assert tap.last_withdraw == datetime.now()
    assert tap.excess_amount == 0
    assert tap.total_available == 0
