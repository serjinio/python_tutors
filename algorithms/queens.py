

class Board(object):

    def __init__(self, size):
        self.size = size
        self.positions = [(i, k) for i in range(0, 4) for k in range(0, 4)]

    def get_row_positions(self, row_number):
        if row_number > self.size:
            raise ValueError('Illegal row number.')
        return [pos for pos in self.positions if pos[0] == row_number]

    def get_column_positions(self, column_number):
        return [pos for pos in self.positions if pos[1] == column_number]

    def get_diagonal(position):
        if len(position) != 2:
            raise ValueError('Illegal position type used, not 2-tuple.')
        positions = set(position)
        # TODO: finish up
        

class Queen(object):

    def __init__(self, board, position):
        self.board = board
        self.position = position

    def threat_cells(self):
        vertical = set(self.board.get_row_positions(self.position[0]))
        horizontal = set(self.board.get_column_positions(self.position[1]))
        threat_cells = vertical | horizontal

        return threat_cells
        
    def is_under_threat(self, position):
        return position in self.threat_cells()


if __name__ == '__main__':
    board = Board(4)
    print board.positions
    queen = Queen(board, (1, 1))
    print "Queen position: %s" % str(queen.position)
    print "Positions under threat: %s" % str(queen.threat_cells())
