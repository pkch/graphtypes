# module: graph.py
from typing import (
    Set, Dict, DefaultDict, Iterable, Iterator,
    Any, Type, AbstractSet, TypeVar
)
from collections import defaultdict
from io import StringIO
import pytest  # type: ignore
from igraph import IGraphMutable, INodeMutable, InvalidOperation
from graph_functions import generic_tests


T = TypeVar('T', bound='Node')


class Node(INodeMutable):
    _adj: 'Set[INodeMutable]'

    def __init__(self, value: Any = None) -> None:
        self.value = value
        self._adj = set()

    def __iter__(self: T) -> Iterator[T]:
        return iter(self._adj)  # type: ignore

    def __len__(self) -> int:
        return len(self._adj)

    def __contains__(self, item: object) -> bool:
        return item in self._adj

    def __repr__(self) -> str:
        return '<Node {} at {}>'.format(self.value, id(self))


# this is a concrete implementation, using concrete Node class
class Graph(IGraphMutable):
    nodes: Set[INodeMutable]

    def __init__(self) -> None:
        self.nodes = set()

    # the return type must be the actual Node class, not the interface
    def add_node(self, value: Any = None) -> INodeMutable:
        '''
        Creates a new node that stores the provided value
        Adds the new node to the graph and returns it
        '''
        n = Node(value)
        self.nodes.add(n)
        return n

    def remove_node(self, node: INodeMutable) -> None:
        '''
        Removes the specified node and all edges to and from it
        Raises if node is not present
        '''
        for v in self.nodes:
            v._adj.discard(node)
        self.nodes.remove(node)

    def add_edge(self, tail: INodeMutable, head: INodeMutable) -> None:
        '''
        Adds the specified edge
        Raises if it's already present
        '''
        if head in tail:
            raise InvalidOperation('Attempted to add a duplicate edge')
        tail._adj.add(head)

    def remove_edge(self, tail: INodeMutable, head: INodeMutable) -> None:
        '''
        Removes the specified edge
        Raises if it's not present
        '''
        tail._adj.remove(head)

    def __repr__(self) -> str:
        return '<Graph with {} nodes>\nNodes: {}'.format(len(self.nodes), self.nodes)


@pytest.mark.parametrize('test_func', generic_tests)
def test_graph(test_func):  # type: ignore
    test_func(Graph)
