from models.account import Account


class AccountCantVote(Exception):
    pass


class Poll(Account):
    def __init__(self, governance: 'Governance'):
        super().__init__()

        self.governance = governance
        self.votes_for = []
        self.votes_against = []

    @property
    def total_votes(self):
        return len(self.votes_for) + len(self.votes_against)

    def can_vote(self, account: Account):
        return account not in self.votes_for and \
         account not in self.votes_against and \
         self.governance.can_vote(account)

    def vote_for(self, account: Account):
        if self.can_vote(account):
            self.votes_for.append(account)
        else:
            raise AccountCantVote()

    def vote_against(self, account: Account):
        if self.can_vote(account):
            self.votes_against.append(account)
        else:
            raise AccountCantVote()
