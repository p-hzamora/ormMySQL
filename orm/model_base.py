# region imports
from abc import ABC
from collections import defaultdict
from typing import Any, Callable, Literal, Self, overload
import dis
from queue import Queue

from orm.interfaces import IRepositoryBase
from app.extesions.repository.orm.table.column import Column
from orm.table.table import Table
# endregion

CONDITIONS = Literal["=", "<", ">", "<=", ">=", "REGEXP"]


class ModelBase[T:Table](ABC):
    """
    Clase base de las clases Model.

    Contiene los metodos necesarios para hacer consultas a una tabla
    """

    # region Constructor
    def __init__(self, model: T, *, repository: IRepositoryBase):
        self._model: T = model
        if not issubclass(self._model, Table):
            # Deben heredar de Table ya que es la forma que tenemos para identificar si estamos pasando una instancia del tipo que corresponde o no cuando llamamos a insert o upsert.
            # Si no heredase de Table no sabriamos identificar el tipo de dato del que se trata porque al llamar a isinstance, obtendriamos el nombre de la clase que mapea a la tabla, Encargo, Edificio, Presupuesto y no podriamos crear una clase generica

            raise Exception(f"La clase '{model}' no hereda de Table")

        if model.__table_name__ is Ellipsis:
            raise Exception(
                f"Se debe declarar la variabnle '__table_name__' en la clase '{model.__name__}'"
            )

        self._repository = repository
        self._conditions: defaultdict[Queue] = defaultdict(lambda: Queue())

    # endregion

    # region Private methods
    def __repr__(self):
        return f"<Model: {self.__class__.__name__}>"

    def __add_condition[TValue](
        self,
        col: Callable[[T], None | bool],
        value: TValue,
        condition: CONDITIONS,
        _restriction: str,
    ) -> Self:
        attr = {x.opname: x.argval for x in dis.Bytecode(col)}

        if value is None:
            attr["COMPARE_OP"] = (
                "=" if attr["COMPARE_OP"] == "==" else attr["COMPARE_OP"]
            )
            self._conditions[_restriction].put(
                f"{attr["LOAD_ATTR"]} {attr["COMPARE_OP"]} '{attr["LOAD_CONST"]}'"
            )
            return self

        # if isinstance(value, list):
        #     self._conditions[_restriction].put(f"{attr["LOAD_ATTR"]} {condition} '{value}'")

        self._conditions[_restriction].put(f"{attr["LOAD_ATTR"]} {condition} '{value}'")
        return self

    # endregion

    # region Public methods
    # region insert
    @overload
    def insert(self, values: T) -> None:
        """
        PARAMS
        ------
        - values: Recibe un unico objeto que ha de coincidir con el valor del modelo
        """
        ...

    @overload
    def insert(self, values: list[T]) -> None:
        """
        PARAMS
        ------
        - values: Recibe una lista del mismo objeto que el modelo
        """
        ...

    def insert(self, values: T | list[T]) -> None:
        """
        Inserta valores en la bbdd parseando los datos a diccionarios
        """

        def is_valid(column: Column) -> bool:
            """
            Validamos si la columna la debemos eliminar o no a la hora de insertar o actualizar valores.

            Querremos elimina un valor de nuestro objeto cuando especifiquemos un valor que en la bbdd sea AUTO_INCREMENT o AUTO GENERATED ALWAYS AS (__) STORED.

            RETURN
            -----

            - True  -> No eliminamos la columna de la consulta
            - False -> Eliminamos la columna
            """
            # en el caso de tener un valor
            cond_2 = (
                column.auto_increment
                and column.column_value is None
                and column.primary_key
            )

            if column.auto_generated or cond_2:
                return False
            return True

        def create_dict_list(values: T | list[T]):
            """
            Utilizamos lista como nonlocal para poder utilizar esta funcion de forma reciproca
            """
            nonlocal lista

            if issubclass(values.__class__, Table):
                dicc: dict = {}
                for col in values.__dict__.values():
                    if isinstance(col, Column) and is_valid(col):
                        dicc.update({col.column_name: col.column_value})
                lista.append(dicc)

            elif isinstance(values, list):
                for x in values:
                    create_dict_list(x)
            else:
                raise Exception(f"Tipo de dato'{type(values)}' no esperado")

        lista: list = []
        create_dict_list(values)

        self._repository.insert(self._model.__table_name__, lista)
        return None

    # endregion

    # region upsert
    @overload
    def upsert(self, values: T) -> None:
        """
        PARAMS
        ------
        - values: Recibe un unico objeto que ha de coincidir con el valor del modelo
        """
        ...

    @overload
    def upsert(self, values: list[T]) -> None:
        """
        PARAMS
        ------
        - values: Recibe una lista del mismo objeto que el modelo
        """
        ...

    def upsert(self, values: list[T]) -> None:
        """
        Actualizar valores ya existentes en la bbdd parseando los datos a diccionarios. En caso de que existan, los inserta
        """

        def is_valid(column: Column) -> bool:
            """
            Eliminamos aquellas columnas autogeneradas y dejamos aquellas columnas unicas para que la consulta falle y realice un upsert

            Aunque una pk sea autogenerada debemos eliminarla de la query ya que no podemos pasar un valor a una columna la cual no acepta valores nuevos.
            Cuando se genere dicha columna y la base de datos detecte que el valor generado está repetido, será entonces cuando detecte la duplicidad y realice ON DUPLICATE KEY UPDATE

            RETURN
            -----

            - True  -> No eliminamos la columna de la consulta
            - False -> Eliminamos la columna
            """
            if (
                column.auto_increment and not column.primary_key
            ) or column.auto_generated:
                return False
            return True

        def create_dict_list(values: T | list[T]):
            """
            Utilizamos lista como nonlocal para poder utilizar esta funcion de forma reciproca
            """
            nonlocal lista

            if issubclass(values.__class__, Table):
                dicc: dict = {}
                for col in values.__dict__.values():
                    if isinstance(col, Column) and is_valid(col):
                        dicc.update({col.column_name: col.column_value})
                lista.append(dicc)

            elif isinstance(values, list):
                for x in values:
                    create_dict_list(x)
            else:
                raise Exception(f"Tipo de dato'{type(values)}' no esperado")

        lista: list = []
        create_dict_list(values)
        self._repository.upsert(self._model.__table_name__, lista)
        return None

    # endregion

    # region all
    @overload
    def all(self) -> list[T]:
        ...

    @overload
    def all[TValue](self, flavour: TValue) -> TValue:
        ...

    def all[TValue](self, flavour: TValue = None) -> list[T] | TValue:
        if flavour is None:
            query_res = self._repository.read_sql(
                f"SELECT * FROM {self._model.__table_name__}", flavour=dict
            )
            return [self._model(**x) for x in query_res]

        return self._repository.read_sql(
            f"SELECT * FROM {self._model.__table_name__}", flavour=flavour
        )

    # endregion

    # region get
    @overload
    def get[TValue](
        self, col: Callable[[T], None], flavour: TValue
    ) -> TValue | list[TValue] | None:
        ...

    @overload
    def get(self, col: Callable[[T], None]) -> list[T] | None:
        """
        PARAMS
        ------

        col: Callable[[T],None] -> lambda function to specify col name
        """
        ...

    @overload
    def get(self, col: list[Callable[[T], None]]) -> list[T] | None:
        """
        PARAMS
        ------

        col: list[Callable[[T],None]] -> list of lambda functions to specify a group of retrieves names

        """
        ...

    @overload
    def get[TValue](
        self, col: list[Callable[[T], None]], flavour: TValue
    ) -> list[TValue] | None:
        """
        PARAMS
        ------

        col: list[Callable[[T],None]]   -> list of lambda functions to specify a group of retrieves names
        flavour: TValue                 -> object to return like pd.DataFrame, list, tuple, dict
        """
        ...

    @overload
    def get(self) -> list[T] | None:
        """
        You must call this function when you have used filter_by or group_by. Otherwise you'll raise an Exception error
        """
        ...

    @overload
    def get[TValue](self, flavour: TValue) -> TValue | list[TValue] | None:
        """
        PARAMS
        ------

        flavour:TValue  -> object type returned

        RETURN
        -----

        TValue or list[TValue]
        if you specify pd.DataFrame as flavour, you will get a pd.DataFrame. Otherwise you will retrieve list of TValue
        """
        ...

    def get(
        self,
        col: str | list[Callable[[T], None]] | Callable[[T], None] = None,
        *,
        flavour: Any = None,
    ) -> T | list[T] | None:
        if (iconditions := len(self._conditions)) == 0:
            raise Exception(
                "You cannot call the 'get()' method without calling 'filter_by()' or 'group_by()' before.\nIf you want to retrieve all table objects, you must use 'all()'"
            )

        is_col_method: bool = False
        if isinstance(col, list):
            col = ", ".join(
                [
                    {x.opname: x.argval for x in dis.Bytecode(i)}["LOAD_ATTR"]
                    for i in col
                ]
            )

        elif callable(col):
            is_col_method = True
            col = {x.opname: x.argval for x in dis.Bytecode(col)}["LOAD_ATTR"]

        query_res: str = (
            f"SELECT {col if col else '*'} FROM {self._model.__table_name__}"
        )

        # region recorre las queue creando la query
        conditions = []
        _tuple = tuple(
            self._conditions.items()
        )  # ej, ((" AND ",<Queue() object>),(" OR ",<Queue() object>))
        for i in range(1, iconditions + 1):
            str_cond: str = _tuple[i - 1][0]
            value_cond: Queue = _tuple[i - 1][1]

            # concateno todos los valores de la cola y los agrupo dentro de parentesis (<conditions>)
            condition = str_cond.join(
                [value_cond.get() for _ in range(value_cond.qsize())]
            )
            conditions.append(f"({condition})")
            # forma dinamica para agregar a la lista el tipo de condicion con el grupo siguiente
            #
            if i != iconditions:
                # agrega solo el tipo de condicion que corresponda "AND", "OR", etc...
                conditions.append(_tuple[i - 1][0])

        query_res = f"{query_res} WHERE {"".join(conditions)}"
        self._conditions = defaultdict(lambda: Queue())
        # endregion

        if is_col_method:
            # if 'is_col_method' True means that you are trying to return one column so to avoid list[tuple[Any]] we iterate through res var to get tuple[Any]

            res = self._repository.read_sql(
                query_res, flavour=flavour if flavour else tuple
            )
            if isinstance(res[0], tuple):
                res = tuple([x[0] for x in res[::]]) if res else None
            return res

        if flavour:
            return self._repository.read_sql(query_res, flavour=flavour)

        res = self._repository.read_sql(query_res, flavour=dict)
        res = [self._model(**x) for x in res]
        return res if len(res) != 0 else None

    # endregion

    # region first
    @overload
    def first[TValue](
        self, col: Callable[[T], None], flavour: TValue
    ) -> TValue | list[TValue] | None:
        ...

    @overload
    def first(self, col: Callable[[T], None]) -> list[T] | None:
        """
        PARAMS
        ------

        col: Callable[[T],None] -> lambda function to specify col name
        """
        ...

    @overload
    def first(self, col: list[Callable[[T], None]]) -> list[T] | None:
        """
        PARAMS
        ------

        col: list[Callable[[T],None]] -> list of lambda functions to specify a group of retrieves names

        """
        ...

    @overload
    def first(self) -> T | None:
        """
        You must call this function when you have used filter_by or group_by. Otherwise you'll raise an Exception error
        """
        ...

    @overload
    def first[TValue](self, flavour: TValue) -> TValue | list[TValue] | None:
        """
        PARAMS
        ------

        flavour:TValue  -> object type returned

        RETURN
        -----

        TValue or list[TValue]
        if you specify pd.DataFrame as flavour, you will get a pd.DataFrame. Otherwise you will retrieve list of TValue
        """
        ...

    def first(
        self,
        col: str | list[Callable[[T], None]] | Callable[[T], None] = None,
        *,
        flavour: Any = None,
    ) -> T:
        res = self.get(col=col, flavour=flavour)
        return res[0] if res else None

    # endregion

    # region filter_by
    @overload
    def filter_by(self, col: Callable[[T], bool]) -> Self:
        """
        Specifies match filter by adding 'AND' to the query

        EXAMPLE
        -

        >>> filter_by(lambda x: x.nombre == "Pablo").get()

        ERROR
        -----

        >>> filter_by(lambda x: x.nombre == cond).get()
        >>> you will get -> x.nombre == "cond"  instead of x.nombre == "Pablo"
        """
        ...

    @overload
    def filter_by(self, col: Callable[[T], None], value: int | float | str) -> Self:
        """
        Specifies match filter by adding 'AND' to the query

        EXAMPLE
        -

        >>> cond = "Pablo"
        >>> filter_by(lambda x: x.nombre == cond).get() # RAISE ERROR
        >>> filter_by(lambda x: x.nombre, value= cond).filter_by(lambda x: x.uuid).get()

        lambda function cannot get the value of a variable like cond, that is the reason to create two alternatives

        ERROR
        -----

        >>> cond = "Pablo"
        >>> filter_by(lambda x: x.nombre == cond).get()
        >>> you will get -> x.nombre == "cond"  instead of x.nombre == "Pablo"
        """
        ...

    @overload
    def filter_by(
        self, col: Callable[[T], None], value: int | float | str, condition: CONDITIONS
    ) -> Self:
        """
        Specifies "REGEXP" in "condition" arg to makes regular expression match
        """
        ...

    def filter_by(
        self,
        col: Callable[[T], None],
        value: int | float | str = None,
        condition: CONDITIONS = "=",
    ) -> Self:
        self.__add_condition(col, value, condition, " AND ")
        return self

    # endregion

    # region where
    @overload
    def where(self, col: Callable[[T], bool]) -> Self:
        ...

    @overload
    def where[TValue](self, col: Callable[[T], str], value: TValue) -> Self:
        ...

    @overload
    def where[TValue](
        self,
        col: Callable[[T], str],
        value: list[TValue] | TValue,
        condition: CONDITIONS,
    ) -> Self:
        ...

    def where[TValue](
        self,
        col: Callable[[T], bool | str],
        value: TValue | list[TValue] = None,
        condition: CONDITIONS = "=",
    ) -> Self:
        self.__add_condition(col, value, condition, " OR ")
        return self

    # endregion

    # region delete
    @overload
    def delete(self) -> None:
        ...

    @overload
    def delete(self, instance: T) -> None:
        ...

    @overload
    def delete(self, instance: list[T]) -> None:
        ...

    def delete(self, instance: T | list[T] = None) -> None:
        def get_pk(instance: T | list[T]) -> Column:
            for col in instance.__dict__.values():
                if isinstance(col, Column) and col.primary_key:
                    # utilizamos la columna que sea primary key si no la encuentra, dara error
                    break
            if not col.primary_key:
                raise Exception(
                    f"La tabla '{self._model.__table_name__}' no tiene primary key"
                )
            return col

        col: str
        if instance is None:
            return self.delete(self.get())

        elif issubclass(instance.__class__, Table):
            pk = get_pk(instance)
            if pk.column_value is None:
                raise Exception(
                    f"No se puede realizar la petición 'DELETE' sin establecer un valor único para la primary key '{pk.column_name}'"
                )
            col = pk.column_name
            value = str(pk.column_value)

        elif isinstance(instance, list):
            value = []
            for ins in instance:
                pk = get_pk(ins)
                col = pk.column_name
                value.append(str(pk.column_value))

        else:
            raise Exception(f"'{type(instance)}' dato no esperado")

        self._repository.delete(self._model.__table_name__, col=col, value=value)
        return None

    # endregion


# endregion
