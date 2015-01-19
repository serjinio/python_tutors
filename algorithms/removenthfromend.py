

import logging


# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    # @return a ListNode
    def removeNthFromEnd(self, head, n):
        nodeA, nodeB, nodeB_prev = head, head, None
        offset = 0
        while nodeA is not None:
            if offset == n:
                nodeB_prev = nodeB
                nodeB = nodeB.next
            else:
                offset += 1
            nodeA = nodeA.next
        return self.removeNode(head, nodeB, nodeB_prev)

    def removeNode(self, head, node, prev_node):
        if node == head:
            head = node.next
        else:
            prev_node.next = node.next
        node.next = None
        return head


def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()
    print Solution().twoSum()
