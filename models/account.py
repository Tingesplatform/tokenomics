import os


class Account:
    ACCOUNTS_STORAGE = {}
    """Ethereum account"""
    def __init__(self):
        self.address = "0x" + os.urandom(20).hex()
        self.ACCOUNTS_STORAGE[self.address] = self

    def __str__(self):
        return f'Account {self.address}'

    __repr__ = __str__
