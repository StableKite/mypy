"""Real CPython constructor controls; no Root or dependency substitutions."""
from abc import ABC, abstractmethod
from typing import assert_type


class NumberFactory:
    def __new__(cls, value: str) -> int:
        return int(value)

    def __init__(self, required_bytes: bytes) -> None:
        raise AssertionError("CPython must skip unrelated __init__")


class Resource:
    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False

    def close(self) -> None:
        self.closed = True


class AbstractFactory(ABC):
    def __new__(cls, name: str) -> Resource:
        return Resource(name)

    @abstractmethod
    def close(self) -> None:
        ...


class Standard:
    def __init__(self, value: int) -> None:
        self.value = value


number = NumberFactory("12")
assert_type(number, int)
assert type(number) is int and number == 12
resource = AbstractFactory("owned-language-control")
assert_type(resource, Resource)
assert type(resource) is Resource and resource.name == "owned-language-control"
resource.close()
assert resource.closed
assert Standard(7).value == 7
