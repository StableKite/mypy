"""Each selected overload must bind its own actual cls parameter."""
from typing import Generic, TypeVar, assert_type, overload

T = TypeVar('T')


class Restricted(Generic[T]):
    @overload
    def __new__(cls: 'type[Restricted[int]]', value: int) -> int: ...
    @overload
    def __new__(cls: 'type[Restricted[str]]', value: str) -> str: ...
    def __new__(cls, value: int | str) -> int | str:
        return value


assert_type(Restricted[int](1), int)
assert_type(Restricted[str]('one'), str)
Restricted[int]('wrong')  # genuine-negative: selected overload cannot bind cls
Restricted[str](2)  # genuine-negative: selected overload cannot bind cls
