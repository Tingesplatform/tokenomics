from models.dao import Governance
from models.tokens import TingesToken


# Create Governance
# Create TingesToken
# Bind TingesToken to Governance
# Mint tokens to founders
# Finish genesis
def test_genesis(generate_accounts):
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

    assert governance.founders == founders
    assert governance.organization_name == 'Tinges'
    assert governance.staked_tokens == {f: 1000 for f in founders}
    assert governance.token == token
    assert governance.proposals == []
    assert governance.min_involv_prcnt == 50
    assert governance.min_cons_vote_prcnt == 80
    assert governance.current_state == 'Private'
    for f in founders:
        assert token.balance_of(f) == 1000
