

import sys

import logging

    
def find_best_stops(dests, total_floors, max_stops):
    costs = _prepare_costs_mtx(total_floors, max_stops)
    logging.debug(costs)
    
    for f in range(0, total_floors):
        for s in range(0, max_stops):
            
    
    return []


def _prepare_costs_mtx(total_floors, max_stops):
    eff_stops = max_stops + 1
    costs = [[0] * eff_stops for i in range(0, total_floors)]
    costs[0] = [sys.maxint for i in range(0, eff_stops)]
    
    for i in range(0, total_floors):
        costs[i][0] = sys.maxint

    return costs


def _configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    _configure_logging()

    N = 5
    dests = [1, 3, 4]
    k = 3

    print find_best_stops(dests, N, k)
    
