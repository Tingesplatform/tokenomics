"""The tokenomics package for token economy modeling"""
import os


class Account:
    """Ethereum account"""
    def __init__(self, frm = None):
        if frm:
            self.owner = frm
        self.addr = "0x"+os.urandom(20).hex()


class ERC20Token(Account):
    """Basic ERC-20 token class with balances and totalSupply"""
    def __init__(self):
        super().__init__()
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

class Bucket(Account):
    """The container of predefined volume storing raised funds"""
    def __init__(self, token=None, max_volume = 1000, overflow_bkt = None):
        super().__init__()
        self.max_volume = max_volume
        self.token = token
        self.taps = [] # egress taps authorized to withdraw
        self.overflow_bkt = overflow_bkt

    def flush(self):
        token_balance = self.token.balance_of(self)
        if token_balance > self.max_volume:
            self.token.transfer(self, self.overflow_bkt, token_balance - self.max_volume)

    def set_overflow_bucket(self, overflow_bkt):
        self.overflow_bkt = overflow_bkt

    def add_tap(self, tap_addr):
        pass

    def del_tap(self, tap_addr):
        pass


class Tap(Account):
    def __init__(self, upstream = None):
        super().__init__()
        self.upstream = upstream # upstream bucket

    def close(self):
        pass

    def open(self):
        pass

    def set_rate(self, rate):
        pass

    def withdraw(self, amount):
        pass

    def withdraw_all(self):
        pass
