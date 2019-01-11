from datetime import datetime, timedelta
import pytest

from models.dao import Bucket


@pytest.fixture
def coupled_buckets(dai_stablecoin):
    parent_bucket = Bucket(
        name='Parent bucket',
        withdraw_begin=datetime.now(),
        token=dai_stablecoin,
        max_volume=1000)
    child_bucket = Bucket(
        name='Child bucket',
        withdraw_begin=datetime.now(),
        token=dai_stablecoin,
        max_volume=1000)
    parent_bucket.set_overflow_bucket(child_bucket)

    return (parent_bucket, child_bucket)


@pytest.mark.freeze_time
def test_bucket_creation(dai_stablecoin):
    bucket = Bucket(
        name='Test bucket',
        withdraw_begin=datetime.now(),
        token=dai_stablecoin,
        max_volume=1000
    )

    assert bucket.name == 'Test bucket'
    assert bucket.withdraw_begin == datetime.now()
    assert bucket.token == dai_stablecoin
    assert bucket.max_volume == 1000
    assert bucket.overflow_bkt is None
    assert bucket.set_overflow_bucket.caller_name == 'Governance'
    assert bucket.flush.caller_name == 'Governance'
    assert bucket.withdraw.caller_name == 'Tap'


def test_set_overflow_bucket(dai_stablecoin):
    parent_bucket = Bucket(
        name='Parent bucket',
        withdraw_begin=datetime.now(),
        token=dai_stablecoin,
        max_volume=1000
    )
    child_bucket = Bucket(
        name='Child bucket',
        withdraw_begin=datetime.now(),
        token=dai_stablecoin,
        max_volume=1000
    )
    parent_bucket.set_overflow_bucket(child_bucket)

    assert parent_bucket.overflow_bkt == child_bucket


def test_successful_flush(dai_stablecoin, coupled_buckets):
    parent, child = coupled_buckets
    dai_stablecoin.mint(parent, 1000)

    parent.flush()

    assert dai_stablecoin.balance_of(parent) == 1000
    assert dai_stablecoin.balance_of(child) == 0


def test_overflow_flush(dai_stablecoin, coupled_buckets):
    parent, child = coupled_buckets

    dai_stablecoin.mint(parent, 1500)

    parent.flush()

    assert dai_stablecoin.balance_of(parent) == 1000
    assert dai_stablecoin.balance_of(child) == 500


def test_child_overflow_flush(dai_stablecoin, coupled_buckets):
    parent, child = coupled_buckets

    dai_stablecoin.mint(parent, 5000)

    parent.flush()

    assert dai_stablecoin.balance_of(parent) == 1000
    assert dai_stablecoin.balance_of(child) == 4000


def test_successful_withdraw(account, dai_stablecoin):
    bucket = Bucket(
        name='Test bucket',
        withdraw_begin=datetime.now() - timedelta(days=1),
        token=dai_stablecoin,
        max_volume=1000
    )

    dai_stablecoin.mint(bucket, 1000)
    bucket.withdraw(account, 700)

    assert dai_stablecoin.balance_of(bucket) == 300
    assert dai_stablecoin.balance_of(account) == 700


def test_withdraw_before_begin(account, dai_stablecoin):
    bucket = Bucket(
        name='Test bucket',
        withdraw_begin=datetime.now() + timedelta(days=1),
        token=dai_stablecoin,
        max_volume=1000)

    dai_stablecoin.mint(bucket, 1000)
    bucket.withdraw(account, 700)

    assert dai_stablecoin.balance_of(bucket) == 1000
    assert dai_stablecoin.balance_of(account) == 0


def test_withdraw_too_much(account, dai_stablecoin):
    bucket = Bucket(
        name='Test bucket',
        withdraw_begin=datetime.now() + timedelta(days=1),
        token=dai_stablecoin,
        max_volume=1000)

    dai_stablecoin.mint(bucket, 1000)
    bucket.withdraw(account, 5000)

    assert dai_stablecoin.balance_of(bucket) == 1000
    assert dai_stablecoin.balance_of(account) == 0
