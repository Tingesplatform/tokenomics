import pytest

from models.dao import Governance
from models.tokens import TingesToken
from models.account import Account


@pytest.fixture(autouse=True)
def reset_accounts_storage():
    Account.ACCOUNTS_STORAGE = {}


@pytest.fixture
def governance(generate_accounts):
    founders = generate_accounts(5)
    governance = Governance(
        organization_name='Tinges',
        founders=founders,
        min_involv_prcnt=50,
        min_cons_vote_prcnt=80)
    token = TingesToken()
    governance.set_token(token)
    for f in founders:
        governance.mint_to_founder(f, 1000)
    governance.finish_genesis()

    return governance
