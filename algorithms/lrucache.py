

import logging


class LRUCache:

    class Node:

        def __init__(self, key, data, next=None, prev=None):
            self.key = key
            self.data = data
            self.next = next
            self.prev = prev

        def __str__(self):
            return 'k: {}; v: {}'.format(self.key, self.data)

        def __repr__(self):
            return 'Node({}, {})'.format(repr(self.key), repr(self.data))

    # @param capacity, an integer
    def __init__(self, capacity):
        self.capacity = capacity
        self.size = 0
        self.head = None
        self.tail = None
        self.dic = {}

    # @return an integer
    def get(self, key):
        if self.dic.get(key):
            item = self.dic[key]
        else:
            return -1
        value = item.data
        self._push_to_top(item)
        return value

    # @param key, an integer
    # @param value, an integer
    # @return nothing
    def set(self, key, value):
        if self.dic.get(key):
            new_node = self.dic[key]
            new_node.data = value
            self.get(key)
        else:
            new_node = LRUCache.Node(key, value, self.head)
            if self.size == 0:
                self.head = new_node
                self.tail = new_node
            else:
                self.head.prev = new_node
                self.head = new_node
            self.dic[key] = new_node
            self.size += 1
            self._adjust_size()

    def _adjust_size(self):
        while self.size > self.capacity:
            del self.dic[self.tail.key]
            one_to_last = self.tail.prev
            one_to_last.next = Noneema
            self.tail = one_to_last
            self.size -= 1

    def _push_to_top(self, node):
        if node is self.head:
            return
        prev_node = node.prev
        next_node = node.next
        if prev_node is not None and next_node is not None:
            prev_node.next = next_node
            next_node.prev = prev_node
        elif prev_node is not None and next_node is None:
            prev_node.next = None
            self.tail = prev_node
        node.prev = None
        node.next = self.head
        self.head.prev = node
        self.head = node

    def __str__(self):
        node = self.head
        res = 'LRUCache contents:\n'
        while node is not None:
            res += '\tkey: {}; value: {}\n'.format(node.key, node.data)
            node = node.next
        res += '\n\tDict: {}'.format(self.dic)
        return res


def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()
    cache = LRUCache(3)
    cache.set('k1', 1)
    cache.set('k2', 2)
    cache.set('k3', 3)
    print 'getting k1:', cache.get('k1')
    print cache
    print 'getting k2:', cache.get('k2')
    print cache
    print 'getting k3:', cache.get('k3')
    print cache
    print 'setting one above capcacity'
    cache.set('k4', 4)
    print 'getting k1:', cache.get('k1')
    print cache

    print 'getting k8:', cache.get('k8')

    cache = LRUCache(1101)
    cache.set(253, 668)
    cache.set(202, 206)
    cache.set(1231, 3177)
    print 'getting 465:', cache.get(465)

    print 'test scenario:'
    cache = LRUCache(2)
    cache.set(2, 1)
    cache.set(2, 2)
    print cache
    print 'get(2):', cache.get(2)
    cache.set(1, 1)
    cache.set(4, 1)
    print cache
    print 'get(2):', cache.get(2)
