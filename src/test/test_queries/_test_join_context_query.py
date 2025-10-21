from test.models import D


from ormlambda.sql.clauses.select import Select
from ormlambda.sql import functions as func
from ormlambda.dialects import mysql

DIALECT = mysql.dialect


def test_select_with_concat():
    selected = Select[D](
        D,
        lambda d: (
            func.Concat[D]((D.pk_d, "-", D.C.pk_c, "-", D.C.B.pk_b, "-", D.C.B.A, "-", D.C.B.data), alias_clause="concat_pks", dialect=DIALECT),
            d,
            d.C.B.A.data_a,
            d.C,
            func.Count(D.C.B.A.name_a, alias_table=lambda x: x.dtype, dialect=DIALECT),
            func.Max(D.C.B.A.data_a, dialect=DIALECT),
        ),
        dialect=DIALECT,
    )
    query_string: str = "SELECT CONCAT(`d`.pk_d, '-', `d_fk_c_pk_c`.pk_c, '-', b.pk_b, '-', `a`.pk_a, `a`.name_a, `a`.data_a, `a`.date_a, `a`.value, '-', b.data) AS `concat_pks`, `d`.pk_d AS `d_pk_d`, `d`.data_d AS `d_data_d`, `d`.fk_c AS `d_fk_c`, `d`.fk_extra_c AS `d_fk_extra_c`, `a`.data_a AS `a_data_a`, `d_fk_c_pk_c`.pk_c AS `c_pk_c`, `d_fk_c_pk_c`.data_c AS `c_data_c`, `d_fk_c_pk_c`.fk_b AS `c_fk_b`, COUNT(`a`.name_a) AS `count`, MAX(`a`.data_a) AS `max` FROM d AS `d`"
    assert selected.compile(DIALECT).string == query_string
