
import logging
import graphs


def build_graph(beads):
    g = graphs.UnidirectedGraph()
    adj_mtx = [[0] * len(beads) for i in range(len(beads))]

    for b_idx, b in enumerate(beads):
        logging.debug('looking for links of {}'.format(b))
        for b2_idx, b2 in enumerate(beads):
            if b_idx == b2_idx:
                continue
            elif adj_mtx[b_idx][b2_idx] != 0:
                continue

            if any([True for color1 in b for color2 in b2
                    if color1 == color2]):
                logging.debug('\tfound a link with {}'.format(b2))
                adj_mtx[b_idx][b2_idx] = 1
                adj_mtx[b2_idx][b_idx] = 1
                g.add_edge((b_idx, b2_idx))

    return g


def graph_mtx_as_str(mtx):
    res = ""
    for row in mtx:
        line = ""
        for el in row:
            line += str(el) + ';'
        res += line[:-1] + '\n'

    return res

    
def find_longest_cycle(graph):
    logging.debug('in find cycle on graph:\n{}'.format(graph))
    if len(graph) == 0:
        return 0

    start_node = graph.nodes()[0]
    node = start_node
    visited = set()
    nodes_stack = [start_node]
    
    logging.debug('Looking for a cycle starting from node: {}'.
                  format(start_node))
    while len(nodes_stack) != 0:
        node = nodes_stack.pop()
        logging.debug('node: {}'.format(node))

        if node == start_node and len(visited) > 0:
            logging.debug('\tFound a cycle ending at a start node!')
            logging.debug([str(el) for el in visited])
            if len(visited) == len(graph):
                break
        # if node in visited:
        #    continue

        visited.add(node)

        # if len(visited) == len(graph):
        #    break

        for e in graph.node_edges(node):
            # if e.to not in visited:
            nodes_stack.append(e.to)


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()

    test_data1 = [
        (2, 1),
        (2, 2),
        (3, 4),
        (3, 1),
        (2, 4)
    ]

    g = build_graph(test_data1)
    print g
    find_longest_cycle(g)
