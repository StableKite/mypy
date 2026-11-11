This review extends the existing ctypes errcheck contract with precise byref
owner types and the standard pickle reduction contract. Each vendored stub keeps
its original unrelated declarations and compatibility differences.

The read-only CArgObject owner is covariant and defaults to object. byref alone
preserves the concrete CData argument type; other converters can own bytes or
None. Existing Python-version-specific positional signatures are retained.

Pickle reductions can contain the documented sixth state-setter callable.
Only reducer_override additionally returns NotImplemented. The native hook's
known argument counts and invalid reduction forms remain checked.

MyPy also preserves a known NotImplementedType result when the return annotation
explicitly includes that type. Real Any results still warn. Legacy return
annotations, including existing operator behavior, retain their original rules.
No caller configuration, runtime implementation, or SDK is replaced by this work.
