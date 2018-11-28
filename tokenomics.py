"""The tokenomics package for token economy modeling"""
import os
import sys
from enum import Enum
from datetime import datetime, timedelta


class Account:
    """Ethereum account"""
    def __init__(self, frm = None):
        if frm:
            self.owner = frm
        self.addr = "0x"+os.urandom(20).hex()

class Timer:
    def __init__(self, start = None):
        if start == None:
            self.time = datetime.now()
        else:
            self.time = start
    def increment(self, seconds):
        self.time += timedelta(seconds = seconds)


class ERC20Token(Account):
    """Basic ERC-20 token class with balances and totalSupply"""
    def __init__(self):
        super().__init__()
        self.balances = {}
        self.total_supply = 0

    def balance_of(self, holder: Account):
        """balanceOf ERC-20 method re-implementation"""
        if holder.addr in self.balances:
            return self.balances[holder.addr]
        else:
            return 0

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
    class State(Enum):
        CLOSED = 0
        PARTIAL = 1
        OPEN = 2
    def __init__(self, upstream = None, state = State.OPEN, rate = None, withdrawer = None, timer = None):
        super().__init__()
        self.upstream = upstream # upstream bucket
        self.state = state
        if rate != None:
            self.rate = rate
            self.state = self.State.PARTIAL
        else:
            self.rate = sys.maxsize
        self.withdrawer = withdrawer
        self.available = 0
        if type(timer) == Timer:
            self.timer = timer
            self.available_updated = self.timer.time

    def update(self):
        curtime = self.timer.time
        delta = curtime - self.available_updated
        self.available_updated = curtime
        delta_sec = delta.total_seconds()
        self.available += delta_sec * self.rate

    def get_available(self):
        self.update()
        return self.available

    def close(self):
        self.available = 0
        self.available_updated = self.timer.time
        self.state = self.State.CLOSED
        self.rate = 0

    def open(self):
        self.state = self.State.OPEN
        self.rate = sys.maxsize

    def set_rate(self, rate):
        self.update()
        self.state = self.State.PARTIAL
        self.rate = rate

    def withdraw(self, amount):
        if self.state == self.State.CLOSED:
            return False
        if self.state in [self.State.OPEN, self.State.PARTIAL]:
            if self.state == self.State.PARTIAL:
                self.update()
                if amount > self.available:
                    return False
                else:
                    self.available -= amount
            self.upstream.token.transfer(self.upstream, self.withdrawer, amount)
            return True

    def withdraw_all(self):
        self.update()
        amount = self.available
        self.withdraw(amount)
