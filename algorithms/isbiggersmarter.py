

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


def find_longest_seq(input_seq):
    """Find longest subsequence of input items satisfying  the requirements."""
    by_weights, by_s_vals = _prepare_input_seq(input_seq)
    s_vals = [item[1] for item in by_s_vals]
    tbl = init_table(by_weights, s_vals)
    parents = init_table(by_weights, s_vals)
    logging.debug('memoization table: {}'.format(table_as_str(tbl, s_vals)))

    logging.debug('starting search of a longest sequence...')
    for idx1, el1 in enumerate(by_weights):
        n_elephs = idx1 + 1
        w1, s1 = el1

        logging.debug('\t considering sequence of {} elephants'
                      .format(n_elephs))
        for idx2, el2 in enumerate(by_s_vals):
            w2, s2 = el2
            if n_elephs == 1:
                parents[n_elephs][idx2] = -1
                tbl[n_elephs][idx2] = 1
                continue

            logging.debug('\t\t weight: {}; iq: {}'.format(w2, s2))

            thresh_w, thresh_s = by_s_vals[idx2]
            biggest_len, biggest_len_idx = _find_best_parent(
                tbl[n_elephs - 1], by_s_vals, thresh_s, thresh_w)
            if biggest_len != -1:
                tbl[n_elephs][idx2] = biggest_len + 1
                parents[n_elephs][idx2] = biggest_len_idx
            else:
                tbl[n_elephs][idx2] = tbl[n_elephs - 1][idx2]
                parents[n_elephs][idx2] = parents[n_elephs - 1][idx2]

    logging.debug('table after search: {}'.format(table_as_str(tbl, s_vals)))
    logging.debug('parents map: {}'.format(table_as_str(parents, s_vals)))

    path = _reconstruct_path(tbl, parents)
    path.reverse()
    return [by_s_vals[i] for i in path]


def init_table(input_seq, s_vals):
    tbl = [[0] * len(s_vals) for i in range(len(input_seq) + 1)]
    return tbl


def _find_best_parent(tbl, input_seq, thresh_iq, thresh_w):
    """Finds best parent in the memoization table given thresh
    hold values."""
    logging.debug(('looking for best parent element using '
                   'criteria: iq < {}; weight > {}')
                  .format(thresh_iq, thresh_w))
    indexes = [idx for idx, item in enumerate(input_seq)
               if item[1] < thresh_iq if item[0] > thresh_w]
    lengths = [tbl[idx] for idx in indexes] + [-1]
    logging.debug('best parent sequences found: {}'.format(lengths))

    longest, longest_idx = -1, -1
    for idx, ln in enumerate(lengths):
        if ln > longest:
            longest, longest_idx = ln, indexes[idx]

    return longest, longest_idx


def _prepare_input_seq(input_seq):
    by_weights, by_iqs = input_seq[:], input_seq[:]
    by_weights.sort(key=lambda item: item[0])
    by_weights.reverse()
    by_iqs.sort(key=lambda item: item[1])
    return by_weights, by_iqs


def _reconstruct_path(tbl, parents):
    logging.debug('reconstructing path from memoize table...')
    max_idx, max_row_idx, max_value = -1, -1, -1
    row_idx = len(tbl) - 1
    while row_idx > 1:
        for idx, item in enumerate(tbl[row_idx]):
            if item > max_value:
                max_value = item
                max_idx = idx
                max_row_idx = row_idx
        row_idx -= 1
    logging.debug('found maximum path length of {} at row: {} and index: {}'
                  .format(max_value, max_row_idx, max_idx))
    if max_value < 1:
        return []

    return _concat_path(max_idx, parents, max_row_idx)


def _concat_path(idx, parents, row_idx):
    parent_idx = parents[row_idx][idx]
    if row_idx == 1 or parent_idx == -1:
        return [idx]

    logging.debug('parent of {} is {}'.format(idx, parent_idx))
    return [idx] + _concat_path(parent_idx, parents, row_idx - 1)


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()

    elephants = [
        (6008, 1300),
        (6000, 2100),
        (500, 2000),
        (1000, 4000),
        (1100, 3000),
        (6000, 2000),
        (8000, 1400),
        (6000, 1200),
        (2000, 1900)
    ]

    elephants.sort(key=lambda el: el[0])
    elephs = find_longest_seq(elephants)
    print 'resulting longest subsequence:'
    for e in elephs:
        print e
