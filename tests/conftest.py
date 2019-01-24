import pytest

from models.account import Account
from models.tokens import TingesToken, DAIStableCoin, USDTStableCoin


@pytest.fixture
def account():
    return Account()


@pytest.fixture
def generate_accounts():
    def _generate_accounts(count):
        return [Account() for i in range(count)]

    return _generate_accounts


@pytest.fixture
def tinges_token():
    return TingesToken()


@pytest.fixture
def dai_stablecoin():
    return DAIStableCoin()


@pytest.fixture
def usdt_stablecoin():
    return USDTStableCoin()
