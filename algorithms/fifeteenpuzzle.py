

import fileinput
import copy
import random
import cProfile
import sys
import logging


class FifeteenPuzzle(object):
    """Represent data structure for Fifeteen puzzle."""

    def __init__(self, input_numbers):
        """Initializes object with input data.

        :param input_numbers: List of lists representing 4 by 4
          array of integers.
        """
        if type(input_numbers[0][0]) is not int:
            raise ValueError('Can only initialize puzzle with arrays of ints, '
                             'but found "{}" as elements type!'.format(
                                 type(input_numbers[0][0])))

        self.numbers = input_numbers

        self._hash = 0
        self.__hash__()

    def get(self, position):
        """Returns number at specified position."""
        return self.numbers[position[0]][position[1]]

    def get_position(self, number):
        """Returns position of a given number in the puzzle."""
        for rowidx, row in enumerate(self.numbers):
            for colidx, num in enumerate(row):
                if num == number:
                    return rowidx, colidx

    @property
    def swappable_positions(self):
        """Return a set of position 2-tuples which are currently swappable."""
        swappable = []
        empty_position = self.get_position(0)
        for i in range(-1, 2, 2):
            adjacent_position1 = empty_position[0] + i, empty_position[1]
            adjacent_position2 = empty_position[0], empty_position[1] + i
            if 0 <= adjacent_position1[0] < 4:
                swappable.append(adjacent_position1)
            if 0 <= adjacent_position2[1] < 4:
                swappable.append(adjacent_position2)

        return swappable

    def swap(self, position):
        """Swap empty and one of the pieces adjacent with it.

        The function does not modifies original object, but returns a newly
        created copy where the swap has been made.

        :param position: 2-tuple: (row, column) specifying which piece
               to swap with empty one
        :return: reference to self for chain calls
        :raise ValueError: in case not swappable position has been specified
        """
        if position not in self.swappable_positions:
            raise ValueError(
                "Cannot swap this position: %s, it is not swappable." %
                str(position))

        newpuz = FifeteenPuzzle(copy.deepcopy(self.numbers))
        empty_position = newpuz.get_position(0)
        swap_number = newpuz.get(position)

        newpuz._put(empty_position, swap_number)
        newpuz._put(position, 0)

        return newpuz

    def move(self, m):
        """Perform move in the specified direction.

        :param m: Move direction, should be one of the: 'RLUD'.
        :returns: Newly created copy of the object with move made
        """
        if m not in "RLUD":
            raise ValueError(
                ("Not a legal move: '{}', should be one of " +
                 "the 'RLUD'.").format(m))
        if m not in self.legal_moves:
            raise ValueError(
                ("Not a legal move at this state: '{}', " +
                 "should be one of the '{}'.").format(m, self.legal_moves))

        posdiff = (0, 0)
        if m == 'L':
            posdiff = (0, 1)
        elif m == 'R':
            posdiff = (0, -1)
        elif m == 'U':
            posdiff = (1, 0)
        elif m == 'D':
            posdiff = (-1, 0)

        empty_position = self.get_position(0)
        newpuz = self.swap((empty_position[0] - posdiff[0],
                            empty_position[1] - posdiff[1]))
        return newpuz

    @property
    def legal_moves(self):
        """Returns all moves which are legal in current state of the puzzle.

        The method should be used to check valid moves prior to
        calling move().
        """
        moves = ""
        swappable = self.swappable_positions
        empty_position = self.get_position(0)

        for s in swappable:
            pos_diff = empty_position[0] - s[0], empty_position[1] - s[1]
            if pos_diff[0] > 0:
                moves += "U"
            elif pos_diff[0] < 0:
                moves += "D"
            elif pos_diff[1] > 0:
                moves += "L"
            elif pos_diff[1] < 0:
                moves += "R"

        return moves

    @property
    def is_sequential(self):
        """Returns True if the state of the puzzle is in sequence."""
        counter = 1
        for r in range(0, 4):
            for c in range(0, 4):
                if counter == 16:
                    return True
                elif self.get((r, c)) != counter:
                    return False
                counter += 1

    def _put(self, position, value):
        # invalidate hash as we mutating the object
        self._hash = 0
        self.numbers[position[0]][position[1]] = value

    def __hash__(self):
        if self._hash:
            return self._hash

        self._hash = hash(str(self))
        
        return self._hash

    def __str__(self):
        res = ""
        for a, b, c, d in self.numbers:
            res += "{:2d} {:2d} {:2d} {:2d}\n".format(a, b, c, d)
        return res

    def __eq__(self, other):
        if type(other) is not FifeteenPuzzle:
            return False                    
        if other.__hash__() != self.__hash__():
            return False

        # Hash collisions are unavoidable for such object as there
        # are 15! number of different FifeteenPuzzles possible
        # we have to make sure by using memberwise comparison
        # return True

        for row in range(0, 4):
            for column in range(0, 4):
                if other.numbers[row][column] != self.numbers[row][column]:
                    msg = ("Incorrect hash encountered on:\n{}\nIt's " +
                           "hash value is equal to another object " +
                           "hash:\n{}").format(str(self), str(other))
                    logging.warning(msg)
                    return False

        return True


def read_input(input_lines):
    assert(len(input_lines) == 4)

    input = []
    for l in input_lines:
        tokens = l.split(' ')
        assert(len(tokens) == 4)

        input.append([int(t) for t in tokens])
        if len(input) == 4:
            break

    return input

    
def solve(puzzle):
    moves = _backtrack(puzzle)
    if moves:
        print 'The solution is: {}'.format(moves)
    else:
        print 'Was not able to find a solution.'

        
recursion_level = 0
tries_count = 0


def _backtrack(puzzle):
    global tries_count
    processed_states = set()
    processed_states.add(puzzle)
    states = []
    states.append((puzzle, ""))

    while len(states) > 0:
        tries_count += 1
        puz_state, puz_moves = states.pop(0)

        if puz_state.is_sequential:
            return puz_moves
        if len(puz_moves) > 15:
            logging.debug("This branch is not a solution, stopping!")
            return False

        # if tries_count > 7000:
        #    sys.exit()

        legal_moves = puz_state.legal_moves
        if len(puz_moves) > 0:
            opposite_move = "LRDU"["RLUD".find(puz_moves[-1])]
            legal_moves = legal_moves.replace(opposite_move, '')
        legal_moves = ''.join(random.sample(legal_moves, len(legal_moves)))

        newstates = [(puz_state.move(m), puz_moves + m) for m in legal_moves]
        newstates_filtered = [s for s in newstates if s[0]
                              not in processed_states]
        if len(newstates) != len(newstates_filtered):
            logging.debug("Removed some states. Not filtered & "
                          "filtered set lengths: {}, {}.".format(
                              len(newstates), len(newstates_filtered)))
        states = states + newstates_filtered
        processed_states = processed_states | \
            set([s[0] for s in newstates_filtered])

        logging.info(('Moves made: {}; tries count: {}; will check ' +
                      'moves: {}').format(len(puz_moves),
                                          tries_count, legal_moves))
        logging.debug('End of iteration, moves taken: {}'.format(puz_moves))

    return False


def check_puzzle(puzzle, solution):
    if solution == '':
        return puzzle

    move, solution = solution[:1], solution[1:]

    return check_puzzle(puzzle.move(move), solution)


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')


TESTING = True


if __name__ == '__main__':
    configure_logging()
    puzzle_input = None
    test_input1 = ["2 3 4 0",
                   "1 5 7 8",
                   "9 6 10 12",
                   "13 14 11 15"]
    test_input2 = ["1 2 3 4",
                   "5 6 7 8",
                   "9 10 11 12",
                   "13 14 15 0"]
    test_input3 = ["13 1 2 4",
                   "5 0 3 7",
                   "9 6 10 12",
                   "15 8 11 14"]

    if not TESTING:
        input = ""
        for l in fileinput.input():
            input.append(l)
            if len(input) == 4:
                break
        puzzle_input = read_input(input)
    else:
        puzzle_input = read_input(test_input3)

    puz = FifeteenPuzzle(read_input(test_input1))
    puz2 = FifeteenPuzzle(read_input(test_input2))
    puz3 = FifeteenPuzzle(read_input(test_input3))

    print 'Starting to solve a puzzle...'
    cProfile.run('solve(puz3)')
    print 'Solver finished.'
    
    # print check_puzzle(puz, 'DULLLDRDRDR')
