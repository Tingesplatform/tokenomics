from typing import Optional

from models.helpers import check_caller
from models.account import Account


class ERC20Token(Account):
    """Basic ERC-20 token class with balances and totalSupply"""

    name: Optional[str] = None

    def __init__(self):
        super().__init__()

        self.balances = {}
        self.total_supply = 0

    def balance_of(self, holder: Account) -> int:
        """Returns tokens balance of account"""

        return self.balances.get(holder.address, 0)

    @check_caller('Governance')
    def mint(self, to: Account, tokens: int):
        """Mints (creates new amount of) tokens for the given account"""

        if to.address not in self.balances:
            self.balances[to.address] = 0

        self.balances[to.address] += tokens
        self.total_supply += tokens

    def transfer(self, frm: Account, to: Account, tokens: int):
        """ERC-20 transfer sends tokens from one account to another"""

        assert self.balances[frm.address] >= tokens, 'Insufficient tokens for transfer'

        self.balances[frm.address] -= tokens

        if to.address not in self.balances:
            self.balances[to.address] = 0

        self.balances[to.address] += tokens

    def __str__(self):
        return f'Token {self.name} ({self.address})'

    __repr__ = __str__


class TingesToken(ERC20Token):
    name = 'TNG'


class DAIStableCoin(ERC20Token):
    name = 'DAI'


class USDTStableCoin(ERC20Token):
    name = 'USDT'
