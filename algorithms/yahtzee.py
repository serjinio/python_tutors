
import fileinput
import pdb


class DiceValue(object):
    
    MIN_CATEGORY = 1
    MAX_CATEGORY = 13
    CATEGORY_RANGE = range(MIN_CATEGORY, MAX_CATEGORY + 1)

    def __init__(self, value):
        if not hasattr(value, '__len__') or len(value) != 5:
            raise ValueError(("Illegal argument provided: {0}. " +
                              "Should be 5-tuple.").format(value))
        self._value = value

    def value(self):
        return self._value

    def sum_of_value(self):
        return sum(self._value)
    
    def scores(self):
        res = dict([(c, self.score(c)) for c in self.CATEGORY_RANGE])
        return res

    def scores_as_list_desc(self):
        """Returns scores as list of tuples: (category, score),
        sorted in descending order - highest scores first.
        """
        scs = self.scores()
        scs_list = zip(scs.keys(), scs.values())
        scs_list.sort(key=lambda el: el[1])
        scs_list.reverse()
        return scs_list

    def score(self, category):
        if category not in self.CATEGORY_RANGE:
            raise ValueError("Invalid value for a category: %d. " +
                             "Should be one of %s." % category,
                             self.CATEGORY_RANGE)
        counts = self._count_values()
        
        if category <= 6:
            return sum(e for e in self.value() if e == category)
        else:
            casemap = {
                7: lambda: sum(self.value()),
                8: lambda: sum(self.value()) if 3 in counts.values() else 0,
                9: lambda: sum(self.value()) if 4 in counts.values() else 0,
                10: lambda: 50 if 5 in counts.values() else 0,
                11: lambda: 25 if self._is_straight_of(4) else 0,
                12: lambda: 35 if self._is_straight_of(5) else 0,
                13: lambda: 40 if len(set(self.value())) == 2 else 0
            }
            assert(self.MAX_CATEGORY in casemap)
            return casemap[category]()
            
    def _count_values(self):
        count_val = lambda v: len([1 for x in self.value() if x == v])
        return dict((x, count_val(x)) for x in self.value())
        
    def _is_straight_of(self, length):
        vlist = list(self.value())
        vlist.sort()
        diffs = []
        for i in range(1, len(vlist)):
            diffs.append(vlist[i] - vlist[i - 1])
        return diffs.count(1) + 1 >= length

    def __str__(self):
        return str(self.value())

    def __repr__(self):
        return str("DiceValue({0})".format(self.value()))
        

class DiceValsQueue(object):
    """Wrapper for list of dice values with convenience methods."""

    def __init__(self, dice_values):
        self._dice_values = dice_values
        self.sort_dices()

    def pop(self):
        diceval = self._dice_values[-1]
        del self._dice_values[-1]
        return diceval

    def push_left(self, diceval):
        if diceval is not None:
            self._dice_values.insert(0, diceval)
            self.sort_dices()
        
    def sort_dices(self):
        self._dice_values.sort(key=lambda el: 30 - el.sum_of_value())
        
    def __len__(self):
        return len(self._dice_values)

            
class Yahtzee(object):
    
    def __init__(self, dice_values):
        if not hasattr(dice_values, '__len__') or len(dice_values) != 13:
            raise ValueError('Invalid dice values were provided.')
        self._DICE_VALUES = dice_values

    def reset(self):
        self._dice_map = dict([(c, None) for c
                               in DiceValue.CATEGORY_RANGE])
        self._dice_values = DiceValsQueue(
            [DiceValue(x.value()) for x in self._DICE_VALUES])
        self._dice_values.push_left("some value")
        
    def dice_mapping(self):
        self.reset()
        while len(self._dice_values) > 0:
            diceval = self._dice_values.pop()
            best_cat = self._best_category(diceval)
            otherdiceval = self._update_dice_map(
                diceval, best_cat)
            self._dice_values.push_left(otherdiceval)
            
        #self._optimize_dice_mapping(self._dice_map)
        pdb.set_trace()
        return self._dice_map

    def _optimize_dice_mapping(self, dice_map):
        for category in dice_map.keys():
            for cat in dice_map.keys():
                if cat == category:
                    continue
                score_before = self._compute_total_score(dice_map)
                self._swap_dices(dice_map, cat, category)
                score_after = self._compute_total_score(dice_map)
                if score_after < score_before:
                    self._swap_dices(dice_map, cat, category)

    def _swap_dices(self, dice_map, key1, key2):
        dice_map[key1], dice_map[key2] = dice_map[key2], dice_map[key1]
    
    def _have_bonus(self, dice_map):
        return self._compute_scores(dice_map)[:-1] > 0
        
    def game_summary(self):
        self.dice_mapping()
        return self._compute_scores(self._dice_map)

    def _compute_total_score(self, dice_map):
        return self._compute_scores(dice_map)[-1]

    def _compute_scores(self, dice_map):
        scores = [dice_map[i].score(i) for i in
                  DiceValue.CATEGORY_RANGE]
        scores.append(35 if sum(scores[:6]) >= 63 else 0)
        scores.append(sum(scores))
        return scores
        
    def _best_category(self, dice_value):
        """Returns best matching category for a given dice value."""
        for category, score in dice_value.scores_as_list_desc():
            prevscore = -1 if self._dice_map.get(category) is None \
                else self._dice_map.get(category).score(category)
            if score > prevscore:
                return category
        raise ValueError(
            'Illegal state: program was not able to find mathing ' +
            'category for a dice value: %s' % dice_value)
        
    def _update_dice_map(self, dicevalue, category):
        prevdicevalue = self._dice_map.get(category)
        self._dice_map[category] = dicevalue
        return prevdicevalue


if __name__ == '__main__':
    dicevalues = []
    for line in fileinput.input():
        values = [int(t) for t in line.split()]
        dicevalues.append(DiceValue(values))

    for i in range(0, len(dicevalues), 13):
        game = Yahtzee(dicevalues[i:i + 13])
        game_scores = game.game_summary()
        print game_scores
