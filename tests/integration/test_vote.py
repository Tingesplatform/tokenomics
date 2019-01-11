from datetime import datetime
import pytest

from models.dao import Bucket, Tap


@pytest.fixture
def bucket(dai_stablecoin):
    return Bucket(
        name='Test',
        withdraw_begin=datetime(2018, 3, 1),
        token=dai_stablecoin,
        max_volume=25000)


# Create Bucket
# Create Proposal for add Bucket
# Vote for Proposal
# Execute Proposal
def test_successful_vote_for_add_bucket(governance, bucket):
    proposal = governance.create_proposal(
        description='Add buckets',
        exec_data=f"self.add_bucket(Account.ACCOUNTS_STORAGE['{bucket.address}'])")
    poll = proposal.poll

    for f in governance.founders:
        poll.vote_for(f)
    governance.finish_proposal_poll(proposal)
    governance.execute_proposal(proposal)

    assert proposal.finished
    assert proposal.accepted
    assert proposal.executed
    assert governance.buckets == [bucket]


# Create Tap
# Create Proposal for Tap actications
# Vote against Proposal
def test_vote_against_activate_tap(governance, bucket, account):
    tap = Tap(
        withdrawer=account, bucket=bucket, description='development', rate=1)

    proposal = governance.create_proposal(
        description='Acticate tap',
        exec_data=f"Account.ACCOUNTS_STORAGE['{tap.address}'].activate()")
    poll = proposal.poll

    for f in governance.founders:
        poll.vote_against(f)
    governance.finish_proposal_poll(proposal)

    assert proposal.finished
    assert not proposal.accepted
    assert not proposal.executed
    assert not tap.active
