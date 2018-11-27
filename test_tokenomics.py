from tokenomics import Account, ERC20Token

def test_mint_to_single_account():
    alice = Account("Alice")
    token = ERC20Token()
    assert token.total_supply == 0
    token.mint(alice, 100)
    assert token.balance_of(alice) == 100
    assert token.total_supply == 100

def test_mint_and_transfer_all():
    alice = Account("Alice")
    bob = Account("Bob")
    token = ERC20Token()
    token.mint(alice, 100)
    token.transfer(alice, bob, 100)
    assert token.balance_of(alice) == 0
    assert token.balance_of(bob) == 100
    assert token.total_supply == 100

def test_mint_and_transfer_partial():
    alice = Account("Alice")
    bob = Account("Bob")
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
