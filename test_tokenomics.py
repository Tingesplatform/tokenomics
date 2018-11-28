from tokenomics import Account, ERC20Token, Bucket, Tap, Timer
from datetime import timedelta
import sys

def test_mint_to_single_account():
    alice = Account()
    token = ERC20Token()
    assert token.total_supply == 0
    token.mint(alice, 100)
    assert token.balance_of(alice) == 100
    assert token.total_supply == 100

def test_timer():
    timer = Timer()
    oldtime = timer.time
    timer.increment(100)
    assert timer.time - oldtime == timedelta(seconds=100)


def test_mint_and_transfer_all():
    alice = Account()
    bob = Account()
    token = ERC20Token()
    token.mint(alice, 100)
    token.transfer(alice, bob, 100)
    assert token.balance_of(alice) == 0
    assert token.balance_of(bob) == 100
    assert token.total_supply == 100

def test_mint_and_transfer_partial():
    alice = Account()
    bob = Account()
    token = ERC20Token()
    token.mint(alice, 100)
    token.transfer(alice, bob, 99)
    assert token.balance_of(alice) == 1
    assert token.balance_of(bob) == 99
    token.transfer(alice, bob, 1)
    assert token.balance_of(alice) == 0
    assert token.balance_of(bob) == 100
    token.transfer(bob, alice, 2)
    assert token.balance_of(alice) == 2
    assert token.balance_of(bob) == 98
    assert token.total_supply == 100

def test_bucket_overflow():
    token = ERC20Token()
    of_bkt = Bucket(token=token)
    bkt = Bucket(token=token, overflow_bkt=of_bkt)
    token.mint(bkt, 1000000)
    bkt.flush()
    assert token.balance_of(bkt) == 1000
    assert token.balance_of(of_bkt) == 1000000 - 1000
    assert token.total_supply == 1000000
    token.mint(bkt, 1000)
    bkt.flush()
    assert token.balance_of(of_bkt) == 1000000

def test_bucket_and_tap():
    timer = Timer()
    alice = Account()
    bob = Account()
    token = ERC20Token()
    bkt = Bucket(token=token)
    token.mint(bkt, 1000000)
    assert token.balance_of(bkt) == 1000000
    alices_tap = Tap(withdrawer=alice, upstream=bkt, timer=timer)
    bobs_tap = Tap(withdrawer=bob, upstream=bkt, state=Tap.State.CLOSED, timer=timer)
    assert token.balance_of(alice) == 0
    res = alices_tap.withdraw(1)
    assert res == True
    assert token.balance_of(alice) == 1
    assert token.balance_of(bob) == 0
    res = bobs_tap.withdraw(1)
    assert res == False
    assert token.balance_of(bob) == 0
    bobs_tap.set_rate(100)

def test_bucket_rate():
    timer = Timer()
    alice = Account()
    token = ERC20Token()
    bkt = Bucket(token=token)
    token.mint(bkt, 1000000)
    assert token.balance_of(bkt) == 1000000
    alices_tap = Tap(withdrawer=alice, upstream=bkt, rate=100, timer=timer)
    assert alices_tap.available == 0
    timer.increment(1000)
    alices_tap.update()
    assert alices_tap.available == 100000
    assert token.balance_of(alice) == 0
    assert token.balance_of(bkt) == 1000000
    res = alices_tap.withdraw(100000)
    assert res == True
    assert token.balance_of(alice) == 100000
    assert token.balance_of(bkt) == 1000000 - 100000
    res = alices_tap.withdraw(900000)
    assert res == False
    assert token.balance_of(alice) == 100000
    assert token.balance_of(bkt) == 1000000 - 100000
    timer.increment(2000)
    res = alices_tap.withdraw(200000)
    assert res == True
    assert token.balance_of(alice) == 300000
    assert token.balance_of(bkt) == 1000000 - 300000
    res = alices_tap.withdraw(1)
    assert res == False
    assert token.balance_of(alice) == 300000
    assert token.balance_of(bkt) == 1000000 - 300000

def test_tap_states():
    token = ERC20Token()
    bkt = Bucket(token=token)
    alice = Account()
    timer = Timer()
    alices_tap = Tap(withdrawer=alice, upstream=bkt, rate=100, timer=timer)
    assert alices_tap.state == Tap.State.PARTIAL
    alices_tap.close()
    assert alices_tap.state == Tap.State.CLOSED
    assert alices_tap.rate == 0
    alices_tap.open()
    assert alices_tap.state == Tap.State.OPEN
    assert alices_tap.rate == sys.maxsize
    alices_tap.set_rate(100)
    assert alices_tap.state == Tap.State.PARTIAL
    assert alices_tap.rate == 100

def test_withdraw_all():
    token = ERC20Token()
    bkt = Bucket(token=token)
    token.mint(bkt, 1000000000)
    alice = Account()
    timer = Timer()
    alices_tap = Tap(withdrawer=alice, upstream=bkt, rate=100, timer=timer)
    assert alices_tap.state == Tap.State.PARTIAL
    timer.increment(seconds=10)
    assert token.balance_of(alice) == 0
    assert alices_tap.get_available() == 1000
    res = alices_tap.withdraw_all()
    assert token.balance_of(alice) == 1000
    assert alices_tap.available == 0
    assert alices_tap.get_available() == 0
    assert token.balance_of(alices_tap) == 0









