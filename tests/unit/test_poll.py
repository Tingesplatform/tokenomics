from unittest.mock import Mock
import pytest

from models.poll import Poll, AccountCantVote


@pytest.fixture
def governance():
    return Mock()


@pytest.fixture
def poll(governance):
    return Poll(governance)


def test_poll_createion(governance):
    poll = Poll(governance)

    assert poll.governance == governance
    assert poll.votes_for == []
    assert poll.votes_against == []
    assert poll.total_votes == 0


def test_successful_vote_for(poll, account):
    poll.governance.can_vote = Mock(return_value=True)
    poll.vote_for(account)

    assert poll.governance.can_vote.called_once_with(account=account)
    assert poll.votes_for == [account]
    assert poll.total_votes == 1


def test_successful_vote_against(poll, account):
    poll.governance.can_vote = Mock(return_value=True)
    poll.vote_against(account)

    assert poll.governance.can_vote.called_once_with(account=account)
    assert poll.votes_against == [account]
    assert poll.total_votes == 1


def test_account_cant_vote(poll, account):
    poll.governance.can_vote = Mock(return_value=False)

    with pytest.raises(AccountCantVote):
        poll.vote_for(account)


def test_vote_twice(poll, account):
    poll.governance.can_vote = Mock(return_value=True)
    poll.vote_for(account)

    with pytest.raises(AccountCantVote):
        poll.vote_for(account)
