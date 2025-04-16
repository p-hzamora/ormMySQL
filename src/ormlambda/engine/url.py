"""
URL class extracted from SQLAlchemy
"""
from __future__ import annotations

import re
import collections.abc as collections_abc
from typing import (
    Any,
    Literal,
    cast,
    Iterable,
    Mapping,
    NamedTuple,
    Optional,
    overload,
    Sequence,
    Union,
)

from urllib.parse import (
    parse_qsl,
    quote,
    quote_plus,
    unquote,
)

from . import utils

type DrivernameType = Literal['mysql'] | str
class URL(NamedTuple):
    """
    Represent the components of a URL used to connect to a database.

    URLs are typically constructed from a fully formatted URL string, where the
    :func:`.make_url` function is used internally by the
    :func:`_sa.create_engine` function in order to parse the URL string into
    its individual components, which are then used to construct a new
    :class:`.URL` object. When parsing from a formatted URL string, the parsing
    format generally follows
    `RFC-1738 <https://www.ietf.org/rfc/rfc1738.txt>`_, with some exceptions.

    A :class:`_engine.URL` object may also be produced directly, either by
    using the :func:`.make_url` function with a fully formed URL string, or
    by using the :meth:`_engine.URL.create` constructor in order
    to construct a :class:`_engine.URL` programmatically given individual
    fields. The resulting :class:`.URL` object may be passed directly to
    :func:`_sa.create_engine` in place of a string argument, which will bypass
    the usage of :func:`.make_url` within the engine's creation process.

    .. versionchanged:: 1.4

        The :class:`_engine.URL` object is now an immutable object.  To
        create a URL, use the :func:`_engine.make_url` or
        :meth:`_engine.URL.create` function / method.  To modify
        a :class:`_engine.URL`, use methods like
        :meth:`_engine.URL.set` and
        :meth:`_engine.URL.update_query_dict` to return a new
        :class:`_engine.URL` object with modifications.   See notes for this
        change at :ref:`change_5526`.

    .. seealso::

        :ref:`database_urls`

    :class:`_engine.URL` contains the following attributes:

    * :attr:`_engine.URL.drivername`: database backend and driver name, such as
      ``postgresql+psycopg2``
    * :attr:`_engine.URL.username`: username string
    * :attr:`_engine.URL.password`: password string
    * :attr:`_engine.URL.host`: string hostname
    * :attr:`_engine.URL.port`: integer port number
    * :attr:`_engine.URL.database`: string database name
    * :attr:`_engine.URL.query`: an immutable mapping representing the query
      string.  contains strings for keys and either strings or tuples of
      strings for values.


    """

    drivername: DrivernameType
    """database backend and driver name, such as
    ``postgresql+psycopg2``

    """

    username: Optional[str]
    "username string"

    password: Optional[str]
    """password, which is normally a string but may also be any
    object that has a ``__str__()`` method."""

    host: Optional[str]
    """hostname or IP number.  May also be a data source name for some
    drivers."""

    port: Optional[int]
    """integer port number"""

    database: Optional[str]
    """database name"""

    query: dict[str, Union[tuple[str, ...], str]]
    """an immutable mapping representing the query string.  contains strings
       for keys and either strings or tuples of strings for values, e.g.::

            >>> from ormlambda.engine import make_url
            >>> url = make_url(
            ...     "postgresql+psycopg2://user:pass@host/dbname?alt_host=host1&alt_host=host2&ssl_cipher=%2Fpath%2Fto%2Fcrt"
            ... )
            >>> url.query
            immutabledict({'alt_host': ('host1', 'host2'), 'ssl_cipher': '/path/to/crt'})

         To create a mutable copy of this mapping, use the ``dict`` constructor::

            mutable_query_opts = dict(url.query)

       .. seealso::

          :attr:`_engine.URL.normalized_query` - normalizes all values into sequences
          for consistent processing

          Methods for altering the contents of :attr:`_engine.URL.query`:

          :meth:`_engine.URL.update_query_dict`

          :meth:`_engine.URL.update_query_string`

          :meth:`_engine.URL.update_query_pairs`

          :meth:`_engine.URL.difference_update_query`

    """  # noqa: E501

    @classmethod
    def create(
        cls,
        drivername: DrivernameType,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        query: Mapping[str, Union[Sequence[str], str]] = {},
    ) -> URL:
        """Create a new :class:`_engine.URL` object.

        .. seealso::

            :ref:`database_urls`

        :param drivername: the name of the database backend. This name will
          correspond to a module in ormlambda/databases or a third party
          plug-in.
        :param username: The user name.
        :param password: database password.  Is typically a string, but may
          also be an object that can be stringified with ``str()``.

          .. note:: The password string should **not** be URL encoded when
             passed as an argument to :meth:`_engine.URL.create`; the string
             should contain the password characters exactly as they would be
             typed.

          .. note::  A password-producing object will be stringified only
             **once** per :class:`_engine.Engine` object.  For dynamic password
             generation per connect, see :ref:`engines_dynamic_tokens`.

        :param host: The name of the host.
        :param port: The port number.
        :param database: The database name.
        :param query: A dictionary of string keys to string values to be passed
          to the dialect and/or the DBAPI upon connect.   To specify non-string
          parameters to a Python DBAPI directly, use the
          :paramref:`_sa.create_engine.connect_args` parameter to
          :func:`_sa.create_engine`.   See also
          :attr:`_engine.URL.normalized_query` for a dictionary that is
          consistently string->list of string.
        :return: new :class:`_engine.URL` object.

        .. versionadded:: 1.4

            The :class:`_engine.URL` object is now an **immutable named
            tuple**.  In addition, the ``query`` dictionary is also immutable.
            To create a URL, use the :func:`_engine.url.make_url` or
            :meth:`_engine.URL.create` function/ method.  To modify a
            :class:`_engine.URL`, use the :meth:`_engine.URL.set` and
            :meth:`_engine.URL.update_query` methods.

        """

        return cls(
            cls._assert_str(drivername, "drivername"),
            cls._assert_none_str(username, "username"),
            password,
            cls._assert_none_str(host, "host"),
            cls._assert_port(port),
            cls._assert_none_str(database, "database"),
            cls._str_dict(query),
        )

    @classmethod
    def _assert_port(cls, port: Optional[int]) -> Optional[int]:
        if port is None:
            return None
        try:
            return int(port)
        except TypeError:
            raise TypeError("Port argument must be an integer or None")

    @classmethod
    def _assert_str(cls, v: str, paramname: str) -> str:
        if not isinstance(v, str):
            raise TypeError("%s must be a string" % paramname)
        return v

    @classmethod
    def _assert_none_str(cls, v: Optional[str], paramname: str) -> Optional[str]:
        if v is None:
            return v

        return cls._assert_str(v, paramname)

    @classmethod
    def _str_dict(
        cls,
        dict_: Optional[
            Union[
                Sequence[tuple[str, Union[Sequence[str], str]]],
                Mapping[str, Union[Sequence[str], str]],
            ]
        ],
    ) -> dict[str, Union[tuple[str, ...], str]]:
        if dict_ is None:
            return {}

        @overload
        def _assert_value(
            val: str,
        ) -> str: ...

        @overload
        def _assert_value(
            val: Sequence[str],
        ) -> Union[str, tuple[str, ...]]: ...

        def _assert_value(
            val: Union[str, Sequence[str]],
        ) -> Union[str, tuple[str, ...]]:
            if isinstance(val, str):
                return val
            elif isinstance(val, collections_abc.Sequence):
                return tuple(_assert_value(elem) for elem in val)
            else:
                raise TypeError("Query dictionary values must be strings or " "sequences of strings")

        def _assert_str(v: str) -> str:
            if not isinstance(v, str):
                raise TypeError("Query dictionary keys must be strings")
            return v

        dict_items: Iterable[tuple[str, Union[Sequence[str], str]]]
        if isinstance(dict_, collections_abc.Sequence):
            dict_items = dict_
        else:
            dict_items = dict_.items()

        return dict(
            {
                _assert_str(key): _assert_value(
                    value,
                )
                for key, value in dict_items
            }
        )

    def set(
        self,
        drivername: Optional[DrivernameType] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        query: Optional[Mapping[str, Union[Sequence[str], str]]] = None,
    ) -> URL:
        """return a new :class:`_engine.URL` object with modifications.

        Values are used if they are non-None.  To set a value to ``None``
        explicitly, use the :meth:`_engine.URL._replace` method adapted
        from ``namedtuple``.

        :param drivername: new drivername
        :param username: new username
        :param password: new password
        :param host: new hostname
        :param port: new port
        :param query: new query parameters, passed a dict of string keys
         referring to string or sequence of string values.  Fully
         replaces the previous list of arguments.

        :return: new :class:`_engine.URL` object.

        .. versionadded:: 1.4

        .. seealso::

            :meth:`_engine.URL.update_query_dict`

        """

        kw: dict[str, Any] = {}
        if drivername is not None:
            kw["drivername"] = drivername
        if username is not None:
            kw["username"] = username
        if password is not None:
            kw["password"] = password
        if host is not None:
            kw["host"] = host
        if port is not None:
            kw["port"] = port
        if database is not None:
            kw["database"] = database
        if query is not None:
            kw["query"] = query

        return self._assert_replace(**kw)

    def _assert_replace(self, **kw: Any) -> URL:
        """argument checks before calling _replace()"""

        if "drivername" in kw:
            self._assert_str(kw["drivername"], "drivername")
        for name in "username", "host", "database":
            if name in kw:
                self._assert_none_str(kw[name], name)
        if "port" in kw:
            self._assert_port(kw["port"])
        if "query" in kw:
            kw["query"] = self._str_dict(kw["query"])

        return self._replace(**kw)

    def update_query_string(self, query_string: str, append: bool = False) -> URL:
        """Return a new :class:`_engine.URL` object with the :attr:`_engine.URL.query`
        parameter dictionary updated by the given query string.

        E.g.::

            >>> from ormlambda.engine import make_url
            >>> url = make_url("postgresql+psycopg2://user:pass@host/dbname")
            >>> url = url.update_query_string(
            ...     "alt_host=host1&alt_host=host2&ssl_cipher=%2Fpath%2Fto%2Fcrt"
            ... )
            >>> str(url)
            'postgresql+psycopg2://user:pass@host/dbname?alt_host=host1&alt_host=host2&ssl_cipher=%2Fpath%2Fto%2Fcrt'

        :param query_string: a URL escaped query string, not including the
         question mark.

        :param append: if True, parameters in the existing query string will
         not be removed; new parameters will be in addition to those present.
         If left at its default of False, keys present in the given query
         parameters will replace those of the existing query string.

        .. versionadded:: 1.4

        .. seealso::

            :attr:`_engine.URL.query`

            :meth:`_engine.URL.update_query_dict`

        """  # noqa: E501
        return self.update_query_pairs(parse_qsl(query_string), append=append)

    def update_query_pairs(
        self,
        key_value_pairs: Iterable[tuple[str, Union[str, list[str]]]],
        append: bool = False,
    ) -> URL:
        """Return a new :class:`_engine.URL` object with the
        :attr:`_engine.URL.query`
        parameter dictionary updated by the given sequence of key/value pairs

        E.g.::

            >>> from ormlambda.engine import make_url
            >>> url = make_url("postgresql+psycopg2://user:pass@host/dbname")
            >>> url = url.update_query_pairs(
            ...     [
            ...         ("alt_host", "host1"),
            ...         ("alt_host", "host2"),
            ...         ("ssl_cipher", "/path/to/crt"),
            ...     ]
            ... )
            >>> str(url)
            'postgresql+psycopg2://user:pass@host/dbname?alt_host=host1&alt_host=host2&ssl_cipher=%2Fpath%2Fto%2Fcrt'

        :param key_value_pairs: A sequence of tuples containing two strings
         each.

        :param append: if True, parameters in the existing query string will
         not be removed; new parameters will be in addition to those present.
         If left at its default of False, keys present in the given query
         parameters will replace those of the existing query string.

        .. versionadded:: 1.4

        .. seealso::

            :attr:`_engine.URL.query`

            :meth:`_engine.URL.difference_update_query`

            :meth:`_engine.URL.set`

        """  # noqa: E501

        existing_query = self.query
        new_keys: dict[str, Union[str, list[str]]] = {}

        for key, value in key_value_pairs:
            if key in new_keys:
                new_keys[key] = utils.to_list(new_keys[key])
                cast("list[str]", new_keys[key]).append(cast(str, value))
            else:
                new_keys[key] = list(value) if isinstance(value, (list, tuple)) else value

        new_query: Mapping[str, Union[str, Sequence[str]]]
        if append:
            new_query = {}

            for k in new_keys:
                if k in existing_query:
                    new_query[k] = tuple(utils.to_list(existing_query[k]) + utils.to_list(new_keys[k]))
                else:
                    new_query[k] = new_keys[k]

            new_query.update({k: existing_query[k] for k in set(existing_query).difference(new_keys)})
        else:
            new_query = self.query.union({k: tuple(v) if isinstance(v, list) else v for k, v in new_keys.items()})
        return self.set(query=new_query)

    def update_query_dict(
        self,
        query_parameters: Mapping[str, Union[str, list[str]]],
        append: bool = False,
    ) -> URL:
        """Return a new :class:`_engine.URL` object with the
        :attr:`_engine.URL.query` parameter dictionary updated by the given
        dictionary.

        The dictionary typically contains string keys and string values.
        In order to represent a query parameter that is expressed multiple
        times, pass a sequence of string values.

        E.g.::


            >>> from ormlambda.engine import make_url
            >>> url = make_url("postgresql+psycopg2://user:pass@host/dbname")
            >>> url = url.update_query_dict(
            ...     {"alt_host": ["host1", "host2"], "ssl_cipher": "/path/to/crt"}
            ... )
            >>> str(url)
            'postgresql+psycopg2://user:pass@host/dbname?alt_host=host1&alt_host=host2&ssl_cipher=%2Fpath%2Fto%2Fcrt'


        :param query_parameters: A dictionary with string keys and values
         that are either strings, or sequences of strings.

        :param append: if True, parameters in the existing query string will
         not be removed; new parameters will be in addition to those present.
         If left at its default of False, keys present in the given query
         parameters will replace those of the existing query string.


        .. versionadded:: 1.4

        .. seealso::

            :attr:`_engine.URL.query`

            :meth:`_engine.URL.update_query_string`

            :meth:`_engine.URL.update_query_pairs`

            :meth:`_engine.URL.difference_update_query`

            :meth:`_engine.URL.set`

        """  # noqa: E501
        return self.update_query_pairs(query_parameters.items(), append=append)

    def difference_update_query(self, names: Iterable[str]) -> URL:
        """
        Remove the given names from the :attr:`_engine.URL.query` dictionary,
        returning the new :class:`_engine.URL`.

        E.g.::

            url = url.difference_update_query(["foo", "bar"])

        Equivalent to using :meth:`_engine.URL.set` as follows::

            url = url.set(
                query={
                    key: url.query[key]
                    for key in set(url.query).difference(["foo", "bar"])
                }
            )

        .. versionadded:: 1.4

        .. seealso::

            :attr:`_engine.URL.query`

            :meth:`_engine.URL.update_query_dict`

            :meth:`_engine.URL.set`

        """

        if not set(names).intersection(self.query):
            return self

        return URL(
            self.drivername,
            self.username,
            self.password,
            self.host,
            self.port,
            self.database,
            dict({key: self.query[key] for key in set(self.query).difference(names)}),
        )

    @property
    def normalized_query(self) -> Mapping[str, Sequence[str]]:
        """Return the :attr:`_engine.URL.query` dictionary with values normalized
        into sequences.

        As the :attr:`_engine.URL.query` dictionary may contain either
        string values or sequences of string values to differentiate between
        parameters that are specified multiple times in the query string,
        code that needs to handle multiple parameters generically will wish
        to use this attribute so that all parameters present are presented
        as sequences.   Inspiration is from Python's ``urllib.parse.parse_qs``
        function.  E.g.::


            >>> from ormlambda.engine import make_url
            >>> url = make_url(
            ...     "postgresql+psycopg2://user:pass@host/dbname?alt_host=host1&alt_host=host2&ssl_cipher=%2Fpath%2Fto%2Fcrt"
            ... )
            >>> url.query
            immutabledict({'alt_host': ('host1', 'host2'), 'ssl_cipher': '/path/to/crt'})
            >>> url.normalized_query
            immutabledict({'alt_host': ('host1', 'host2'), 'ssl_cipher': ('/path/to/crt',)})

        """  # noqa: E501

        return dict({k: (v,) if not isinstance(v, tuple) else v for k, v in self.query.items()})

    def __to_string__(self, hide_password: bool = True) -> str:
        """Render this :class:`_engine.URL` object as a string.

        :param hide_password: Defaults to True.   The password is not shown
         in the string unless this is set to False.

        """
        return self.render_as_string(hide_password=hide_password)

    def render_as_string(self, hide_password: bool = True) -> str:
        """Render this :class:`_engine.URL` object as a string.

        This method is used when the ``__str__()`` or ``__repr__()``
        methods are used.   The method directly includes additional options.

        :param hide_password: Defaults to True.   The password is not shown
         in the string unless this is set to False.

        """
        s = self.drivername + "://"
        if self.username is not None:
            s += quote(self.username, safe=" +")
            if self.password is not None:
                s += ":" + ("***" if hide_password else quote(str(self.password), safe=" +"))
            s += "@"
        if self.host is not None:
            if ":" in self.host:
                s += f"[{self.host}]"
            else:
                s += self.host
        if self.port is not None:
            s += ":" + str(self.port)
        if self.database is not None:
            s += "/" + self.database
        if self.query:
            keys = list(self.query)
            keys.sort()
            s += "?" + "&".join(f"{quote_plus(k)}={quote_plus(element)}" for k in keys for element in utils.to_list(self.query[k]))
        return s

    def __repr__(self) -> str:
        return self.render_as_string()

    def __copy__(self) -> URL:
        return self.__class__.create(
            self.drivername,
            self.username,
            self.password,
            self.host,
            self.port,
            self.database,
            # note this is an immutabledict of str-> str / tuple of str,
            # also fully immutable.  does not require deepcopy
            self.query,
        )

    def __deepcopy__(self, memo: Any) -> URL:
        return self.__copy__()

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, URL) and self.drivername == other.drivername and self.username == other.username and self.password == other.password and self.host == other.host and self.database == other.database and self.query == other.query and self.port == other.port

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def get_backend_name(self) -> str:
        """Return the backend name.

        This is the name that corresponds to the database backend in
        use, and is the portion of the :attr:`_engine.URL.drivername`
        that is to the left of the plus sign.

        """
        if "+" not in self.drivername:
            return self.drivername
        else:
            return self.drivername.split("+")[0]

    def _instantiate_plugins(self, kwargs: Mapping[str, Any]) -> tuple[URL, list[Any], dict[str, Any]]:
        plugin_names = utils.to_list(self.query.get("plugin", ()))
        plugin_names += kwargs.get("plugins", [])

        kwargs = dict(kwargs)

        u = self.difference_update_query(["plugin", "plugins"])

        kwargs.pop("plugins", None)

        for key, value in self.query.items():
            if key not in kwargs:
                kwargs[key] = value

        return u, kwargs


def make_url(name_or_url: str | URL) -> URL:
    """Given a string, produce a new URL instance.

    The format of the URL generally follows `RFC-1738
    <https://www.ietf.org/rfc/rfc1738.txt>`_, with some exceptions, including
    that underscores, and not dashes or periods, are accepted within the
    "scheme" portion.

    If a :class:`.URL` object is passed, it is returned as is.

    .. seealso::

        :ref:`database_urls`

    """

    if isinstance(name_or_url, str):
        return _parse_url(name_or_url)
    elif not isinstance(name_or_url, URL) and not hasattr(name_or_url, "_sqla_is_testing_if_this_is_a_mock_object"):
        raise ValueError(f"Expected string or URL object, got {name_or_url!r}")
    else:
        return name_or_url


def _parse_url(name: str) -> URL:
    pattern = re.compile(
        r"""
            (?P<name>[\w\+]+)://
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>[^@]*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/\?]+)\] |
                    (?P<ipv4host>[^/:\?]+)
                )?
                (?::(?P<port>[^/\?]*))?
            )?
            (?:/(?P<database>[^\?]*))?
            (?:\?(?P<query>.*))?
            """,
        re.X,
    )

    if m := pattern.match(name):
        components = m.groupdict()
        query: Optional[dict[str, str | list[str]]]
        if components["query"] is not None:
            query = {}

            for key, value in parse_qsl(components["query"]):
                if key in query:
                    query[key] = utils.to_list(query[key])
                    cast(list[str], query[key]).append(value)
                else:
                    query[key] = value
        else:
            query = None
        components["query"] = query

        if components["username"] is not None:
            components["username"] = unquote(components["username"])

        if components["password"] is not None:
            components["password"] = unquote(components["password"])

        ipv4host = components.pop("ipv4host")
        ipv6host = components.pop("ipv6host")
        components["host"] = ipv4host or ipv6host
        name = components.pop("name")

        if components["port"]:
            components["port"] = int(components["port"])

        return URL.create(name, **components)  # type: ignore

    else:
        raise ValueError(f"Could not parse URL from string '{name}'")
