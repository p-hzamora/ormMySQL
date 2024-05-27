import inspect
import dis
from typing import Iterator


class GestAssignedName():
    @staticmethod
    def take1(iterator):
        try:
            return next(iterator)
        except StopIteration:
            raise Exception("missing bytecode instruction") from None


    def take(self, iterator, count):
        for x in range(count):
            yield self.take1(iterator)


    def get(self, frame):
        """Takes a frame and returns a description of the name(s) to which the
        currently executing CALL_FUNCTION instruction's value will be assigned.

        fn()                    => None
        a = fn()                => "a"
        a, b = fn()             => ("a", "b")
        a.a2.a3, b, c* = fn()   => ("a.a2.a3", "b", Ellipsis)
        """

        iterator = iter(dis.get_instructions(frame.f_code))
        for instr in iterator:
            if instr.offset == frame.f_lasti:
                break
        else:
            assert False, "bytecode instruction missing"
        assert instr.opname.startswith("CALL")
        instr = self.take1(iterator)
        if instr.opname == "POP_TOP":
            raise ValueError("not assigned to variable")
        return self.instr_dispatch(instr, iterator)


    def instr_dispatch(self, instr:dis.Instruction, iterator:Iterator):
        opname = instr.opname
        if (
            opname == "STORE_FAST"  # (co_varnames)
            or opname == "STORE_GLOBAL"  # (co_names)
            or opname == "STORE_NAME"  # (co_names)
            or opname == "STORE_DEREF"
        ):  # (co_cellvars++co_freevars)
            return instr.argval
        if opname == "UNPACK_SEQUENCE":
            return tuple(self.instr_dispatch(instr, iterator) for instr in self.take(iterator, instr.arg))
        if opname == "UNPACK_EX":
            return (*tuple(self.instr_dispatch(instr, iterator) for instr in self.take(iterator, instr.arg)), Ellipsis)
        # Note: 'STORE_SUBSCR' and 'STORE_ATTR' should not be possible here.
        # `lhs = rhs` in Python will evaluate `lhs` after `rhs`.
        # Thus `x.attr = rhs` will first evalute `rhs` then load `a` and finally
        # `STORE_ATTR` with `attr` as instruction argument. `a` can be any
        # complex expression, so full support for understanding what a
        # `STORE_ATTR` will target requires decoding the full range of expression-
        # related bytecode instructions. Even figuring out which `STORE_ATTR`
        # will use our return value requires non-trivial understanding of all
        # expression-related bytecode instructions.
        # Thus we limit ourselfs to loading a simply variable (of any kind)
        # and a arbitary number of LOAD_ATTR calls before the final STORE_ATTR.
        # We will represents simply a string like `my_var.loaded.loaded.assigned`
        if opname in {"LOAD_CONST", "LOAD_DEREF", "LOAD_FAST", "LOAD_GLOBAL", "LOAD_NAME"}:
            return instr.argval + "." + ".".join(self.instr_dispatch_for_load(instr, iterator))
        raise NotImplementedError("assignment could not be parsed: " "instruction {} not understood".format(instr))


    def instr_dispatch_for_load(self, instr, iterator):
        instr = self.take1(iterator)
        opname = instr.opname
        if opname == "LOAD_ATTR":
            yield instr.argval
            yield from self.instr_dispatch_for_load(instr, iterator)
        elif opname == "STORE_ATTR":
            yield instr.argval
        else:
            raise NotImplementedError("assignment could not be parsed: " "instruction {} not understood".format(instr))


class Column[T]:
    __slots__ = (
        "column_name",
        "column_value",
        "is_primary_key",
        "is_auto_generated",
        "is_auto_increment",
        "is_unique",
    )

    def __init__(
        self,
        *,
        is_primary_key: bool = False,
        is_auto_generated: bool = False,
        is_auto_increment: bool = False,
        is_unique: bool = False,
    ) -> None:
        self.column_name = GestAssignedName.get(inspect.currentframe().f_back)
        self.column_value: T = None
        self.is_primary_key: bool = is_primary_key
        self.is_auto_generated: bool = is_auto_generated
        self.is_auto_increment: bool = is_auto_increment
        self.is_unique: bool = is_unique

    def __repr__(self) -> str:
        return f"<Column: {self.column_name}>"
