

import fileinput


def find_best_street(relatives_streets):
    relatives_streets.sort()
    if (len(relatives_streets) == 1):
        return relatives_streets[0]
    else:
        return relatives_streets[len(relatives_streets) / 2]

        
def get_total_dist(ref_str, streets):
    return sum([abs(ref_str - s) for s in streets])

    
def convert_input_line(line):
    res = []
    for ind, el in enumerate(line.strip().split(" ")):
        if ind == 0:
            continue
        else:
            res.append(int(el))
    return res


if __name__ == "__main__":
    input_lines = []
    for line in fileinput.input():
        input_lines.append(convert_input_line(line))

    best_streets = [find_best_street(inp) for inp in input_lines]
    distances = [get_total_dist(s, line) for s, line in
                 zip(best_streets, input_lines)]

    for dist in distances:
        print dist
