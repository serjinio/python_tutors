

import logging
import graphs


def max_capacity_path(graph, start_node, dest_node):
    paths, bfs_parents, capacities = {}, {}, {}
    visited, nodes_queue = set(), []
    
    capacities[start_node] = None
    paths[start_node] = None
    nodes_queue.append(start_node)

    node, max_capacity = None, 0
    while len(nodes_queue) > 0:
        node = nodes_queue.pop(0)
        logging.debug('Staring node processing: {}.'.format(node))
        if node in visited:
            continue
        else:
            visited.add(node)

        logging.debug('Processing node edges:')
        for edge in graph.node_edges(node):
            logging.debug('\t edge to {}.'.format(edge.to))
            if edge.to == bfs_parents.get(node):
                logging.debug('\t backwards edge, skipping.')
                continue
                
            if capacities.get(edge.to) is None:
                capacities[edge.to] = 0            
            edge_capacity = min([edge.weight, capacities[node]])
            if capacities[node] == None:
                edge_capacity = edge.weight
            
            if edge_capacity > capacities[edge.to]:
                paths[edge.to] = node
                capacities[edge.to] = edge.weight
                
            logging.debug('\t capacities: {}'.format(capacities))
            logging.debug('\t bfs_parents: {}'.format(bfs_parents))
            
            if edge.to == dest_node:
                continue
            if edge.to not in nodes_queue:
                nodes_queue.append(edge.to)
                if not bfs_parents.get(edge.to):
                    bfs_parents[edge.to] = node
                
    return _find_path(paths, start_node, dest_node)
    

def _find_path(path_matrix, start_node, dest_node):
    logging.debug(('Looking for a path between nodes {} and {}. '
                  'Using path matrix: {}').format(start_node, dest_node, path_matrix))
    
    path = []
    node = dest_node
    while node != None:
        path.append(node)
        node = path_matrix[node]
        if len(path) > len(path_matrix):
            raise ValueError(('Path from node {} to {} contains cycles, '
                              'invalid path matrix provided.')
                             .format(start_node, dest_node))
    
    return reversed(path)


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')

    
if __name__ == '__main__':
    configure_logging()
    
    test_data1 = [
        (1, 2, 30),
        (1, 3, 15),
        (1, 4, 10),
        (2, 4, 25),
        (2, 5, 60),
        (3, 4, 40),
        (3, 6, 26),
        (4, 7, 25),
        (5, 7, 20),
        (6, 7, 30)
    ]

    g = graphs.UnidirectedGraph(test_data1)
    print ('Max capacity path in a graph: {}') \
        .format([el for el in max_capacity_path(g, 1, 7)])
        
