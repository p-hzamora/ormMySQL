import sys
from pathlib import Path
from types import NoneType
import unittest
from datetime import datetime
from shapely import Point
from parameterized import parameterized
from typing import Any, NamedTuple, Type


sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())

from ormlambda import Column, Table, ORM
from test.config import create_engine
from ormlambda.dialects import mysql

from ormlambda.dialects.mysql import DECIMAL, INTEGER, MEDIUMINT, TIMESTAMP, TINYINT, VARCHAR


DIALECT = mysql.dialect

def create_url(x:str=""):
    return f"mysql://root:1500@localhost:3306/{x}?pool_size=3"

BORRAR = "borrar"


class EConceptoFacturadoPm(Table):
    __table_name__ = "e_concepto_facturado_pm"

    pk_concepto_facturado_pm: Column[MEDIUMINT] = Column(MEDIUMINT(unsigned=True), is_not_null=True, is_auto_increment=True, is_primary_key=True)

    fk_entregable: Column[MEDIUMINT] = Column(MEDIUMINT(unsigned=True))
    concepto: Column[VARCHAR] = Column(VARCHAR(300))
    informacion_adicional: Column[VARCHAR] = Column(VARCHAR(300))
    base_imponible: Column[DECIMAL] = Column(DECIMAL(10, 2))
    porcentaje_impuesto_a_aplicar: Column[DECIMAL] = Column(DECIMAL(3, 2), is_not_null=True)
    concepto_incluido_en_misma_factura: Column[MEDIUMINT] = Column(MEDIUMINT(unsigned=True))
    enviar_sino: Column[TINYINT] = Column(TINYINT(1), is_not_null=True, default="0")
    fk_ref_factura_anulada: Column[VARCHAR] = Column(VARCHAR(50))
    fk_ref_anticipo: Column[VARCHAR] = Column(VARCHAR(50))
    fk_ref_factura: Column[VARCHAR] = Column(VARCHAR(50))
    enviado_sino: Column[TINYINT] = Column(TINYINT(1), is_not_null=True, default="0")
    timestamp_creacion: Column[TIMESTAMP] = Column(TIMESTAMP(), is_not_null=True, is_auto_generated=True, default="CURRENT_TIMESTAMP")


class TestResolverType(unittest.TestCase):
    def setUp(self):
        temp = create_engine(create_url())
        if not temp.schema_exists(BORRAR):
            temp.create_schema(BORRAR)

        self.engine = create_engine(create_url(BORRAR))
    def test_new_test(self) -> None:
        ORM(EConceptoFacturadoPm, self.engine).create_table()
        pass
        EConceptoFacturadoPm().base_imponible

if __name__ == "__main__":
    unittest.main()
