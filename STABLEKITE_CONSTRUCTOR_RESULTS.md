# Constructor results

Version: `2.4.1+stablekite.6`. Base: accepted StableKite 5,
`7991846dd80c443bfcbf719f3b53c96d6e2b7f45`.

The normative reference is the
[typing constructor specification](https://typing.python.org/en/latest/spec/constructors.html).

An ordinary `__new__` can return an unrelated object, a union, a TypeVar,
a protocol-typed object, `None`, a callable or a literal. Its declared return
type is checked against the actual body. It need not be a subtype of its
defining class. The existing separate metaclass class-creation check remains.

The constructor uses an explicit result that differs from the usual class
instance. After overload selection and type argument inference, a related
result invokes the applicable non-object `__init__`; an unrelated result, or
a union containing an unrelated member, skips that stage. The relationship
uses nominal inheritance rather than structural protocol assignability.
Explicit `Any` and `Never` follow the specification.

The actual constructor result also determines whether a call allocates an
abstract class. A factory facade that returns a genuine concrete resource
does not allocate its abstract facade. A real abstract allocation remains an
error. Custom metaclass `__call__` results participate before `__new__`.

The implicit `cls` argument is checked against the selected `__new__`
overload, including after loading its defining module from the normal cache.
A class whose constructor returns `Never` retains its identity and class
attributes as a class object.

The six added strict CLI tests use the real standard library, including
ordinary and related constructors, actual bad arguments and return bodies,
TypeVar bounds, `cls` binding, overloads, abstract allocations and metaclasses.
The positive programs are also executable on stock CPython 3.13 and 3.15 on
Windows and Linux; stock free-threaded 3.15 keeps its natural GIL state.
The mixed-union program explicitly proves that its related runtime branch
still calls `__init__`.

Nine obsolete expected diagnostic comments in eight old cases were changed.
All actual Python bytes preceding those comments and all other old lines,
reveals, options and fixtures are unchanged. A separate per-line ledger
records the old and new comments, the exact specification clause, and the
corresponding executable control. The old fixture bodies containing `pass`
are not claimed to execute their annotated return value.

One redundant empty EOF line was removed only from the new primary positive
fixture with explicit authorization. A separate ledger preserves its old and
new SHA256 and confirms identical complete ASTs, including source coordinates.
Every other byte of that input and every other new input is unchanged.

Local validation: 8,293 checks pass (8,287 previous plus six added), with the
previous 35 skips and seven expected failures unchanged. Original source,
mypyc, plugin, miscellaneous and runtime self-checks, pinned Black/Ruff and
the previous genuine HID and pickle contracts pass. Distribution and CI
qualification are recorded separately; this document does not claim them.
