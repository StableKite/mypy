"""Actual bad calls and bodies; each marked line must receive a semantic error."""
from abc import ABC, abstractmethod
from typing import Generic, Self, TypeVar, overload

T = TypeVar('T')
BoundInt = TypeVar('BoundInt', bound=int)


class IdentityFactory:
    def __new__(cls, value: T) -> T:
        return value

    def __init__(self, value: bytes) -> None:
        self.value = value


existing_identity = object.__new__(IdentityFactory)
IdentityFactory(existing_identity)  # genuine-negative: related generic result still calls init


class Restricted(Generic[T]):
    def __new__(cls: 'type[Restricted[int]]') -> 'Restricted[int]':
        return object.__new__(cls)


Restricted[str]()  # genuine-negative: invalid cls binding


class BoundedFactory:
    def __new__(cls, value: BoundInt) -> BoundInt:
        return value


BoundedFactory('wrong')  # genuine-negative: TypeVar bound


class RelatedFactory:
    def __new__(cls, value: int) -> Self:
        return object.__new__(cls)

    def __init__(self, value: int) -> None:
        self.value = value


RelatedFactory('wrong')  # genuine-negative: related Self argument


class RealAbstract(ABC):
    @abstractmethod
    def close(self) -> None: ...


RealAbstract()  # genuine-negative: genuine abstract allocation


class WrongBodyFactory:
    def __new__(cls) -> int:
        return 'wrong'  # genuine-negative: actual bad return body


class OverloadedFactory:
    @overload
    def __new__(cls, value: str) -> str: ...
    @overload
    def __new__(cls, value: int) -> Self: ...
    def __new__(cls, value: int | str) -> 'OverloadedFactory | str':
        return value if isinstance(value, str) else object.__new__(cls)

    def __init__(self, value: bytes) -> None:
        self.value = value


OverloadedFactory(1)  # genuine-negative: selected Self overload must validate init


class RealMeta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, object]) -> type:
        return type.__new__(mcls, 7, bases, namespace)  # genuine-negative: metaclass class creation argument


class CreatedByMeta(metaclass=RealMeta):
    pass
