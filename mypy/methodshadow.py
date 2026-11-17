"""Separate instance callable contracts from the real class function symbol."""

from __future__ import annotations

from mypy.nodes import VARIANCE_NOT_READY, Decorator, FuncDef, TypeInfo
from mypy.types import CallableType, FunctionLike, Instance, Type, TypeVarType, get_proper_type


def ordinary_method(info: TypeInfo, name: str) -> FuncDef | None:
    symbol = info.get(name)
    if symbol is None:
        return None
    if isinstance(symbol.node, FuncDef):
        method = symbol.node
    elif isinstance(symbol.node, Decorator) and not symbol.node.decorators:
        method = symbol.node.func
    else:
        return None
    if method.is_class or method.is_static or method.is_property:
        return None
    return method


def own_contracts(info: TypeInfo, name: str) -> list[Type]:
    if not info.method_shadow_types:
        return []
    result = []
    for key, typ in sorted(info.live_method_shadow_types().items()):
        _, separator, attribute = key.partition(".")
        if separator and attribute == name:
            result.append(typ)
    return result


def raw_contract(info: TypeInfo, name: str) -> tuple[TypeInfo, Type] | None:
    for base in info.mro:
        contracts = own_contracts(base, name)
        if contracts:
            if ordinary_method(info, name) is None:
                return None
            return base, contracts[0]
    return None


def reset_inferred_variance(info: TypeInfo) -> None:
    if info.defn.type_args:
        for variable in info.defn.type_vars:
            if isinstance(variable, TypeVarType):
                variable.variance = VARIANCE_NOT_READY


def reset_owner(info: TypeInfo, owner: str) -> None:
    prefix = owner + "."
    live = info.live_method_shadow_types()
    pruned = live.keys() != info.method_shadow_types.keys()
    info.method_shadow_types = live
    old = [key for key in live if key.startswith(prefix)]
    for key in old:
        del info.method_shadow_types[key]
    if old or pruned:
        reset_inferred_variance(info)


def can_record_contract(info: TypeInfo, name: str, typ: Type) -> bool:
    method = ordinary_method(info, name)
    annotation = get_proper_type(typ)
    if (
        method is None
        or method.is_final
        or info.is_metaclass()
        or not supports_instance_write(info)
    ):
        return False
    if contains_self(typ):
        return False
    if not isinstance(annotation, CallableType) and not (
        isinstance(annotation, Instance)
        and annotation.type.is_protocol
        and annotation.type.protocol_members == ["__call__"]
    ):
        return False
    return True


def record_contract(info: TypeInfo, owner: str, name: str, typ: Type) -> None:
    if not can_record_contract(info, name, typ):
        return
    info.method_shadow_types[owner + "." + name] = typ
    reset_inferred_variance(info)


def concrete_callable(typ: Type) -> bool:
    # Import lazily: checkexpr itself uses member-access and subtype machinery.
    from mypy.checkexpr import has_any_type

    proper = get_proper_type(typ)
    return (
        isinstance(proper, FunctionLike)
        and not any(item.is_ellipsis_args for item in proper.items)
        and not has_any_type(typ)
    )


def contains_self(typ: Type) -> bool:
    from mypy.typeops import get_all_type_vars

    return any(variable.id.is_self() for variable in get_all_type_vars(typ))


def supports_instance_write(info: TypeInfo) -> bool:
    if info.slots is not None and "__dict__" not in info.slots:
        return False
    if info.is_named_tuple:
        return False
    for namespace in ("dataclass", "attrs"):
        metadata = info.metadata.get(namespace)
        if isinstance(metadata, dict) and metadata.get("frozen") is True:
            return False
    return True


def writable_method(info: TypeInfo, name: str) -> bool:
    method = ordinary_method(info, name)
    if (
        method is None
        or method.is_final
        or method.type is None
        or not supports_instance_write(info)
        or raw_contract(info, name) is None
    ):
        return False
    return concrete_callable(method.type) and not contains_self(method.type)
