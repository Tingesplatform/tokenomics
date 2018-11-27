"""The tokenomics package for token economy modeling"""

class Account:
    """Ethereum account"""
    def __init__(self, addr: str):
        self.addr = addr


class ERC20Token:
    """Basic ERC-20 token class with balances and totalSupply"""
    def __init__(self):
        self.balances = {}
        self.total_supply = 0

    def balance_of(self, holder: Account):
        """balanceOf ERC-20 method re-implementation"""
        return self.balances[holder.addr]

    def mint(self, to: Account, tokens):
        """mints (creates new amount of) tokens for the given account"""
        if to.addr not in self.balances:
            self.balances[to.addr] = 0
        self.balances[to.addr] += tokens
        self.total_supply += tokens

    def transfer(self, frm: Account, to: Account, tokens):
        """ERC-20 transfer sends tokens from one account to another"""
        assert self.balances[frm.addr] >= tokens
        self.balances[frm.addr] -= tokens
        if to.addr not in self.balances:
            self.balances[to.addr] = 0
        self.balances[to.addr] += tokens
