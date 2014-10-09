

import logging
import pdb


def divide(input_list):
    """
    Divides input list of integers into two sets with 'nearly equal sums'
    a list of input integers.
    """
    target_sum = sum(input_list) / 2

    print 'will optimize sums of the input list: {}'.format(input_list)

    seq1, seq2 = optimize(input_list, target_sum)

    print 'Sums: {} and {}.'.format(sum(seq1), sum(seq2))
    return seq1, seq2


def optimize(input_list, target_sum):
    """Returns subsequence with sum, which is most close to the requested target_sum."""
    upper_bound = sum(input_list) + 1
    s = list()
    for i in range(upper_bound):
        s.append([False] * (len(input_list) + 1))
    for j in range(len(input_list) + 1):
        s[0][j] = True

    logging.info('starting solution search. input list: {}'.format(input_list))
    logging.info('target sum value: {}'.format(target_sum))

    sumvalue, elements_num = 0, 0
    for i in range(1, upper_bound):
        for j in range(1, len(input_list) + 1):
            s[i][j] = (False)
            if input_list[j - 1] <= i:
                s[i][j] = s[i][j - 1] or s[i - input_list[j - 1]][j - 1]
            else:
                s[i][j] = s[i][j - 1]

            if s[i][j]:
                logging.debug('possible sum: {} with # of elements: {}'.format(i, j))
                if abs(i - target_sum) < abs(sumvalue - target_sum):
                    sumvalue, elements_num = i, j
                    
    logging.info(('solution search finished. closest possible sum value: {}; '
                   'elements number: {}').format(sumvalue, elements_num))
    target_sequence, other_sequence = find_target_seq(input_list, s, sumvalue)
    logging.debug('elements to make this sum: {}'.format(target_sequence))
    return target_sequence, other_sequence


def find_target_seq(input_list, solution_table, target_sum):
    """Given solution table find subset of input set to realize target_sum.

    :returns: 2-tuple: (target_sequence, other_sequence)
    """
    logging.debug('looking for subset with sum {} in: {}'.format(target_sum, input_list))
    target_seq, other_seq = [], []
    indexes = []
    while target_sum > 0:
        for idx, el in enumerate(solution_table[target_sum]):
            if el is True:
                logging.debug('solution table ({}, {}) is T'.format(target_sum, idx))
                target_seq.append(input_list[idx - 1])
                indexes.append(idx - 1)
                target_sum = target_sum - input_list[idx - 1]
                break
            elif idx == len(solution_table[target_sum]) - 1:
                raise ValueError(('Cannot find subset with requested sum: '
                                  '{} in the set: {}').format(target_sum, input_list))

    for idx, el in enumerate(input_list):
        if idx in indexes:
            continue
        else:
            other_seq.append(el)
    
    return target_seq, other_seq
                                

def list_as_str(l):
    res = "   "
    for i in range(len(l[0])):
        res += ' {} '.format(i)
    res += '\n'
    
    for idx, i in enumerate(l):
        res += ' {} '.format(idx)
        for el in i:
            res += ' T ' if el else ' F '
        res += '\n'
    return res
    

def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()
    
    test_data1 = [100, 90, 200]
    test_data2 = [3, 1, 1, 2, 2, 1]
    test_data3 = [3, 1, 2, 2, 1, 1]
    test_data4 = [1, 2, 344, 5, 6, 77, 8, 6, 86, 5, 34, 3]

    divide(test_data4)
    
