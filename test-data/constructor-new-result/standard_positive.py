"""Executable constructor contracts from the typing specification."""
from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Callable
from typing import Any, Generic, Literal, Never, Protocol, Self, TypeVar, assert_type, overload

T = TypeVar('T')
events: list[str] = []


class GenericFactory(Generic[T]):
    def __new__(cls, value: T) -> list[T]:
        return [value]

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('unrelated init')


assert_type(GenericFactory(7), list[int])
assert GenericFactory[str]('seven') == ['seven']


class IdentityFactory:
    def __new__(cls, value: T) -> T:
        return value

    def __init__(self, value: bytes) -> None:
        events.append('identity-init')


assert_type(IdentityFactory(8), int)
assert IdentityFactory(b'eight') == b'eight'


class MixedFactory:
    def __new__(cls, flag: bool) -> 'MixedFactory | int':
        return object.__new__(cls) if flag else 9

    def __init__(self, flag: bytes) -> None:
        events.append('mixed-init')


assert_type(MixedFactory(False), MixedFactory | int)
assert MixedFactory(False) == 9
assert type(MixedFactory(True)) is MixedFactory
assert events == ['mixed-init']


class OptionalFactory:
    def __new__(cls, value: str) -> int | None:
        return int(value) if value else None

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('optional init')


assert_type(OptionalFactory('10'), int | None)
assert OptionalFactory('') is None


class NoneFactory:
    def __new__(cls) -> None:
        return None

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('none init')


assert_type(NoneFactory(), None)


class CallableFactory:
    def __new__(cls) -> Callable[[int], str]:
        return str

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('callable init')


assert_type(CallableFactory(), Callable[[int], str])
assert CallableFactory()(11) == '11'


class Closeable(Protocol):
    def close(self) -> None: ...


class Resource:
    def __init__(self, name: str) -> None:
        self.name = name

    def close(self) -> None:
        events.append(self.name)


class ProtocolFactory:
    def __new__(cls) -> Closeable:
        return Resource('protocol-close')

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('protocol init')

    def close(self) -> None:
        raise AssertionError('structural similarity is not nominal allocation')


assert_type(ProtocolFactory(), Closeable)
ProtocolFactory().close()
assert events[-1] == 'protocol-close'


class Parent:
    def __init__(self, value: int) -> None:
        self.value = value


class ChildFactory(Parent):
    def __new__(cls, value: str) -> Parent:
        return Parent(int(value))

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('superclass result skips child init')


assert_type(ChildFactory('12'), Parent)
assert type(ChildFactory('12')) is Parent


class BaseFactory:
    def __new__(cls, value: int) -> 'Product':
        return object.__new__(Product)

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('returned subclass selects subclass init')


class Product(BaseFactory):
    def __init__(self, value: int) -> None:
        self.value = value


assert_type(BaseFactory(13), Product)
assert BaseFactory(13).value == 13


class RelatedFactory:
    def __new__(cls, value: int) -> Self:
        return object.__new__(cls)

    def __init__(self, value: int) -> None:
        self.value = value


assert_type(RelatedFactory(14), RelatedFactory)
assert RelatedFactory(14).value == 14


class OverloadedFactory:
    @overload
    def __new__(cls, value: int) -> int: ...
    @overload
    def __new__(cls, value: str) -> Self: ...
    def __new__(cls, value: int | str) -> 'OverloadedFactory | int':
        return value if isinstance(value, int) else object.__new__(cls)

    def __init__(self, value: str) -> None:
        self.value = value


assert_type(OverloadedFactory(15), int)
assert_type(OverloadedFactory('fifteen'), OverloadedFactory)
assert OverloadedFactory('fifteen').value == 'fifteen'


class FactoryMeta(ABCMeta):
    def __call__(cls, name: str) -> Resource:
        return Resource(name)


class MetaFacade(ABC, metaclass=FactoryMeta):
    @abstractmethod
    def close(self) -> None: ...


assert_type(MetaFacade('meta-resource'), Resource)
assert type(MetaFacade('meta-resource')) is Resource


def invoke(factory: Callable[[str], Parent]) -> Parent:
    return factory('16')


assert invoke(ChildFactory).value == 16


class LiteralFactory:
    def __new__(cls) -> Literal[1]:
        return 1


assert_type(LiteralFactory(), Literal[1])
assert type(LiteralFactory()) is int

BoundSelf = TypeVar('BoundSelf', bound='BoundIdentity')


class BoundIdentity:
    def __new__(cls, value: BoundSelf) -> BoundSelf:
        return value

    def __init__(self, value: 'BoundIdentity') -> None:
        events.append('bound-identity-init')


existing_bound = object.__new__(BoundIdentity)
assert_type(BoundIdentity(existing_bound), BoundIdentity)
assert BoundIdentity(existing_bound) is existing_bound
assert events[-1] == 'bound-identity-init'


class AnyFactory:
    def __new__(cls) -> Any:
        return 17

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('explicit Any follows the constructor specification')


assert_type(AnyFactory(), Any)
assert type(AnyFactory()) is int


class AnyUnionFactory:
    def __new__(cls) -> 'Self | Any':
        return 18

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('an explicit Any union skips init checking')


assert_type(AnyUnionFactory(), AnyUnionFactory | Any)
assert type(AnyUnionFactory()) is int


class NeverFactory:
    def __new__(cls, value: int) -> Never:
        raise LookupError(value)

    def __init__(self, unused: bytes) -> None:
        raise AssertionError('a non-returning new never reaches init')


def exercise_never() -> None:
    try:
        NeverFactory(19)
    except LookupError:
        events.append('never-new-raised')


exercise_never()
assert events[-1] == 'never-new-raised'
