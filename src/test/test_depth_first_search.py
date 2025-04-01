import unittest
import sys
from pathlib import Path

sys.path.insert(0, [str(x.parent) for x in Path(__file__).parents if x.name == "test"].pop())


from ormlambda.utils.module_tree.dfs_traversal import DFSTraversal  # noqa: E402
from test.models import Address, City, Country  # noqa: E402ry


class TestDFS(unittest.TestCase):
    def test_dfs(self):
        graph = {
            Address: [City],
            City: [Country],
            Country: [],
        }

        topological_sort = DFSTraversal.sort(graph)
        self.assertTupleEqual(topological_sort, (Country, City, Address))

    def test_dfs_with_int(self):
        graph = {
            0: [],
            1: [],
            2: [3],
            3: [1],
            4: [1],
            5: [0],
        }

        topological_sort = DFSTraversal.sort(graph)
        possible_solutions = (
            (1, 0, 3, 5, 4, 2),
            (0, 1, 5, 4, 3, 2),
        )
        self.assertIn(topological_sort, possible_solutions)

    def test_dfs_kahn_algorithm(self):
        graph = {
            "A": ["B", "C", "D"],
            "B": ["E", "F"],
            "C": ["G"],
            "D": ["G", "H"],
            "E": [],
            "F": ["I", "J"],
            "G": ["K"],
            "H": [],
            "I": [],
            "J": ["K"],
            "K": [],
        }

        topological_sort = DFSTraversal.sort(graph)

        possible_solutions = ("K", "J", "I", "H", "G", "F", "E", "D", "C", "B", "A")
        # 3 5 2 4 7 6
        self.assertTupleEqual(topological_sort, possible_solutions)

    def test_dfs_kahn_algorithm_with_cycle(self):
        graph = {
            "A": ["B", "C", "D"],
            "B": ["E", "F"],
            "C": ["K"],
            "D": ["G", "H"],
            "E": [],
            "F": ["I", "J"],
            "G": ["C"],
            "H": [],
            "I": [],
            "J": ["K"],
            "K": ["G"],
        }

        topological_sort = DFSTraversal.sort(graph)
        possible_solutions = ("J", "I", "H", "F", "E", "D", "B", "A")
        # 3 5 2 4 7 6
        self.assertTupleEqual(topological_sort, possible_solutions)

    def test_dfs_with_node_alone(self):
        adj = {
            0: [2, 3, 6],
            1: [4],
            2: [6],
            3: [1, 4],
            4: [5, 8],
            5: [],
            6: [7, 11],
            7: [4, 12],
            8: [],
            9: [10],
            10: [6],
            11: [12],
            12: [8],
            13: [],
        }

        result = DFSTraversal.sort(adj)
        self.assertTupleEqual(result, (8, 5, 12, 4, 11, 7, 6, 1, 10, 3, 2, 13, 9, 0))


if __name__ == "__main__":
    unittest.main()
