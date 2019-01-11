import pytest

from models.tokens import ERC20Token, TingesToken, \
    DAIStableCoin, USDTStableCoin


@pytest.fixture
def token():
    return ERC20Token()


def test_token_creation(token):
    assert len(token.address) == 42
    assert token.balances == {}
    assert token.total_supply == 0
    assert token.name is None


def test_mint_tokens(token, account):
    token.mint(account, 1000)

    assert token.balance_of(account) == 1000


def test_successful_tokens_transfer(token, generate_accounts):
    sender, receiver = generate_accounts(2)

    token.mint(sender, 1000)
    token.transfer(sender, receiver, 1000)

    assert token.balance_of(sender) == 0
    assert token.balance_of(receiver) == 1000


def test_insufficient_tokens_for_transfer(token, generate_accounts):
    sender, receiver = generate_accounts(2)

    token.mint(sender, 500)

    with pytest.raises(AssertionError, match='Insufficient tokens for transfer'):
        token.transfer(sender, receiver, 1000)

    assert token.balance_of(sender) == 500
    assert token.balance_of(receiver) == 0


def test_tinges_token():
    assert TingesToken().name == 'TNG'


def test_dai_stablecoin():
    assert DAIStableCoin().name == 'DAI'
