# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None


class Solution:
    # @param head, a ListNode
    # @return a list node
    def detectCycle(self, head):
        if not self.hasCycle(head):
            return None
        node = head
        nodes = set()
        while node is not None:
            if node in nodes:
                return node
            nodes.add(node)
            node = node.next

    def hasCycle(self, head):
        nodeA = head
        nodeB = head
        while nodeB is not None:
            nodeA, nodeB = nodeA.next, nodeB.next
            if nodeB is not None:
                nodeB = nodeB.next
            else:
                break
            if nodeA == nodeB:
                return True
        return False
