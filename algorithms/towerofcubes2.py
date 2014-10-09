
import logging


CUBE_SIDES_NUM = 6

    
def compute_dists_matrix(cubes):
    logging.debug('computing dists matrix from input cubes:\n\t {}'
                  .format(cubes))
    
    dists = [[[1 for i in range(CUBE_SIDES_NUM)]
              for k in range(CUBE_SIDES_NUM)]
             for n in range(len(cubes))]
    side_tuples = [(s_from, s_to) for s_from in range(CUBE_SIDES_NUM)
                   for s_to in range(CUBE_SIDES_NUM)]

    for i in range(1, len(cubes)):
        logging.debug('computing distances for cube {}'
                      .format(i))
        for s_from, s_to in side_tuples:
            for k in range(i - 1, -1, -1):
                if cubes[i][s_from] != cubes[k][s_to]:
                    continue
                update_dist(cubes, dists, i, k, s_from, s_to)
            
    return dists


def update_dist(cubes, dists, cube_from, cube_to, from_side, to_side):
    dist = max_dist(dists, cube_to, to_side) + 1
    if dist > dists[cube_from][from_side][to_side]:
        dists[cube_from][from_side][to_side] = dist
        
        logging.debug(('\tmatching cubes: {}({})->{}({}). max dist: {}')
                      .format(cube_from, from_side, cube_to, to_side, dist))


def opposite_side(side):
    if side % 2 == 0:
        return side + 1
    else:
        return side - 1


def max_dist(dists, cube, bottom_side):
    return max(dists[cube][opposite_side(bottom_side)])

    
def find_longest_path(dists):
    s_from, s_to, cube = -1, -1, -1
    max_len = 0
    for i in range(len(dists)):
        for s_f in range(CUBE_SIDES_NUM):
            for s_t in range(CUBE_SIDES_NUM):
                if dists[i][s_f][s_t] > max_len:
                    max_len = dists[i][s_f][s_t]
                    s_from, s_to, cube = s_f, s_t, i

    return max_len
    

def read_input(input_lines):
    res = []
    
    for l in input_lines:
        cube = [int(el) for el in l.split(' ')]
        assert(len(cube) == 6)
        res.append(cube)
        
    return res


def dists_matrix_as_str(dists):
    res = ""
    for row in dists:
        line = ""
        for dist_vec in row:
            vec = ''
            for dist in dist_vec:
                vec += str(dist) + ','
            line += vec[:-1] + '; '
        res += line + '\n'
        
    return res
                
    
def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
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

    cubes = read_input(input_data)
    dists = compute_dists_matrix(cubes)
    print 'dists matrix: '
    print dists_matrix_as_str(dists)
    print 'longest path:', find_longest_path(dists)
