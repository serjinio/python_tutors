

import logging


class Solution:
    # @param A, a list of integers
    # @param target, an integer to be searched
    # @return a list of length 2, [index1, index2]
    def searchRange(self, A, target):
        start_idx = self.binarySearch(A, target)
        if start_idx == -1:
            return [-1, -1]
        idx = start_idx
        while A[idx] == target and idx < len(A) - 1:
            idx += 1
        if A[idx] != target:
            idx -= 1
        return [start_idx, idx]

    def binarySearch(self, arr, value):
        # logging.debug('in binary search')
        low_idx, high_idx = 0, len(arr) - 1
        idx = (high_idx - low_idx) / 2
        while high_idx - low_idx > 1:
            # logging.debug('low_idx: {}; high_idx: {}'
            #               .format(low_idx, high_idx))
            if arr[idx] == value:
                while arr[idx] == value and idx > 0:
                    idx -= 1
                if arr[idx] != value:
                    idx += 1
                return ++idx
            elif arr[idx] > value:
                    high_idx = idx
            elif arr[idx] < value:
                    low_idx = idx
            idx = low_idx + (high_idx - low_idx) / 2
        # logging.debug('looking in last two items: [{}:{}]'
        #               .format(low_idx, high_idx))
        if arr[low_idx] == value:
            return low_idx
        elif arr[high_idx] == value:
            return high_idx
        else:
            return -1


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')
    # print Solution().searchRange([5, 7, 7, 8, 8, 10], 8)
    # print Solution().searchRange([1, 2, 3], 3)
    print Solution().searchRange([1, 2, 3], 2)


if __name__ == '__main__':
    configure_logging()
