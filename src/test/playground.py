from __future__ import annotations
from datetime import datetime
import sys
from pathlib import Path
from typing import Literal, Optional

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda import ORM, create_engine, Table, Column, ForeignKey

DATABASE_URL = "sqlite:///~/Downloads/tesela.db"


class Proveedor(Table):
    __table_name__ = "proveedor"
    pk_proveedor: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    name: Column[str]
    surname_1: Column[str]
    surname_2: Column[str]


class Proyecto(Table):
    __table_name__ = "projecto"
    pk_projecto: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    codigo: Column[str]
    direccion: Column[str]
    status: Column[str]
    created_at: Column[datetime]


type Option = Literal[
    "SI",
    "NO",
    "PTE",
    "REVISADO",
]


class PrecioContradictorio(Table):
    __table_name__ = "precio_contradictorio"
    pk_contradictorio: Column[int] = Column(int, is_primary_key=True, is_auto_increment=True)
    fk_projecto: Column[int] = Column(int)
    codigo: Column[str]
    contradictorios: Column[str]
    fk_proveedor: Column[Optional[int]] = Column(int)

    fecha_enviado: Column[str]
    recibido: Column[str]
    imp_total: Column[float]
    revisado: Column[str]
    enviado: Column[str]

    medio_de_envio: Column[str]
    fecha_envio: Column[datetime]
    aprobado: Column[str]
    firmado: Column[str]

    Proveedor = ForeignKey["PrecioContradictorio", Proveedor](Proveedor, lambda self, out: self.fk_proveedor == out.pk_proveedor)
    Projecto = ForeignKey["PrecioContradictorio", Proyecto](Proyecto, lambda self, out: self.fk_projecto == out.pk_projecto)


engine = create_engine(DATABASE_URL)


ProveedorModel = ORM(Proveedor, engine)
ProjectoModel = ORM(Proyecto, engine)
PrecioContradictorioModel = ORM(PrecioContradictorio, engine)


ProveedorModel.create_table("replace")
ProjectoModel.create_table("replace")
PrecioContradictorioModel.create_table("replace")

project = Proyecto(None, "CE24045", "Calle virgen de la oliva 1", "Activa", datetime.now())
proveedor = Proveedor(None, "Rosman")
contradictorios = [
    PrecioContradictorio(
        pk_contradictorio=None,
        fk_projecto=1,
        codigo="PC01",
        contradictorios="DEMOLICIÓN DE DINTELES Y MOCHETAS",
        fk_proveedor=None,
        fecha_enviado=None,
        recibido="SI",
        imp_total=float(576.00),
        revisado="SI",
        enviado="SI",
        medio_de_envio="email",
        fecha_envio=datetime.now(),
        aprobado="SI",
        firmado="SI",
    ),
    PrecioContradictorio(
        pk_contradictorio=None,
        fk_projecto=1,
        codigo="PC02",
        contradictorios="PICADO DE RECRECIDO DE MORTERO",
        fk_proveedor=1,
        fecha_enviado=None,
        recibido="SI",
        imp_total=float(384.00),
        revisado="SI",
        enviado="SI",
        medio_de_envio="email",
        fecha_envio=datetime.now(),
        aprobado="SI",
        firmado="SI",
    ),
    PrecioContradictorio(
        pk_contradictorio=None,
        fk_projecto=1,
        codigo="PC03",
        contradictorios="SUSTITUCION DE BAJANTES DE URALITA",
        fk_proveedor=1,
        fecha_enviado=None,
        recibido="SI",
        imp_total=float(2237.29),
        revisado="SI",
        enviado="SI",
        medio_de_envio="email",
        fecha_envio=datetime.now(),
        aprobado="SI",
        firmado="SI",
    ),
]

ProjectoModel.insert(project)
ProveedorModel.insert(proveedor)
PrecioContradictorioModel.insert(contradictorios)
pass

PrecioContradictorioModel.drop_table()
ProjectoModel.drop_table()
ProveedorModel.drop_table()
