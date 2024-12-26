import unittest

import test_abstract_model
import test_clause_info
import test_code_first
import test_column
import test_comparer
import test_constructor
import test_depth_first_search
import test_errors
import test_mapped_table
import test_queries_with_different_datatypes
import test_ResolverType
import test_table_class
import test_type_hint
import testing_dbcontext


from test_queries import (
    test_ForeignKey_query,
    test_join_query,
    test_select_query,
    test_table_query,
    test_where_query,
    test_join_context_query,
)

from test_sql_statements import (
    test_sql_statement,
    test_join_statement,
    test_order_statement,
    test_select_statement,
    test_where_statement,
    test_count_statement,
)

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(
    (
        # region query tests
        *loader.loadTestsFromModule(test_ForeignKey_query),
        *loader.loadTestsFromModule(test_select_query),
        *loader.loadTestsFromModule(test_where_query),
        *loader.loadTestsFromModule(test_join_context_query),
        *loader.loadTestsFromModule(test_join_query),
        *loader.loadTestsFromModule(test_table_query),
        # endregion
        # region statement tests
        *loader.loadTestsFromModule(test_select_statement),
        *loader.loadTestsFromModule(test_join_statement),
        *loader.loadTestsFromModule(test_sql_statement),
        *loader.loadTestsFromModule(test_count_statement),
        *loader.loadTestsFromModule(test_select_statement),
        *loader.loadTestsFromModule(test_where_statement),
        *loader.loadTestsFromModule(test_order_statement),
        *loader.loadTestsFromModule(test_where_statement),
        # endregion
        # region other tests
        *loader.loadTestsFromModule(test_abstract_model),
        *loader.loadTestsFromModule(test_clause_info),
        *loader.loadTestsFromModule(test_code_first),
        *loader.loadTestsFromModule(test_column),
        *loader.loadTestsFromModule(test_comparer),
        *loader.loadTestsFromModule(test_constructor),
        *loader.loadTestsFromModule(test_depth_first_search),
        *loader.loadTestsFromModule(test_errors),
        *loader.loadTestsFromModule(test_mapped_table),
        *loader.loadTestsFromModule(test_queries_with_different_datatypes),
        *loader.loadTestsFromModule(test_ResolverType),
        *loader.loadTestsFromModule(test_table_class),
        *loader.loadTestsFromModule(test_type_hint),
        *loader.loadTestsFromModule(testing_dbcontext),
        # endregion
    )
)


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
