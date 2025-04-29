from typing import Any, Type, dataclass_transform

from .fields import get_fields


@dataclass_transform()
def __init_constructor__[T](cls: Type[T]) -> Type[T]:
    fields = get_fields(cls)

    locals_: dict[str, Any] = {}
    init_args: list[str] = ["self"]
    assignments: list[str] = []

    for field in fields:
        if field.name.startswith("__"):
            continue

        locals_[field.type_name] = field.type_
        locals_[field.default_name] = None

        init_args.append(field.init_arg)
        assignments.append(field.assginment)

    string_locals_ = ", ".join(locals_)
    string_init_args = ", ".join(init_args)
    string_assignments = "".join([f"\n\t\t{x}" for x in assignments])

    wrapper_fn = "\n".join(
        [
            f"def wrapper({string_locals_}):",
            f"\n\tdef __init__({string_init_args}):",
            string_assignments,
            "\treturn __init__",
        ]
    )

    namespace = {}

    exec(wrapper_fn, None, namespace)
    init_fn = namespace["wrapper"](**locals_)

    setattr(cls, "__init__", init_fn)
    return cls
