import sys
import unittest
import logging
from test_aggregation_functions import (
    test_alias,
    test_concat,
    test_count,
    test_max,
)

from test_queries import (
    test_DecompositionQueryBase,
    test_ForeignKey_query,
    # test_group_by,
    test_join_context_query,
    test_join_query,
    test_QueryBuilder,
    test_select_query,
    test_table_query,
    test_where_query,
)

from test_sql_statements import (
    test_count_statement,
    test_join_statement,
    test_order_statement,
    test_select_statement,
    test_sql_statement,
    test_where_statement,
)

import test_abstract_model
import test_cast
import test_clause_info
import test_code_first
import test_column
import test_comparer
import test_constructor
import test_depth_first_search
import test_errors
import test_mapped_table
import test_queries_with_different_datatypes
import test_table_class
import test_type_hint

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)

log = logging.getLogger(__name__)

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(
    (
        *loader.loadTestsFromModule(test_alias),
        *loader.loadTestsFromModule(test_concat),
        *loader.loadTestsFromModule(test_count),
        *loader.loadTestsFromModule(test_max),
        *loader.loadTestsFromModule(test_DecompositionQueryBase),
        *loader.loadTestsFromModule(test_ForeignKey_query),
        # *loader.loadTestsFromModule(test_group_by),
        *loader.loadTestsFromModule(test_join_context_query),
        *loader.loadTestsFromModule(test_join_query),
        *loader.loadTestsFromModule(test_QueryBuilder),
        *loader.loadTestsFromModule(test_select_query),
        *loader.loadTestsFromModule(test_table_query),
        *loader.loadTestsFromModule(test_where_query),
        # region statement tests
        *loader.loadTestsFromModule(test_count_statement),
        *loader.loadTestsFromModule(test_join_statement),
        *loader.loadTestsFromModule(test_order_statement),
        *loader.loadTestsFromModule(test_select_statement),
        *loader.loadTestsFromModule(test_sql_statement),
        *loader.loadTestsFromModule(test_where_statement),
        # endregion
        # region other tests
        *loader.loadTestsFromModule(test_abstract_model),
        *loader.loadTestsFromModule(test_cast),
        *loader.loadTestsFromModule(test_clause_info),
        *loader.loadTestsFromModule(test_code_first),
        *loader.loadTestsFromModule(test_column),
        *loader.loadTestsFromModule(test_comparer),
        *loader.loadTestsFromModule(test_constructor),
        *loader.loadTestsFromModule(test_depth_first_search),
        *loader.loadTestsFromModule(test_errors),
        *loader.loadTestsFromModule(test_mapped_table),
        *loader.loadTestsFromModule(test_queries_with_different_datatypes),
        *loader.loadTestsFromModule(test_table_class),
        *loader.loadTestsFromModule(test_type_hint),
        # endregion
    )
)


class CustomTextTestRunner(unittest.TextTestRunner):
    def __init__(
        self,
        stream=None,
        descriptions=True,
        verbosity=1,
        failfast=False,
        buffer=False,
        resultclass=None,
        warnings=None,
        *,
        tb_locals=False,
        durations=None,
    ):
        super().__init__(
            stream,
            descriptions,
            verbosity,
            failfast,
            buffer,
            resultclass,
            warnings,
            tb_locals=tb_locals,
            durations=durations,
        )

    def run(self, test):
        # This method is called before each test is run
        result = super().run(test)
        return result

    def _makeResult(self):
        # Create the result object
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)


class CustomTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity, *, durations = None):
        super().__init__(stream, descriptions, verbosity, durations=durations)

    def startTest(self, test):
        # Print the test name just before it runs
        log.info(f"Running: {test}")
        super().startTest(test)


if __name__ == "__main__":
    runner = CustomTextTestRunner()
    result = runner.run(suite)
