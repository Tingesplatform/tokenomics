from tokenomics import Account, ERC20Token, Bucket, Tap

def test_mint_to_single_account():
    alice = Account()
    token = ERC20Token()
    assert token.total_supply == 0
    token.mint(alice, 100)
    assert token.balance_of(alice) == 100
    assert token.total_supply == 100

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

