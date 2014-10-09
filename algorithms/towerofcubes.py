
import logging
import graphs


def build_graph(cubes):
    logging.debug('building cubes graph from input of length: {}'
                  .format(len(cubes)))
    g = graphs.DirectedGraph()
    
    for i_idx, i_cube in enumerate(cubes):
        for k_idx in range(i_idx + 1, len(cubes)):
            k_cube = cubes[k_idx]
            logging.debug('i_cube: {}; k_cube: {}'.format(i_cube, k_cube))
            for i_cube_side_idx, i_cube_side in enumerate(i_cube):
                if i_cube_side not in k_cube:
                    continue
                    
                k_cube_side_idx = k_cube.index(i_cube_side)
                    
                logging.debug('\t adding edge: {} =side:{}=> {}'
                              .format(i_idx + 1, i_cube_side_idx + 1,
                                      k_idx + 1))
                g.add_edge((i_idx + 1, k_idx + 1),
                           (i_cube_side_idx + 1, k_cube_side_idx + 1))
    
    return g

    
def find_longest_cube_path_in_DAG(graph):
    logging.info(('Will try to find longest path for a graph '
                  'of {} nodes').format(len(graph)))
    longest_path = []
    
    for starting_node in range(1, len(graph) + 1):
        path = find_longest_cube_path(graph, starting_node)
        logging.info('longest path from node {}: {}'
                     .format(starting_node, path))
        if len(path) > len(longest_path):
            longest_path = path
    
    return longest_path


def find_longest_cube_path(graph, starting_node):
    logging.debug(('will search for a longest path in the graph using {} as a '
                   'starting node').format(starting_node))
    paths = []
    connecting_edges = []
    
    for base_cube_side in range(1, 7):
        logging.debug(('searching for the longest path using {} as base '
                       'cube top side').format(base_cube_side))
        distances = [0] * (len(graph) + 1)
        for i in range(starting_node):
            distances[i] = None
        parents = {}
        edges = {}
        
        for n in range(starting_node, len(graph) + 1):
            logging.debug('\tnode {}'.format(n))
            valid_edges = None
            
            if n == starting_node:
                valid_edges = [e for e in graph.node_edges(n)
                               if e.name[0] == base_cube_side]
            else:
                if edges.get(n) is None:
                    logging.debug(('cube {} has been skipped as no incident '
                                   'edges was found for it.').format(n))
                    continue
                    
                edge_to_n = edges[n]
                n_bottom_side = edge_to_n.name[1]
                n_top_side = n_bottom_side - 1 if n_bottom_side % 2 == 0 \
                    else n_bottom_side + 1
                valid_edges = [e for e in graph.node_edges(n)
                               if e.name[0] == n_top_side]

            logging.debug('\t\tusing edges:\n\t\t\t {}'
                          .format([str(e) for e in valid_edges]))
            for edge in valid_edges:
                if distances[edge.to] < distances[n] + 1:
                    distances[edge.to] = distances[n] + 1
                    parents[edge.to] = n
                    edges[edge.to] = edge

            logging.debug('\tafter node {} distances: {}'.format(n, distances))
            logging.debug('\tafter node {} parent edges: {}'.
                          format(n, [str(edges[e]) for e in edges]))

        logging.debug(('finished search of a longest path with base cube '
                       'top side: {}').format(base_cube_side))
        logging.debug('distances: {}'.format(distances))
        logging.debug('parents: {}'.format(parents))
        paths.append(construct_path(parents, distances))
        connecting_edges.append(edges)
        
    logging.debug('searching for the longest path in the results:\n\t {}'
                  .format(paths))
    longest_path = []
    longest_path_cons = []
    for p, cons in zip(paths, connecting_edges):
        if len(longest_path) < len(p):
            longest_path = p
            longest_path_cons = cons

    logging.debug('connection edges for the longest path:\n\t {}'
                  .format([str(longest_path_cons[e])
                           for e in longest_path_cons]))
    return longest_path
    

def construct_path(parents, distances):
    path = []
    path_end_node = distances.index(max(distances))
    path_parent_node = parents.get(path_end_node)
    if path_parent_node is not None:
        path.append(path_end_node)
        while path_parent_node is not None:
            path.append(path_parent_node)
            path_parent_node = parents.get(path_parent_node)
            
    path.reverse()
    return path


def read_input(input_lines):
    res = []
    for l in input_lines:
        cube = [int(el) for el in l.split(' ')]
        assert(len(cube) == 6)
        res.append(cube)
        
    return res


def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s:  %(message)s')

    
if __name__ == '__main__':
    configure_logging()
    
    input_data = [
        '1 2 2 2 1 2',
        '3 3 3 3 3 3',
        '3 2 1 1 1 1'
    ]

    input_data2 = [
        '1 5 10 3 6 5',
        '2 6 7 3 6 9',
        '5 7 3 2 1 9',
        '1 3 3 5 8 10',
        '6 6 2 2 4 4',
        '1 2 3 4 5 6',
        '10 9 8 7 6 5',
        '6 1 2 3 4 7',
        '1 2 3 3 2 1',
        '3 2 1 1 2 3'
    ]

    cubes = read_input(input_data2)
    cubes.reverse()
    g = build_graph(cubes)
    logging.debug('resulting graph:\n {}'.format(g))
    path = find_longest_cube_path_in_DAG(g)
    print 'Longest path from cubes (heaviest to lightest):\n\t {}' \
        .format(path)
    print 'Path length: {}'.format(len(path))
