import pytest
from models.dao import Governance, AccountNotFounder, \
    TokenIsNotSet, PollCantBeFinished, ConsesusNotReached, CantExecutreProposal
from models.helpers import InvalidStateError


@pytest.fixture
def governance(generate_accounts, tinges_token):
    governance = Governance(
        organization_name='Tinges',
        founders=generate_accounts(3),
        min_involv_prcnt=50,
        min_cons_vote_prcnt=80)

    governance.set_token(tinges_token)

    return governance


@pytest.fixture
def governance_w_proposal(governance):
    for f in governance.founders:
        governance.mint_to_founder(f, 1000)
    governance.finish_genesis()
    governance.create_proposal(
        description='Test proposal', exec_data='self.foo="bar"')

    return governance


def test_governance_createion(generate_accounts):
    founders = generate_accounts(3)
    governance = Governance(
        organization_name='Tinges',
        founders=founders,
        min_involv_prcnt=50,
        min_cons_vote_prcnt=80)

    assert governance.organization_name == 'Tinges'
    assert governance.founders == founders
    assert governance.current_state == 'Genesis'
    assert governance.staked_tokens == {}
    assert governance.token is None
    assert governance.total_staked == 0
    assert governance.proposals == []
    assert governance.min_involv_prcnt == 50
    assert governance.min_cons_vote_prcnt == 80
    assert governance.create_proposal.caller_name == 'staker'


def test_successful_set_token(generate_accounts, tinges_token):
    founders = generate_accounts(3)
    governance = Governance(
        organization_name='Tinges',
        founders=founders,
        min_involv_prcnt=50,
        min_cons_vote_prcnt=80)
    governance.set_token(tinges_token)

    assert governance.token == tinges_token


def test_set_token_not_in_genesus(generate_accounts, tinges_token):
    founders = generate_accounts(3)
    governance = Governance(
        organization_name='Tinges',
        founders=founders,
        min_involv_prcnt=50,
        min_cons_vote_prcnt=80)
    governance.set_state('Locked')

    with pytest.raises(InvalidStateError):
        governance.set_token(tinges_token)


def test_successful_mint_to_founder(governance):
    founder = governance.founders[0]
    governance.mint_to_founder(founder, 1000)

    assert governance.token.balance_of(founder) == 1000
    assert governance.staked_tokens[founder] == 1000
    assert governance.total_staked == 1000


def test_mint_to_not_founder(governance, account):
    with pytest.raises(AccountNotFounder):
        governance.mint_to_founder(account, 1000)


def test_mint_to_founder_wo_token(generate_accounts):
    founders = generate_accounts(3)
    governance = Governance(
        organization_name='Tinges',
        founders=founders,
        min_involv_prcnt=50,
        min_cons_vote_prcnt=80)

    with pytest.raises(TokenIsNotSet):
        governance.mint_to_founder(founders[0], 1000)


def test_successful_finish_genesus(governance):
    governance.finish_genesis()

    assert governance.current_state == 'Private'


def test_successful_create_proposal(governance):
    governance.finish_genesis()
    governance.create_proposal(
        description='Test proposal', exec_data='self.foo="bar"')

    assert len(governance.proposals) == 1

    proposal = governance.proposals[0]
    assert proposal.description == 'Test proposal'
    assert proposal.exec_data == 'self.foo="bar"'
    assert proposal.accepted is False
    assert proposal.finished is False
    assert proposal.executed is False
    assert proposal.poll.governance == governance


def test_create_proposal_w_wrong_state(governance):
    assert governance.current_state == 'Genesis'

    with pytest.raises(InvalidStateError):
        governance.create_proposal(
            description='Test proposal', exec_data='self.foo="bar"')


def test_successful_finish_proposal_poll(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    for f in governance_w_proposal.founders:
        proposal.poll.vote_for(f)
    governance_w_proposal.finish_proposal_poll(proposal)

    assert proposal.accepted
    assert proposal.finished
    assert proposal.executed is False


def test_finish_finished_proposal(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    for f in governance_w_proposal.founders:
        proposal.poll.vote_for(f)
    governance_w_proposal.finish_proposal_poll(proposal)

    with pytest.raises(PollCantBeFinished):
        governance_w_proposal.finish_proposal_poll(
            governance_w_proposal.proposals[0])


def test_various_vote_weight_calculcation(governance):
    rich_founder = governance.founders[0]
    other_founders = governance.founders[1:]

    governance.mint_to_founder(rich_founder, 8500)
    for f in other_founders:
        governance.mint_to_founder(f, 1000)
    governance.finish_genesis()
    proposal = governance.create_proposal(
        description='Test proposal', exec_data='self.foo="bar"')
    proposal.poll.vote_for(rich_founder)
    for f in other_founders:
        proposal.poll.vote_against(f)
    governance.finish_proposal_poll(proposal)

    assert proposal.finished
    assert proposal.accepted


def test_finish_proposal_not_invlolved(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    proposal.poll.vote_for(governance_w_proposal.founders[0])

    with pytest.raises(ConsesusNotReached):
        governance_w_proposal.finish_proposal_poll(
            governance_w_proposal.proposals[0])

    assert not proposal.accepted
    assert not proposal.finished
    assert not proposal.executed


def test_finish_proposal_poll_wo_consesus(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    proposal.poll.vote_for(governance_w_proposal.founders[0])
    proposal.poll.vote_for(governance_w_proposal.founders[1])
    proposal.poll.vote_against(governance_w_proposal.founders[2])

    with pytest.raises(ConsesusNotReached):
        governance_w_proposal.finish_proposal_poll(
            governance_w_proposal.proposals[0])

    assert not proposal.accepted
    assert not proposal.finished
    assert not proposal.executed


def test_finish_proposal_poll_w_wrong_state(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    for f in governance_w_proposal.founders:
        proposal.poll.vote_for(f)

    governance_w_proposal.set_state('Locked')

    with pytest.raises(InvalidStateError):
        governance_w_proposal.finish_proposal_poll(
            governance_w_proposal.proposals[0])

    assert not proposal.accepted
    assert not proposal.finished
    assert not proposal.executed


def test_successful_execute_proposal(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    for f in governance_w_proposal.founders:
        proposal.poll.vote_for(f)
    governance_w_proposal.finish_proposal_poll(proposal)

    governance_w_proposal.execute_proposal(proposal)

    assert proposal.executed
    assert governance_w_proposal.foo == 'bar'


def test_execute_executed_proposal(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    for f in governance_w_proposal.founders:
        proposal.poll.vote_for(f)
    governance_w_proposal.finish_proposal_poll(proposal)
    governance_w_proposal.execute_proposal(proposal)

    with pytest.raises(CantExecutreProposal):
        governance_w_proposal.execute_proposal(proposal)


def test_execute_not_finished_proposal(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]

    with pytest.raises(CantExecutreProposal):
        governance_w_proposal.execute_proposal(proposal)


def test_execute_not_accepted_proposal(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    for f in governance_w_proposal.founders:
        proposal.poll.vote_against(f)

    with pytest.raises(CantExecutreProposal):
        governance_w_proposal.execute_proposal(proposal)


def test_execute_proposal_w_wrong_state(governance_w_proposal):
    proposal = governance_w_proposal.proposals[0]
    for f in governance_w_proposal.founders:
        proposal.poll.vote_for(f)
    governance_w_proposal.finish_proposal_poll(proposal)
    governance_w_proposal.set_state('Locked')

    with pytest.raises(InvalidStateError):
        governance_w_proposal.execute_proposal(proposal)

    assert not hasattr(governance_w_proposal, 'foo')
