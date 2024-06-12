# region imports
from abc import ABC
from collections import defaultdict
from typing import Any, Callable, Optional, Self, Type, overload, Iterable
import dis
from queue import Queue

from .orm_objects.queries.order import OrderType
from .orm_objects.queries import SQLQuery
from .orm_objects.foreign_key import ForeignKey
from .orm_objects.queries.select import SelectQuery, TableColumn
from .orm_objects import Column, Table

from .interfaces import IRepositoryBase
from .condition_types import ConditionType

# endregion


class ModelBase[T: Table](ABC):
    """
    Clase base de las clases Model.

    Contiene los metodos necesarios para hacer consultas a una tabla
    """

    # region Constructor
    def __init__(self, model: T, *, repository: IRepositoryBase):
        self._model: T = model
        self.build_query: SQLQuery[T] = SQLQuery()

        if not issubclass(self._model, Table):
            # Deben heredar de Table ya que es la forma que tenemos para identificar si estamos pasando una instancia del tipo que corresponde o no cuando llamamos a insert o upsert.
            # Si no heredase de Table no sabriamos identificar el tipo de dato del que se trata porque al llamar a isinstance, obtendriamos el nombre de la clase que mapea a la tabla, Encargo, Edificio, Presupuesto y no podriamos crear una clase generica

            raise Exception(f"La clase '{model}' no hereda de Table")

        if model.__table_name__ is Ellipsis:
            raise Exception(f"Se debe declarar la variabnle '__table_name__' en la clase '{model.__name__}'")

        self._repository: IRepositoryBase = repository

    # endregion

    # region Private methods
    def __repr__(self):
        return f"<Model: {self.__class__.__name__}>"

    @staticmethod
    def __is_valid(column: Column) -> bool:
        """
        Validamos si la columna la debemos eliminar o no a la hora de insertar o actualizar valores.

        Querremos elimina un valor de nuestro objeto cuando especifiquemos un valor que en la bbdd sea AUTO_INCREMENT o AUTO GENERATED ALWAYS AS (__) STORED.

        RETURN
        -----

        - True  -> No eliminamos la columna de la consulta
        - False -> Eliminamos la columna
        """
        # not all to get False and deleted column
        return not all(
            [
                column.column_value is None,
                column.is_auto_increment,
                column.is_primary_key,
                column.is_auto_generated,
            ]
        )
    @classmethod
    def __create_dict_list(cls, _list: list, values: T | list[T]):
        if issubclass(values.__class__, Table):
            dicc: dict = {}
            for col in values.__dict__.values():
                if isinstance(col, Column) and cls.__is_valid(col):
                    dicc.update({col.column_name: col.column_value})
            _list.append(dicc)

        elif isinstance(values, list):
            for x in values:
                cls.__create_dict_list(x)
        else:
            raise Exception(f"Tipo de dato'{type(values)}' no esperado")

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

        lista: list = []
        self.__create_dict_list(lista, values)

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
            if (column.is_auto_increment and not column.is_primary_key) or column.is_auto_generated:
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
    def all(self) -> list[T]: ...

    @overload
    def all[TValue](self, flavour: Optional[TValue]) -> TValue: ...

    @overload
    def all[TValue](self, limit: Optional[int]) -> TValue: ...

    def all[TValue](self, flavour: Optional[TValue] = None, limit: Optional[int] = None) -> list[T] | TValue:
        LIMIT = "" if not limit else f"LIMIT {limit}"
        if flavour is None:
            query_res = self._repository.read_sql(f"SELECT * FROM {self._repository.database}.{self._model.__table_name__} {LIMIT}", flavour=dict)
            return [self._model(**x) for x in query_res]

        return self._repository.read_sql(f"SELECT * FROM {self._model.__table_name__} {LIMIT}", flavour=flavour)

    # endregion

    # region get
    @overload
    def get[TValue](self, col: Callable[[T], None], flavour: TValue) -> TValue | list[TValue] | None: ...

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
    def get[TValue](self, col: list[Callable[[T], None]], flavour: TValue) -> list[TValue] | None:
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
    ) -> T | list[T] | None: ...

    # endregion

    # region first
    @overload
    def first[TValue](self, col: Callable[[T], None], flavour: TValue) -> TValue | list[TValue] | None: ...

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
    def filter_by(self, col: Callable[[T], None], value: int | float | str, condition: ConditionType) -> Self:
        """
        Specifies "REGEXP" in "condition" arg to makes regular expression match
        """
        ...

    def filter_by(
        self,
        col: Callable[[T], None],
        value: int | float | str = None,
        condition: ConditionType = "=",
    ) -> Self:
        # self._conditions.put(Condition(lambda x: x.))
        self.__add_condition(col, value, condition, " AND ")
        return self

    # endregion

    # # region where
    # def where[TValue](
    #     self,
    #     col: Callable[[T], bool | str],
    #     value: TValue | list[TValue] = None,
    #     condition: ConditionType = "=",
    # ) -> Self:
    #     self.__add_condition(col, value, condition, " OR ")
    #     return self

    # # endregion

    # region delete
    @overload
    def delete(self) -> None: ...

    @overload
    def delete(self, instance: T) -> None: ...

    @overload
    def delete(self, instance: list[T]) -> None: ...

    def delete(self, instance: T | list[T] = None) -> None:
        def get_pk(instance: T | list[T]) -> Column:
            for col in instance.__dict__.values():
                if isinstance(col, Column) and col.is_primary_key:
                    # utilizamos la columna que sea primary key si no la encuentra, dara error
                    break
            if not col.is_primary_key:
                raise Exception(f"La tabla '{self._model.__table_name__}' no tiene primary key")
            return col

        col: str
        if instance is None:
            return self.delete(self.select())

        elif issubclass(instance.__class__, Table):
            pk = get_pk(instance)
            if pk.column_value is None:
                raise Exception(f"No se puede realizar la petición 'DELETE' sin establecer un valor único para la primary key '{pk.column_name}'")
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

    # region public methods

    def join(
        self,
        table_right: "Table",
        *,
        by: str,
    ) -> Self:
        self.build_query.join(self._model, table_right, by=by)
        return self

    @overload
    def where(self, lambda_: Callable[[T], bool]) -> Self:
        """
        This method creates where clause by passing the lambda's condition

        EXAMPLE
        -
        mb = ModelBase()
        mb.where(lambda a: 10 <= a.city_id <= 100)
        """
        ...

    @overload
    def where(self, lambda_: Callable[[T], Iterable]) -> Self:
        """
        This method creates where clause by passing the Iterable in lambda function
        EXAMPLE
        -
        mb = ModelBase()
        mb.where(lambda a: (a.city, ConditionType.REGEXP, r"^B"))
        """
        ...

    @overload
    def where(self, lambda_: Callable[[T], bool], **kwargs) -> Self:
        """
        PARAM
        -

        -kwargs: Use this when you need to replace variables inside a lambda method. When working with lambda methods, all variables will be replaced by their own variable names. To avoid this, we need to pass key-value parameters  to specify which variables we want to replace with their values.

        EXAMPLE
        -
        mb = ModelBase()

        external_data = "
        mb.where(lambda a: a.city_id > external_data)
        """
        ...

    def where(self, lambda_: Callable[[T], bool] = lambda: None, **kwargs) -> Self:
        self.build_query.where(instance=tuple([self._model]), lambda_=lambda_, **kwargs)
        return self

    def order(self, _lambda_col: Callable[[T], None], order_type: OrderType) -> Self:
        self.build_query.order(self._model, _lambda_col, order_type)
        return self

    @overload
    def select[*Ts](self, selector: Optional[Callable[[T, *Ts], None]]) -> T | Iterable[T] | str: ...

    @overload
    def select[*Ts, TValue](self, selector: Optional[Callable[[T, *Ts], None]], flavour: TValue) -> Iterable[TValue]: ...

    def select[*Ts, TValue](
        self,
        selector: Optional[Callable[[T, *Ts], None]] = lambda: None,
        *,
        flavour: TValue = None,
    ) -> TValue | T | Iterable[T]:
        select = self.build_query.select(selector, self._model)

        query: str = self.build_query.build()

        if flavour:
            return self._return_flavour(query, flavour)
        return self._return_model(select, query)

    def _return_flavour[TValue](self, query, flavour: TValue) -> list[TValue]:
        return self._repository.read_sql(query, flavour=flavour)

    def _return_model(self, select: SelectQuery, query: str) -> list[T] | T | str:
        response_sql: str | list[dict[str, Any]] = self._repository.read_sql(query, flavour=dict)  # store all columns of the SQL query

        if response_sql and not isinstance(response_sql, str) and isinstance(response_sql, Iterable):
            cluster: list[T] | T | str = ClusterQuery(select, response_sql).clean_response()
            return cluster

        return response_sql

    # endregion


class ClusterQuery:
    def __init__(self, select: SelectQuery, response_sql: dict[list[dict[str, Any]]]) -> None:
        self._select: SelectQuery = select
        self._response_sql: dict[list[dict[str, Any]]] = response_sql

    def loop_foo(self) -> dict[Type[Table], list[Table]]:
        #  We must ensure to get the valid attributes for each instance
        table_initialize = defaultdict(list)

        unic_table: dict[Table, list[TableColumn]] = defaultdict(list)
        for table_col in self._select._select_list:
            unic_table[table_col._table].append(table_col)

        for table_, table_col in unic_table.items():
            for dicc_cols in self._response_sql:
                valid_attr: dict[str, Any] = {}
                for col in table_col:
                    valid_attr[col.real_column] = dicc_cols[col.alias]
                # COMMENT: At this point we are going to instantiate Table class with specific attributes getting directly from database
                table_initialize[table_].append(table_(**valid_attr))
        return table_initialize

    def clean_response(self) -> Iterable | str:
        tbl_dicc: dict[Type[Table], list[Table]] = self.loop_foo()

        # Avoid
        if len(tbl_dicc) == 1:
            val = tuple(tbl_dicc.values())[0]
            if len(val) == 1:
                return val[0]
            return val

        for key, val in tbl_dicc.items():
            if len(val) == 1:
                tbl_dicc[key] = val[0]

        return tuple(tbl_dicc.values())
