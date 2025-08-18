from dataclasses import dataclass

from taihe.semantics.attributes import (
    TypedAttribute,
)
from taihe.semantics.declarations import (
    TypeRefDecl,
)


@dataclass
class DtsTypeAttr(TypedAttribute[TypeRefDecl]):
    # TODO: Hack

    NAME = "dts_type"
    TARGETS = (TypeRefDecl,)

    type_name: str


all_napi_attr_types = [
    DtsTypeAttr,
]
