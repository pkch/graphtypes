from typing import (
    TypeVar, Generic, Set, List, Dict, Callable, DefaultDict, Iterable, AbstractSet, Iterator
)
from collections import defaultdict
from io import StringIO
import pytest  # type: ignore
import re


class InvalidOperation(Exception): ...


T = TypeVar('T')  # represents value type provided by user, and wrapped into Node


class Node(Generic[T], Iterable):
    '''
    public API:
    * value attribute
    * adj property
    '''

    # type annotation for instance attribute
    _adj: 'Set[Node[T]]'

    # None default value automatically adds Optional to the argument type
    def __init__(self, value: T = None) -> None:
        self.value = value
        self._adj = set()

    def __iter__(self) -> 'Iterator[Node[T]]':
        return iter(self._adj)

    def __repr__(self) -> str:
        return '<Node {}>'.format(self.value)


class Graph(Generic[T]):

    nodes: Set[Node[T]]

    def __init__(self) -> None:
        self.nodes = set()

    def add_node(self, value: T = None) -> Node[T]:
        '''
        Creates a new node that stores the provided value
        Adds the new node to the graph and returns it
        '''
        n = Node(value)
        self.nodes.add(n)
        return n

    def remove_node(self, node: Node[T]) -> None:
        '''
        Removes the specified node and all edges to and from it
        Raises if node is not present
        '''
        for v in self.nodes:
            v._adj.discard(node)
        self.nodes.remove(node)

    def add_edge(self, tail: Node[T], head: Node[T]) -> None:
        '''
        Adds the specified edge
        Raises if it's already present
        '''
        if head in tail:
            raise InvalidOperation('Attempted to add a duplicate edge')
        tail._adj.add(head)

    def remove_edge(self, tail: Node[T], head: Node[T]) -> None:
        '''
        Removes the specified edge
        Raises if it's not present
        '''
        tail._adj.remove(head)

    def __repr__(self) -> str:
        return f'<Graph with {len(self.nodes)} nodes>\nNodes: {self.nodes}'


def read_graph(s: Iterable[str], node_type: Callable[[str], T]) -> Graph[T]:
    g = Graph[T]()
    nodes: DefaultDict[str, Node[T]] = defaultdict(g.add_node)

    for line in s:
        node_id, value, *neighbor_ids = line.split()
        nodes[node_id].value = node_type(value)
        for neighbor_id in neighbor_ids:
            g.add_edge(nodes[node_id], nodes[neighbor_id])
    return g


def write_graph(g: Graph[T]) -> str:
    output: List[str] = []
    nodes = {node: node_id for node_id, node in enumerate(g.nodes)}
    for node, node_id in nodes.items():
        output.append(str(node_id))
        output.append(' ' + str(node.value))
        output.extend([' ' + str(nodes[neighbor]) for neighbor in node])
        output.append('\n')
    return ''.join(output)


def labeled_graph_eq(g1: Graph[T], g2: Graph[T]) -> bool:
    '''
    Compares two labeled graphs for equality
    Labels have to be hashable and unique
    '''

    if len(g1.nodes) != len(g2.nodes):
        return False
    labels1 = {node.value: node for node in g1.nodes}
    labels2 = {node.value: node for node in g2.nodes}
    if set(labels1) != set(labels2):
        return False
    # if labels not unique, we don't know the answer
    if len(labels1) != len(g1.nodes):
        raise NotImplementedError

    for label in labels1:
        node1 = labels1[label]
        node2 = labels2[label]
        if {n.value for n in node1} != {n.value for n in node2}:
            return False

    return True


def get_test_graph() -> Graph[str]:
    g = Graph[str]()
    a = g.add_node('A')
    b = g.add_node('B')
    c = g.add_node('C')
    g.add_node('D')
    g.add_edge(a, a)
    g.add_edge(a, b)
    g.add_edge(a, c)
    g.add_edge(c, b)
    return g


def test_basic_functions() -> None:
    g = Graph[str]()
    v = g.add_node()
    w = g.add_node()
    g.add_edge(v, w)
    with pytest.raises(InvalidOperation):
        g.add_edge(v, w)

    g = get_test_graph()
    assert str(g).startswith('<Graph with 4 nodes>\n')

    node_str = {re.sub(r' at \d+', '', str(node)) for node in g.nodes}
    assert node_str == {'<Node A>', '<Node B>', '<Node C>', '<Node D>'}
    for v in list(g.nodes):  # need list(), otherwise set changes during iteration
        g.remove_node(v)
    assert len(g.nodes) == 0

    g = get_test_graph()
    for v in g.nodes:
        for w in list(v):
            g.remove_edge(v, w)
    for v in g.nodes:
        assert len(list(v)) == 0


def test_labeled_eq() -> None:
    g1 = get_test_graph()
    g2 = get_test_graph()
    assert labeled_graph_eq(g1, g2)

    next(iter(g1.nodes)).value = 'Z'
    assert not labeled_graph_eq(g1, g2)


def test_serialization() -> None:
    g = get_test_graph()

    g_str = StringIO('''0 A 0 1 2
    1 B
    2 C 1
    3 D''')
    assert labeled_graph_eq(read_graph(g_str, str), g)
    assert labeled_graph_eq(read_graph(StringIO(write_graph(g)), str), g)
