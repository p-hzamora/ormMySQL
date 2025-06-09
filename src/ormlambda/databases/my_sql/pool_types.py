from typing import Callable, Optional, Type, TypedDict, Any

from mysql.connector.constants import (
    CharacterSet,
    ClientFlag,
)
from mysql.connector.types import HandShakeType, BinaryProtocolType
from mysql.connector.conversion import MySQLConverter


class MySQLArgs(TypedDict):
    client_flags: ClientFlag | int
    sql_mode: Optional[str]
    time_zone: Optional[str]
    autocommit: bool
    server_version: Optional[tuple[int, ...]]
    handshake: Optional[HandShakeType]
    conn_attrs: dict[str, str]

    user: str
    password: str
    password1: str
    password2: str
    password3: str
    database: str
    host: str
    port: int
    unix_socket: Optional[str]
    client_host: str
    client_port: int
    ssl: dict[str, Optional[str | bool | list[str]]]
    ssl_disabled: bool
    force_ipv6: bool
    oci_config_file: Optional[str]
    oci_config_profile: Optional[str]
    webauthn_callback: Optional[str | Callable[[str], None]]
    krb_service_principal: Optional[str]
    openid_token_file: Optional[str]

    use_unicode: bool
    get_warnings: bool
    raise_on_warnings: bool
    connection_timeout: Optional[int]
    read_timeout: Optional[int]
    write_timeout: Optional[int]
    buffered: bool
    unread_result: bool
    have_next_result: bool
    raw: bool
    in_transaction: bool
    allow_local_infile: bool
    allow_local_infile_in_path: Optional[str]

    prepared_statements: Any
    query_attrs: dict[str, BinaryProtocolType]

    ssl_active: bool
    auth_plugin: Optional[str]
    auth_plugin_class: Optional[str]
    pool_config_version: Any
    converter_class: Optional[Type[MySQLConverter]]
    converter_str_fallback: bool
    compress: bool

    consume_results: bool
    init_command: Optional[str]
    character_set: CharacterSet


__all__ = [
    "MySQLArgs",
    "ClientFlag",
]
