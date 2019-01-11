from datetime import datetime
import pytest

from models.dao import Bucket, Tap


def test_withdraw(dai_stablecoin, freezer, generate_accounts):
    bucket1 = Bucket(
        name='March',
        withdraw_begin=datetime(2018, 3, 1),
        token=dai_stablecoin,
        max_volume=1000000)
    bucket2 = Bucket(
        name='April',
        withdraw_begin=datetime(2018, 4, 1),
        token=dai_stablecoin,
        max_volume=1500000)
    bucket3 = Bucket(
        name='March',
        withdraw_begin=datetime(2018, 5, 1),
        token=dai_stablecoin,
        max_volume=2000000)
    dai_stablecoin.mint(bucket1, 3000000)
    bucket1.set_overflow_bucket(bucket2)
    bucket2.set_overflow_bucket(bucket3)
    bucket1.flush()
    tap11 = Tap(
        withdrawer=generate_accounts(1)[0],
        bucket=bucket1,
        description='Development',
        rate=1)
    tap12 = Tap(
        withdrawer=generate_accounts(1)[0],
        bucket=bucket1,
        description='Development',
        rate=0.8)
    tap2 = Tap(
        withdrawer=generate_accounts(1)[0],
        bucket=bucket2,
        description='Development',
        rate=1.5)
    tap3 = Tap(
        withdrawer=generate_accounts(1)[0],
        bucket=bucket3,
        description='Development',
        rate=2)

    freezer.move_to(datetime(2018, 3, 1))
    tap11.activate()
    tap12.activate()
    tap2.activate()
    freezer.move_to(datetime(2018, 3, 15))
    tap11.withdraw(10000)

    assert dai_stablecoin.balance_of(tap11.withdrawer) == 10000
    assert dai_stablecoin.balance_of(bucket1) == 990000

    tap12.withdraw_all()
    assert dai_stablecoin.balance_of(tap12.withdrawer) == 967680
    assert dai_stablecoin.balance_of(bucket1) == 22320

    tap2.withdraw_all()
    assert dai_stablecoin.balance_of(tap2.withdrawer) == 0
    assert dai_stablecoin.balance_of(bucket2) == 1500000

    with pytest.raises(Exception):
        tap3.withdraw_all()
