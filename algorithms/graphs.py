

import logging
from Queue import Queue


class Edge(object):

    def __init__(self, to_node, weight=1, name=None):
        self.to = to_node
        self.weight = weight
        self.name = name

    def __hash__(self):
        return hash(self.to)

    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        weight_and_nodes = self.to == other.to and self.weight == other.weight
        name_equals = True
        if self.name is not None:
            name_equals = self.name == other.name
            
        return weight_and_nodes and name_equals

    def __lt__(self, other):
        if not isinstance(other, Edge):
            return False

        return self.to == other.to and self.weight < other.weight

    def __str__(self):
        edge_spec = "id:" + str(self.name) if self.name is not None else ""
        edge_spec += ';w:' + str(self.weight) if self.weight != 1 else ""
        return "={}=>{}".format(edge_spec, self.to)


class UnidirectedGraph(object):

    def __init__(self, edges=None):
        logging.debug(('Constructing graph with input edges '
                       'list: "{}".').format(edges))
        self._edges = {}
        
        if edges is not None:
            for e in edges:
                self.add_edge(e)
                
    def add_node(self, node_id):
        """Adds new node into the graph.

        :param node_id: Integer ID of a new node to add. If not an int has been
          provided, then the method will throw ValueError.
        :returns: self for chained calls
        """
        if type(node_id) is not int:
            raise ValueError(('Node ID must be an int, but have been '
                             'provided: "{}".').format(node_id))
        if node_id not in self._edges:
            self._edges[node_id] = set()

        return self

    def add_edge(self, edge, name=None):
        """Adds new connection between graph nodes.

        If nodes did not exist in the graph will add nodes at first.

        :param edge: 2-tuple containing integer IDs of nodes a given edge
          connects or 3-tuple which additionally to 2-tuple contains edge weight.
        :param weight: Edge weight, 1 by default.
        :returns: self for chained calls
        """
        if len(edge) != 2 and len(edge) != 3:
            raise ValueError(('Edge should be provided as a 2- or 3-tuple '
                              'of ints, instead got: "{}".')
                             .format(edge))

        endpoint1, endpoint2 = edge[:2]
        weight = 1 if len(edge) == 2 else edge[2]

        self.add_node(endpoint1).add_node(endpoint2)
        self._edges[endpoint1].add(Edge(endpoint2, weight, name))
        self._edges[endpoint2].add(Edge(endpoint1, weight, name))

        return self

    def remove_edge(self, edge):
        if len(edge) != 2:
            raise ValueError(('Edge should be provided as a 2-tuple of ints '
                              'instead got: "{}".').format(edge))

        self._remove_directed_edge(edge)
        self._remove_directed_edge((edge[1], edge[0]))

    def _remove_directed_edge(self, edge):
        node_edges = self._edges.get(edge(0))
        if not node_edges:
            raise ValueError(('Was not able to locate edges for a node {} '
                              'in the graph.').format(edge(0)))

        dest_nodes = [e.to for e in node_edges]
        if edge[1] not in dest_nodes:
            raise ValueError(('The edge to node {} is not in the node\'s '
                              '{} edges list. Cannot remove non existing edge!')
                             .format(edge[0], edge[1]))

        self._edges[edge[0]] = node_edges - \
                               set([e for e in node_edges if e.to == edge[1]])

    def nodes(self):
        return self._edges.keys()

    def node_edges(self, node_id):
        """
        Returns all connections of a given node or None if a given node
        does not exists.
        """
        return self._edges.get(node_id)

    def bfs(self, start_node):
        if start_node not in self:
            raise ValueError(('Start node specified: "{}" should '
                              'be in graph!').format(start_node))
        yielded = set()
        nodes_queue = []
        nodes_queue.append(start_node)

        while len(nodes_queue) > 0:
            node = nodes_queue.pop(0)
            if node in yielded:
                continue
            for edge in self.node_edges(node):
                if edge.to not in nodes_queue:
                    nodes_queue.append(edge.to)

            yield node
            yielded.add(node)

    def __str__(self):
        res = ('Nodes #: {}. Edges list:\n') \
            .format(len(self._edges))

        for key in self._edges:
            res += '{}: '.format(key)
            for endpoint in self._edges[key]:
                res += str(endpoint) + ' '
            res += '\n'

        return res

    def __iter__(self):
        for s in self._edges:
            yield s

    def __len__(self):
        return len(self._edges)

    def __contains__(self, node):
        return node in self._edges


class DirectedGraph(UnidirectedGraph):

    def __init__(self, edges=None):
        super(DirectedGraph, self).__init__(edges)

    def add_edge(self, edge, name=None):
        if len(edge) != 2 and len(edge) != 3:
            raise ValueError(('Edge should be provided as a 2- or 3-tuple '
                              'of ints, instead got: "{}".')
                             .format(edge))

        endpoint1, endpoint2 = edge[:2]
        weight = 1 if len(edge) == 2 else edge[2]
        
        self.add_node(endpoint1).add_node(endpoint2)
        self._edges[endpoint1].add(Edge(endpoint2, weight, name))
        
        return self

    def remove_edge(self, edge):
        if len(edge) != 2:
            raise ValueError(('Edge should be provided as a 2-tuple of ints '
                              'instead got: "{}".').format(edge))

        self._remove_directed_edge(edge)

        

###########################
# Some algorithms on graphs
###########################


def is_bicolorable(graph, start_node):
    """Determines if it is possible to two-color a given graph.

    Function tries to color the graph using two colors, so that no
    two adjacent nodes are of the same colors.

    :param graph: a graph to color.
    :param start_node: start node.
    :returns: True or False depending on if the graph is bicolorable.
    :rtype: bool
    """
    logging.debug("Checking bicoloring of a graph: {}".format(graph))
    color_map = {}

    next_color = 'B'
    for node in graph.bfs(start_node):
        red_adjacent, black_adjacent = False, False
        for edge in graph.node_edges(node):
            if color_map.get(edge.to) == 'R':
                red_adjacent = True
            elif color_map.get(edge.to) == 'B':
                black_adjacent = True

        if red_adjacent and black_adjacent:
            # In this case the graph is not bicolorable
            logging.debug('Graph found to be not bicolorable!')
            return False
        elif red_adjacent:
            color_map[node] = 'B'
        elif black_adjacent:
            color_map[node] = 'R'
        else:
            color_map[node] = next_color
            next_color = 'R' if next_color == 'B' else 'B'
            
        logging.debug('Node "{}" will be colored "{}".'
                      .format(node, color_map[node]))
        
    return True



