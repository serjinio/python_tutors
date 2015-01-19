

import distinct_subseq_in


class Solution:
    # @return an integer
    def numDistinct(self, S, T):
        if len(S) < len(T):
            return 0
        tbl = [0] * len(T)
        for k in range(len(S)):
            prev_tbl = tbl[:]
            for i in range(len(T)):
                # print ('S[{}]={} and T[{}]={}'
                #        .format(k, S[k], i, T[i]))
                if i == 0:
                    tbl[i] += 1 if S[k] == T[i] else 0
                    continue
                if k < i:
                    continue
                if S[k] == T[i]:
                    tbl[i] += prev_tbl[i - 1]
                # print '\t pass finish, tbl:', tbl
        total_matches = tbl[len(T) - 1]
        return total_matches

    def table_as_str(self, tbl, S, T):
        res = "\n      "
        for ch in S:
            res += '{:3} '.format(ch)
        res += "\n"
        n = 0
        for subtbl in tbl:
            res += "{:<2}: ".format(T[n])
            n += 1
            for item in subtbl:
                res += '{:3} '.format(item)
            res += '\n'
        return res


if __name__ == '__main__':
    print 'should be 3:', Solution().numDistinct('rabbbit', 'rabbit')
    print 'should be 5:', Solution().numDistinct('babgbag', 'bag')
    # assert(Solution().numDistinct('babgbag', 'bag') == 5)
    # Solution().numDistinct(distinct_subseq_in.input_string,
    #                        distinct_subseq_in.input_template)
