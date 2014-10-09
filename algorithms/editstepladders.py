

import logging
import graphs

import cProfile


def find_longest_edit_path_in_UAG(graph):
    logging.info(('Will try to find longest path for a graph '
                  'of {} nodes').format(len(graph)))
    visited = set()
    nodes_queue = []
    lengths = {}
    for n in graph:
        lengths[n] = (0, 0)

    for n in graph:
        if len(graph.node_edges(n)) == 1:
            nodes_queue.append(n)

    logging.debug('computing distances:')
    while len(nodes_queue) > 0:
        node = nodes_queue.pop()
        visited.add(node)
        
        logging.debug('\t node {}'.format(node))

        logging.debug('\t processing node edges:')
        for edge in graph.node_edges(node):
            logging.debug('\t\t edge to: {}'.format(edge.to))
            if edge.to in visited:
                logging.debug('\t\t already visited, skipping')
                continue

            local_lengths = list(lengths[edge.to] + (lengths[node][0] + 1,))
            local_lengths.sort(reverse=True)
            logging.debug('local_lengths: {}'.format(local_lengths[:2]))
            lengths[edge.to] = tuple(local_lengths[:2])
            logging.debug('\t\t updated node {} lengths: {}'
                          .format(edge.to, lengths[edge.to]))

        for n in graph:
            if n not in visited and n not in nodes_queue:
                test = [e.to for e in graph.node_edges(n) if e.to in visited]
                if len(test) > 0:
                    nodes_queue.append(n)

    res = max([sum(lengths[l]) for l in lengths])
    logging.info('longest path length in the graph: {}'.format(res))
    return res


def find_longest_edit_path_in_DAG(graph):
    logging.info(('Will try to find longest path for a graph '
                  'of {} nodes').format(len(graph)))
    distances = [0] * len(graph)

    for n in range(len(graph)):
        for edge in graph.node_edges(n):
            if distances[edge.to] < distances[n] + 1:
                distances[edge.to] = distances[n] + 1

    return max(distances)

    
def build_graph(input_dictionary):
    logging.debug(('will build edits graph on the input dictionary '
                   'of length {}').format(len(input_dictionary)))
    len_input = len(input_dictionary)
    edits_matrix = []
    edits_graph = graphs.DirectedGraph()
    for i in xrange(len_input):
        edits_matrix.append([None] * len_input)
        
    for idx1, w1 in enumerate(input_dictionary):
        edits_graph.add_node(idx1)
        for idx2 in xrange(idx1 + 1, len(input_dictionary)):
            w2 = input_dictionary[idx2]
            if idx1 == idx2:
                edits_matrix[idx1][idx2] = False
            elif edits_matrix[idx1][idx2] is None:
                if has_edit_step(w1, w2):
                    edits_matrix[idx1][idx2] = True
                    edits_matrix[idx2][idx1] = True
                    edits_graph.add_edge((idx1, idx2))
                else:
                    edits_matrix[idx1][idx2] = False
                    edits_matrix[idx1][idx2] = False

    return edits_graph


def has_edit_step(word1, word2):
    len_word1, len_word2 = len(word1), len(word2)
    if len_word1 < len_word2:
        word1, word2 = word2, word1
        len_word1, len_word2 = len_word2, len_word1
        
    if len_word1 == len_word2:
        test = [True for ch1, ch2 in zip(word1, word2) if ch1 != ch2]
        if len(test) == 1:
            return True
    elif len_word1 > len_word2:
        test = 1
        idx1 = 0
        for ch2 in word2:
            if ch2 != word1[idx1]:
                test += 1
                continue
            idx1 += 1
            
        if test == 1:
            return True
    else:
        assert(False, 'should be unereachable')

    return False


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')

    
if __name__ == '__main__':
    configure_logging()
    
    test_data1 = [
        'cat',
        'dig',
        'dog',
        'fig',
        'fin',
        'fine',
        'fog',
        'log',
        'wine'
    ]

    logging.info('searching dictionary for edit steps:')
    input_data = test_data1 * 150
    edits_graph = None
    # edits_graph = build_graph(input_data)
    cProfile.run('edits_graph = build_graph(input_data)')
    # print edits_graph
    
    print 'Longest edit path is: {}' \
        .format(find_longest_edit_path_in_DAG(edits_graph))
