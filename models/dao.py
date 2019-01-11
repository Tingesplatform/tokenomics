"""The tokenomics package for token economy modeling"""
import sys
from typing import List
from datetime import datetime
from dataclasses import dataclass

from models.account import Account
from models.tokens import ERC20Token, TingesToken
from models.poll import Poll
from models.helpers import StateMixin, check_caller, require_state


class Bucket(Account, StateMixin):
    """The container of predefined volume storing raised funds"""

    def __init__(
            self,
            name: str,
            withdraw_begin: datetime,
            token: ERC20Token = None,
            max_volume: int = sys.maxsize,
    ):
        super().__init__()

        self.name = name
        self.withdraw_begin = withdraw_begin
        self.token = token
        self.max_volume = max_volume
        self.overflow_bkt = None

    @check_caller('Governance')
    def flush(self):
        """Flushes extra tokens to the overflow bucket"""
        if self.overflow_bkt:
            token_balance = self.token.balance_of(self)

            if token_balance > self.max_volume:
                self.token.transfer(self, self.overflow_bkt, token_balance - self.max_volume)

            self.overflow_bkt.flush()

    @check_caller('Governance')
    def set_overflow_bucket(self, overflow_bkt: 'Bucket'):
        """Sets overflow bucket"""
        self.overflow_bkt = overflow_bkt

    # Should check validness of caller
    @check_caller('Tap')
    def withdraw(self, to: Account, amount: int):
        """Withdraws tokens"""
        if self.withdraw_begin <= datetime.now() and self.token.balance_of(self) >= amount:
            self.token.transfer(self, to, amount)

    def __str__(self):
        return f'Bucket {self.name} ({self.address})'

    __repr__ = __str__


class Tap(Account):
    """Withdraw limiter"""

    def __init__(
            self,
            withdrawer: Account,
            bucket: Bucket,
            description: str = None,
            rate: int = 0,
    ):
        super().__init__()

        self.withdrawer = withdrawer
        self.bucket = bucket
        self.description = description
        self.rate = rate

        self.last_withdraw = None
        self.excess_amount = None
        self.active = False

    @check_caller('Governance')
    def activate(self, last_withdraw=None):
        if last_withdraw:
            self.last_withdraw = last_withdraw
        else:
            self.last_withdraw = datetime.now()

        self.excess_amount = 0
        self.active = True

    @check_caller('Governance')
    def deactivate(self):
        self.active = False

    @check_caller('Governance')
    def set_rate(self, new_rate: int):
        self.rate = new_rate

    @property
    def available_by_rate(self):
        sec_from_last_wd = int((datetime.now() - self.last_withdraw).total_seconds())

        return sec_from_last_wd * self.rate

    @property
    def total_available(self):
        return self.available_by_rate + self.excess_amount

    @check_caller('withdrawer')
    def withdraw(self, amount: int):
        if self.active and amount <= self.total_available:
            diff = self.available_by_rate - amount

            if diff >= 0:
                self.excess_amount += diff
            else:
                self.excess_amount -= diff

            self.last_withdraw = datetime.now()

            self.bucket.withdraw(self.withdrawer, amount)

    @check_caller('withdrawer')
    def withdraw_all(self):
        self.withdraw(self.total_available)

    def __str__(self):
        return f'Tap {self.description} ({self.address})'

    __repr__ = __str__


class AccountNotFounder(Exception):
    pass


class TokenIsNotSet(Exception):
    pass


class PollCantBeFinished(Exception):
    pass


class ConsesusNotReached(Exception):
    pass


class CantExecutreProposal(Exception):
    pass


@dataclass
class Proposal:
    """Proposal struct for Governance contract"""
    description: str
    exec_data: str
    poll: Poll
    accepted: bool = False
    finished: bool = False
    executed: bool = False


class Governance(Account, StateMixin):
    """Main governance contract"""

    state_list = ['Genesis', 'Private', 'Public', 'Locked']

    def __init__(self, organization_name: str, founders: List[Account],
                 min_involv_prcnt: int, min_cons_vote_prcnt: int):
        super().__init__()

        self.organization_name = organization_name
        self.founders = founders
        self.staked_tokens = {}
        self.token = None
        self.proposals = []

        self.min_involv_prcnt = min_involv_prcnt
        self.min_cons_vote_prcnt = min_cons_vote_prcnt

        self.buckets = []
        self.taps = {}

        self.set_state('Genesis')

    @property
    def total_staked(self):
        return sum(self.staked_tokens.values())

    @property
    def total_stakers(self):
        return len(self.staked_tokens.keys())

    @require_state(['Genesis'])
    def set_token(self, token: TingesToken):
        self.token = token

    @require_state(['Genesis'])
    def mint_to_founder(self, founder: Account, amount: int):
        if founder not in self.founders:
            raise AccountNotFounder()

        if self.token:
            self.token.mint(founder, amount)
            self.staked_tokens[founder] = self.staked_tokens.get(founder, 0) + amount
        else:
            raise TokenIsNotSet()

    @require_state(['Genesis'])
    def finish_genesis(self):
        self.set_state('Private')

    @check_caller('staker')
    @require_state(['Private', 'Public'])
    def create_proposal(self, description: str, exec_data: str) -> Proposal:
        poll = Poll(governance=self)
        proposal = Proposal(
            description=description,
            exec_data=exec_data,
            poll=poll
        )

        self.proposals.append(proposal)

        return proposal

    def can_vote(self, account: Account) -> bool:
        return account in self.staked_tokens.keys()

    def can_finish_poll(self, poll: Poll) -> bool:
        total_voted_tokens = 0

        for v in poll.votes_for + poll.votes_against:
            total_voted_tokens += self.staked_tokens.get(v, 0)

        return total_voted_tokens / self.total_stakers > self.min_involv_prcnt / 100

    def compute_poll_result(self, poll: Poll) -> bool:
        tokens_for = 0
        for v in poll.votes_for:
            tokens_for += self.staked_tokens.get(v, 0)

        tokens_against = 0
        for v in poll.votes_against:
            tokens_against += self.staked_tokens.get(v, 0)

        if tokens_for / self.total_staked > self.min_cons_vote_prcnt / 100:
            return True

        if tokens_against / self.total_staked > self.min_cons_vote_prcnt / 100:
            return False

        raise ConsesusNotReached()

    @check_caller('staker')
    @require_state(['Private', 'Public'])
    def finish_proposal_poll(self, proposal: Proposal):
        assert proposal in self.proposals

        poll = proposal.poll

        if not proposal.finished and self.can_finish_poll(poll):
            proposal.accepted = self.compute_poll_result(proposal.poll)
            proposal.finished = True
        else:
            raise PollCantBeFinished()

    @check_caller('staker')
    @require_state(['Private', 'Public'])
    def execute_proposal(self, proposal: Proposal):  # pylint: disable=no-self-use
        if not proposal.executed and proposal.finished and proposal.accepted:
            exec(proposal.exec_data)  # pylint: disable=exec-used

            proposal.executed = True
        else:
            raise CantExecutreProposal()

    @check_caller('Governance')
    @require_state(['Private', 'Public'])
    def add_bucket(self, bucket: Bucket):
        self.buckets.append(bucket)

    def __str__(self):
        return f'Governance for {self.organization_name} ({self.address})'

    __repr__ = __str__
