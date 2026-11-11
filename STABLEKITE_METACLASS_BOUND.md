# Class-object bounds in metaclass methods

Version 2.4.1+stablekite.3 preserves the preceding StableKite ctypes, HID,
pickle, and precise-sentinel changes and adds nominal metaclass owner checks.

An explicit self parameter type[A] is accepted inside a metaclass M when
A's known metaclass MRO contains M. A class bound alone does not guarantee an
unrelated custom metaclass. This does not change the assignability of every M
instance to type[A]; call sites still check the declared self argument.

For super() on such a class object, lookup follows the known metaclass MRO
while retaining the actual class object and its type variables for binding.
The ordinary class MRO takes precedence when it already contains the owner.
Enum indexing with an overridden metaclass getter checks that actual getter,
including its self bound, rather than skipping it through enum handling.

The real case-insensitive EnumMeta method can therefore keep its implementation
returning super().__getitem__(key.upper()), with Member bounded to the actual
CaseInsensitiveEnum base. Its return remains the concrete enum subclass.
Member bounded only to Enum does not guarantee the custom owner and remains
rejected. No producer body changes, Any escape, cast, ignore, or rule change
are required.

Three expected definition diagnostics in
testMetaclassStrictSupertypeOfTypeWithClassmethods are obsolete for this new
capability: A is explicitly declared with metaclass M. Only those three
comments change. The existing precise reveal_type assertions and all invalid
calls and assignments remain, including B.g1/g2/g3 and M instances used as
type[A], type[Class], type[Static], and type[Cvar].

New tests cover exact return types, inherited metaclasses, zero-argument and
explicit super, an incompatible owner, an enum outside the narrower bound,
and wrong key and return types. Existing fixture files are unchanged; a new
strict enum fixture supplies the genuine object.__init__ return annotation.
