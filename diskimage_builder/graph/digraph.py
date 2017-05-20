# Copyright 2016 Andreas Florath (andreas@florath.net)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
import bisect


class Digraph(object):
    """Implements a directed graph.

    Each node of the digraph must have a unique name.
    """

    class Edge(object):
        """Directed graph edge.

        The digraph has weighted edges.  This class holds the weight and
        a reference to the node.
        """

        def __init__(self, node, weight):
            self.__node = node
            self.__weight = weight

        def __eq__(self, other):
            return self.__weight == other.get_weight() \
                and self.__node == other.get_node()

        def __lt__(self, other):
            return self.__weight < other.get_weight()

        def get_node(self):
            """Return the (pointed to) node"""
            return self.__node

        def get_weight(self):
            """Return the edge's weight"""
            return self.__weight

    class Node(object):
        """Directed graph node.

        This holds the incoming and outgoing edges as well as the
        nodes' name.
        """

        def __init__(self, name):
            """Initializes a node.

            Incoming and outgoing are lists of nodes.  Typically one
            direction is provided and the other can be automatically
            computed.
            """
            self.__name = name
            self.__incoming = []
            self.__outgoing = []

        def __repr__(self):
            return "<Node [%s]>" % self.__name

        def get_name(self):
            """Returns the name of the node."""
            return self.__name

        def add_incoming(self, node, weight):
            """Add node to the incoming list."""
            bisect.insort(self.__incoming, Digraph.Edge(node, weight))

        def add_outgoing(self, node, weight):
            """Add node to the outgoing list."""
            bisect.insort(self.__outgoing, Digraph.Edge(node, weight))

        def get_iter_outgoing(self):
            """Return an iterator over the outgoing nodes."""

            return iter([x.get_node() for x in self.__outgoing])

        def has_incoming(self):
            """Returns True if the node has incoming edges"""
            return self.__incoming

        @staticmethod
        def __as_named_list(inlist):
            """Return given list as list of names."""

            return [x.get_node().get_name() for x in inlist]

        def get_outgoing_as_named_list(self):
            """Return the names of all outgoing nodes as a list."""

            return self.__as_named_list(self.__outgoing)

    def __init__(self):
        """Create a empty digraph."""
        self._named_nodes = {}

    def create_from_dict(self, init_dgraph, node_gen_func=Node):
        """Creates a new digraph based on the given information."""

        # First run: create all nodes
        for node_name in init_dgraph:
            # Create the node and put it into the object list of all
            # nodes and into the local dictionary of named nodes.
            named_node = node_gen_func(node_name)
            self.add_node(named_node)

        # Second run: run through all nodes and create the edges.
        for node_name, outs in init_dgraph.items():
            node_from = self.find(node_name)
            for onode in outs:
                node_to = self.find(onode)
                if node_to is None:
                    raise RuntimeError("Node '%s' is referenced "
                                       "but not specified" % onode)
                self.create_edge(node_from, node_to)

    def add_node(self, anode):
        """Adds a new node to the graph.

        Checks if the node with the same name already exists.
        """
        assert issubclass(anode.__class__, Digraph.Node)

        for node in self._named_nodes.values():
            if node.get_name() == anode.get_name():
                raise RuntimeError("Node with name [%s] already "
                                   "exists" % node.get_name())
        self._named_nodes[anode.get_name()] = anode

    def create_edge(self, anode, bnode, weight=0):
        """Creates an edge from a to b - both must be nodes."""

        assert issubclass(anode.__class__, Digraph.Node)
        assert issubclass(bnode.__class__, Digraph.Node)
        assert anode.get_name() in self._named_nodes.keys()
        assert anode == self._named_nodes[anode.get_name()]
        assert bnode.get_name() in self._named_nodes.keys()
        assert bnode == self._named_nodes[bnode.get_name()]
        anode.add_outgoing(bnode, weight)
        bnode.add_incoming(anode, weight)

    def get_iter_nodes_values(self):
        """Returns the nodes dict to the values.

        Note: it is not possible to change things with the help of the
        result of this function.
        """
        return iter(self._named_nodes.values())

    def find(self, name):
        """Get the node with the given name.

        Return None if not available.
        """
        if name not in self._named_nodes:
            return None

        return self._named_nodes[name]

    def as_dict(self):
        """Outputs this digraph and create a dictionary."""

        # Start with an empty dictionary
        rval = {}
        for node in self._named_nodes.values():
            rval[node.get_name()] = node.get_outgoing_as_named_list()
        return rval

    def topological_sort(self):
        """Digraph topological search.

        This algorithm is based upon a depth first search with
        'making' some special nodes.
        The result is the topological sorted list of nodes.
        """

        # List of topological sorted nodes
        tsort = []
        # List of nodes already visited.
        # (This is held here - local to the algorithm - to not modify the
        # nodes themselves.)
        visited = []

        def visit(node):
            """Recursive deep first search function."""

            if node not in visited:
                visited.append(node)
                for onode in node.get_iter_outgoing():
                    visit(onode)
                tsort.insert(0, node)

        # The 'main' function of the topological sort
        for node in self.get_iter_nodes_values():
            if node.has_incoming():
                continue
            visit(node)

        return tsort


# Utility functions

def digraph_create_from_dict(init_dgraph, node_gen_func=Digraph.Node):
    """Creates a new digraph based on the given information."""

    digraph = Digraph()
    digraph.create_from_dict(init_dgraph, node_gen_func)
    return digraph


def node_list_to_node_name_list(node_list):
    """Converts a node list into a list of the corresponding node names."""

    node_name_list = []
    for node in node_list:
        node_name_list.append(node.get_name())
    return node_name_list
