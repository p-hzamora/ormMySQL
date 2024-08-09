from typing import Iterable
from collections import deque, defaultdict


class DFSTraversal:
    """
    Depth first search with Kahn's algorithm
    """

    @staticmethod
    def sort[T](graph: dict[T, Iterable[T]], raise_: bool = False) -> tuple[T, ...]:
        indegree: dict[T, int] = defaultdict(int)
        for key, val in graph.items():
            for node in val:
                indegree[node] += 1

        q: deque[T] = deque()
        for key in graph:
            if indegree[key] == 0:
                q.append(key)

        topo: list[T] = []
        while q:
            node: T = q.popleft()
            topo.append(node)

            for neighbor in graph[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    q.append(neighbor)

        if len(graph) != len(topo):
            difference = set(graph).difference(set(topo))
            msg = f"Cycle found near of nodes '{difference}'"
            if raise_:
                raise Exception(msg)
            print(msg)
        return tuple(topo[::-1])


if __name__ == "__main__":
    adj = {
        0: [2, 3, 6],
        1: [4],
        2: [6],
        3: [1, 4],
        4: [5, 8],
        5: [],
        6: [7, 11],
        7: [4, 12],
        8: [0],
        9: [10],
        10: [6],
        11: [12],
        12: [8],
        13: [],
    }

    ans = DFSTraversal.sort(adj)
    print(ans)
