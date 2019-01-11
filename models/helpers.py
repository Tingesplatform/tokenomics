"""Helpful mixins and decorator"""
from typing import List


class InvalidStateError(Exception):
    pass


class StateDoesNotExists(Exception):
    pass


class StateMixin:
    state_list: List[str]
    current_state: str

    def set_state(self, state: str):
        assert state in self.state_list, StateDoesNotExists

        self.current_state = state


def require_state(states: List[str]):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if self.current_state in states:
                return func(self, *args, **kwargs)

            raise InvalidStateError

        return wrapper

    return decorator


def check_caller(caller_name: str):
    def wrapper(func):
        func.caller_name = caller_name
        return func

    return wrapper
