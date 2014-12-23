

import logging


def table_as_str(tbl, s_values):
    res = "\n     "
    for iq in s_values:
        res += '{:5} '.format(iq)
    res += "\n"

    n = 0
    for subtbl in tbl:
        res += "{:<4} ".format(str(n) + ":")
        n += 1

        for item in subtbl:
            res += '{:5} '.format(item)
        res += '\n'
    return res


def init_table(input_seq, s_vals, init_value=0):
    tbl = [[init_value] * len(s_vals) for i in range(len(input_seq) + 1)]
    return tbl


def find_longest_seq(input_seq):
    s_vals = [s for _, s in input_seq]
    tbl, lengths, parents = init_table(input_seq, s_vals), \
        init_table(input_seq, s_vals), init_table(input_seq, s_vals, -1)

    for length in range(len(input_seq) + 1):
        for t_idx, (w, s) in enumerate(input_seq):
            if length == 0:
                parents[length][t_idx] = -1
                continue
            elif length == 1:
                tbl[length][t_idx] = s - w
                parents[length][t_idx] = -1
                lengths[length][t_idx] = length
                continue

            parents[length][t_idx] = find_parent(length, t_idx, tbl, parents)
            if parents[length][t_idx] == -1:
                tbl[length][t_idx] = 0
                lengths[length][t_idx] = lengths[length - 1][t_idx]
                continue
            parent_capacity = tbl[length - 1][parents[length][t_idx]]
            capacity = min([parent_capacity, s])
            if capacity - w > 0:
                tbl[length][t_idx] = capacity - w
                lengths[length][t_idx] = length
            else:
                tbl[length][t_idx] = 0
                lengths[length][t_idx] = lengths[length - 1][t_idx]

    print 'capacity table: {}'.format(table_as_str(tbl, s_vals))
    print 'parents table: {}'.format(table_as_str(parents, s_vals))
    print 'lengths table: {}'.format(table_as_str(lengths, s_vals))
    return max(lengths[-1])


def find_parent(length, t_idx, capacities, parents):
    sorted_capacities = capacities[length - 1][:]
    sorted_capacities.sort()
    sorted_capacities.reverse()
    parent_idx = -1
    for c in sorted_capacities:
        parent_idx = capacities[length - 1].index(c)
        if parent_idx == t_idx:
            continue
        existing_parents = find_existing_parents(parents,
                                                 length - 1, parent_idx)
        if t_idx in existing_parents:
            continue
        else:
            return parent_idx
    return -1


def find_existing_parents(parents, length, t_idx):
    indices = []
    while parents[length][t_idx] != -1:
        indices.append(parents[length][t_idx])
        length -= 1
        t_idx = parents[length][t_idx]
    return indices


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()

    input_data = [
        (300, 1000),
        (1000, 1200),
        (200, 600),
        (100, 101)
    ]

    longest = find_longest_seq(input_data)
    print "longest sequence: {}".format(longest)
