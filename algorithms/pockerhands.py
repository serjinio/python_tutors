
import fileinput
import pdb


MIN_VALUE = 2
MAX_VALUE = 14


def readin_line(line):
    cards = []
    for token in line.split(" "):
        cards.append((get_int_value(token[0]), token[1]))
    return cards

    
def get_int_value(val):
    values = "23456789TJQKA"
    return values.index(val) + 2

    
def get_with_same_suite(cards):
    suites = reduce(lambda acc, el: acc + el[1], cards, "")
    return max(suites.count(s) for s in "CDHS")

    
def fp_get_value_counts(cards):
    stats = CardsStats(cards)
    counts = stats.get_value_counts()
    return counts


class CardsStats(object):
    
    def __init__(self, cards):
        self.cards = cards
    
    def get_value_counts(self):
        """Returns list of 2-tuples: (value, count)."""
        vals = [(val, self._get_value_count(val)) for val in
                xrange(MIN_VALUE, MAX_VALUE)]
        return dict(el for el in vals if el[1] > 0)
        
    def _get_value_count(self, value):
        """Returns count of card with the given value."""
        return len([c for c in cards if c[0] == value])


def get_value_counts(cards):
    values, suites = zip(*cards)
    return [(v, values.count(v)) for v in values]

    
def cards_hash(cards):
    return reduce(lambda acc, el: acc + 4 ** (el[0] - 2), cards, 0) + \
        get_bonus_points(cards)

    
def get_bonus_points(cards):
    base_power = 13
    num_with_same_suite = get_with_same_suite(cards)
    has_flush = True if num_with_same_suite == 5 else False

#    pdb.set_trace()
    bonus_power = 0
    if has_flush and has_straight(cards):
        bonus_power = base_power + 7
    elif has_four_of_a_kind(cards):
        bonus_power = base_power + 6
    elif has_pair(cards) and has_three_of_a_kind(cards):
        bonus_power = base_power + 5
    elif has_flush:
        bonus_power = base_power + 4
    elif has_straight(cards):
        bonus_power = base_power + 3
    elif has_three_of_a_kind(cards):
        bonus_power = base_power + 2
    elif number_of_pairs(cards) == 2:
        bonus_power = base_power + 1
    elif has_pair(cards):
        bonus_power = base_power

    return 4 ** bonus_power
        

def has_four_of_a_kind(cards):
    value_counts = get_value_counts(cards)
    return value_counts.values().count(4) == 1
    
    
def has_pair(cards):
    return number_of_pairs(cards) >= 1


def has_three_of_a_kind(cards):
    value_counts = get_value_counts(cards)
    return value_counts.values().count(3) == 1

    
def has_straight(cards):
    value_counts = get_value_counts(cards)
    vals = value_counts.values()
    vals.sort()
    return vals[-1] - vals[0] == len(vals)

    
def number_of_pairs(cards):
    return get_value_counts(cards).values().count(2)
    
if __name__ == "__main__":
    black_cards, white_cards = [], []

    for line in fileinput.input():
        cards = readin_line(line)
        black_cards.append(cards[:5])
        white_cards.append(cards[5:])

    for blacks, whites in zip(black_cards, white_cards):
        blacks_hash, whites_hash = cards_hash(blacks), cards_hash(whites)
        if blacks_hash > whites_hash:
            print "Black wins."
        elif whites_hash > blacks_hash:
            print "Whites wins."
        else:
            print "Tie."
    
