
import pdb
import sys
import logging


MATCH = 1
INSERT = 2
DELETE = 3

recursion_level = 0
def string_compare(template, text):
    global recursion_level
    recursion_level += 1

    if len(template) == 0:
        return len(text) * insdel_cost(' ')
    elif len(text) == 0:
        return len(template) * insdel_cost(' ')
    
    # logging.debug('comparing "{}" and "{}"'.format(template, text))
    
    opt = {}

   #logging.debug('will do "MATCH" comparison')
    opt[MATCH] = string_compare(template[:-1], text[:-1]) + \
        match_cost(template[-1], text[-1])
    #logging.debug('will do "INSERT" comparison')
    opt[INSERT] = string_compare(template, text[:-1]) + \
        insdel_cost(template[-1])
    #logging.debug('will do "DELETE" comparison')
    opt[DELETE] = string_compare(template[:-1], text) + \
        insdel_cost(text[-1])

    return min(opt.values())


def insdel_cost(char):
    return 1

    
def match_cost(char1, char2):
    if char1 == char2:
        return 0
    else:
        return 1

    
def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()

    global recursion_level
    
    template = 'y'
    text = 'y'
    print 'cost of edit:', string_compare(template, text)
    print 'number of iterations:', recursion_level
