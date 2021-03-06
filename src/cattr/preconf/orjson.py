"""Preconfigured converters for orjson."""
from base64 import b85decode, b85encode
from datetime import datetime
from typing import Any

from .._compat import Set, is_mapping
from ..converters import GenConverter


def configure_converter(converter: GenConverter):
    """
    Configure the converter for use with the orjson library.

    * bytes are serialized as base85 strings
    * datetimes are serialized as ISO 8601
    * sets are serialized as lists
    * mapping keys are coerced into strings when unstructuring
    """
    converter.register_unstructure_hook(
        bytes, lambda v: (b85encode(v) if v else b"").decode("utf8")
    )
    converter.register_structure_hook(bytes, lambda v, _: b85decode(v))

    converter.register_unstructure_hook(datetime, lambda v: v.isoformat())
    converter.register_structure_hook(
        datetime, lambda v, _: datetime.fromisoformat(v)
    )

    def gen_unstructure_mapping(cl: Any, unstructure_to=None):
        return converter.gen_unstructure_mapping(
            cl, unstructure_to=unstructure_to, key_handler=str
        )

    converter._unstructure_func.register_func_list(
        [(is_mapping, gen_unstructure_mapping, True)]
    )


def make_converter(*args, **kwargs) -> GenConverter:
    kwargs["unstruct_collection_overrides"] = {
        **kwargs.get("unstruct_collection_overrides", {}),
        Set: list,
    }
    res = GenConverter(*args, **kwargs)
    configure_converter(res)

    return res
