
import twosumin
import logging


class Solution:

    # @return a tuple, (index1, index2)
    def twoSum(self, num, target):
        tbl = [{}, {}]
        for idx, n in enumerate(num):
            tbl[0][n] = idx
        for idx2, num2 in enumerate(num):
            if tbl[0].get(target - num2):
                idx1 = tbl[0][target - num2]
                return (min(idx1, idx2) + 1, max(idx1, idx2) + 1)
        return None


def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()
    print Solution().twoSum(twosumin.nums, twosumin.target_sum)
