

import logging
import pdb


class Network(object):

    def __init__(self, station_connections):
        self._connections = {}
        for conn in station_connections:
            self.add_connection(conn)

    def add_node(self, node_id):
        if type(node_id) is not int:
            raise ValueError(('Station ID must be an int, but have been '
                             'provided: "{}".').format(node_id))
        if node_id not in self._connections:
            self._connections[node_id] = set()

        return self

    def add_connection(self, connection):
        if len(connection) != 2:
            raise ValueError(('Connection should be provided as a pair '
                              'of ints, instead got: "{}".')
                             .format(connection))

        endpoint1, endpoint2 = connection
        self.add_node(endpoint1).add_node(endpoint2)
        self._connections[endpoint1].add(endpoint2)
        self._connections[endpoint2].add(endpoint1)

        return self

    def connections(self, node_id):
        return self._connections.get(node_id)

    def __str__(self):
        res = ('Number of nodes: {}. Connections:\n') \
            .format(len(self._connections))

        for key in self._connections:
            res += '{} <=> '.format(key)
            for endpoint in self._connections[key]:
                res += ' ' + str(endpoint) + ','
            res += '\n'

        return res

    def __iter__(self):
        for s in self._connections:
            yield s

    def __len__(self):
        return len(self._connections)

    def __contains__(self, node):
        return node in self._connections


def read_input(input):
    lines = input.split('\n')[1:-1]
    out = []

    for l in lines:
        tokens = l.split(' ')
        if len(tokens) != 2:
            raise ValueError('Invalid edge information - should '
                             'be a pair of integers.')
        out.append((int(tokens[0]), int(tokens[1])))

    return out


def find_mds(stations_network):
    print 'Starting search for MDS on the network: '
    print stations_network
    
    mds = _lookup_mds(stations_network, set(), set())
    
    print 'MDS:', mds
    print 'Length:', len(mds) if mds else 0
    print 'Finished.'


def _lookup_mds(network, mds_set, covered_set):
    """Recursive function to find MDS of a given graph.
    :type network: Network
    :type mds_set: set
    :returns: A set of nodes of the network forming MDS
    :rtype : set
    """
    logging.debug(('MDS lookup iteration. Partial MDS '
                   'set length: {}').format(len(mds_set)))
    logging.debug('current mds set: "{}"'.format(mds_set))
    logging.debug('current covered set: "{}"'.format(covered_set))
    
    if _is_ds(network, mds_set):
        return mds_set
        
    most_connected_node = _find_most_connected_node(network, covered_set)
    mds_set.add(most_connected_node)
    new_covered_set = covered_set | set([most_connected_node]) | \
        network.connections(most_connected_node)

    return _lookup_mds(network, mds_set, new_covered_set)
    

def _find_most_connected_node(network, excluded_set):
    logging.debug(('looking for the most connected node '
                  'with excluded set: {}').format(excluded_set))
    most_connected_node = None
    max_connections = 0

    for s in network:
        not_covered_connections = network.connections(s) - excluded_set
        if len(not_covered_connections) > max_connections:
            max_connections = len(not_covered_connections)
            most_connected_node = s

    logging.debug('most connected node: {}'.format(most_connected_node))
    return most_connected_node
    

def _is_ds(network, ds_set):
    covered_nodes = set()
    for node in ds_set:
        covered_nodes = covered_nodes | network.connections(node) | set([node])

    if len(covered_nodes) == len(network):
        return True
    else:
        return False
    
    
def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')



if __name__ == '__main__':
    configure_logging()
    
    sample_input = """8 12
1 2
1 6
1 8
2 3
2 6
3 4
3 5
4 5
4 7
5 6
6 7
6 8
0 0"""

    network = Network(read_input(sample_input))
    # print _is_ds(network, network._connections.keys())
    find_mds(network)
