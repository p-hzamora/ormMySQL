import unittest

import test_abstract_model
import test_code_first
import test_depth_first_search
import test_disassembler
import test_mapped_table
import test_nested_element
import test_sql_statements
import test_table_class
import test_tree_instruction
import test_type_hint
import test_order

from test_queries import (
    test_join_selector,
    test_relationship_fk,
    test_select,
    test_table,
    test_where_condition,
    test_count,
)

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(
    (
        *loader.loadTestsFromModule(test_abstract_model),
        *loader.loadTestsFromModule(test_code_first),
        *loader.loadTestsFromModule(test_depth_first_search),
        *loader.loadTestsFromModule(test_disassembler),
        *loader.loadTestsFromModule(test_mapped_table),
        *loader.loadTestsFromModule(test_nested_element),
        *loader.loadTestsFromModule(test_sql_statements),
        *loader.loadTestsFromModule(test_table_class),
        *loader.loadTestsFromModule(test_tree_instruction),
        *loader.loadTestsFromModule(test_type_hint),
        *loader.loadTestsFromModule(test_join_selector),
        *loader.loadTestsFromModule(test_relationship_fk),
        *loader.loadTestsFromModule(test_select),
        *loader.loadTestsFromModule(test_table),
        *loader.loadTestsFromModule(test_where_condition),
        *loader.loadTestsFromModule(test_count),
        *loader.loadTestsFromModule(test_order),
    )
)


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
