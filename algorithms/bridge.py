

import fileinput


def compute_best_strategy(round):
    moves, other = [], []
    total_time = 0
    turn = 'from'

    round.sort()
    fastest, second_fastest = round[0], round[1]

    while round:
        print 'making turn ', turn, '...'
        if turn == 'from':
            if fastest in round and second_fastest in round:
                total_time += second_fastest
                moves.append(round[:2])
                move(round, other, round[:2])
            else:
                total_time += max(round[-2:])
                moves.append(round[-2:])
                move(round, other, round[-2:])
        if turn == 'to':
            total_time += other[0]
            moves.append(other[0])
            move(other, round, other[0])

        print 'source side:', round
        print 'destination side:', other
        
        round.sort()
        other.sort()
        if turn == 'from':
            turn = 'to'
        else:
            turn = 'from'
            
    moves.insert(0, total_time)
    return moves
    

def move(fr, to, el):
    if hasattr(el, '__iter__'):
        del fr[fr.index(el[0])]
        del fr[fr.index(el[1])]
        to.append(el[0])
        to.append(el[1])
    else:
        del fr[fr.index(el)]
        to.append(el)

    
if __name__ == '__main__':
    rounds = []
    current_round = []
    for index, line in enumerate(fileinput.input()):
        if index in (0, 1):
            continue
        if line.strip() == '':
            # get rid of length, we do not need it and append to rounds list
            del current_round[0]
            rounds.append(current_round)
            current_round = []
            continue
            
        current_round.append(int(line.strip()))

    # append last round
    if len(current_round) > 1:
        del current_round[0]
        rounds.append(current_round)

    results = []
    for r in rounds:
        results.append(compute_best_strategy(r))

    print results
    for r in results:
        for el in r:
            print el
        print

