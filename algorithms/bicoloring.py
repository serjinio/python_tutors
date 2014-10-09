

import logging
from graphs import UnidirectedGraph as DA, is_bicolorable


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()
    
    test_data1 = [(0, 1), (1, 2), (2, 0)]
    test_data2 = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
                  (0, 6), (0, 7), (0, 8)]
    
    g = DA(test_data1)
    print 'Input graph: {}'.format(g)
    print 'Is bicolorable: {}'.format(is_bicolorable(g, 0))
