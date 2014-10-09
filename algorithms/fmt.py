

import fileinput


def format_lines(lines):
    tokens = remove_newlines(get_tokens(lines))
    formatted_tokens = []
    
    line_length = 0
    for token in tokens:
        if token == "\n":
            formatted_tokens.append(token)
            line_length = 0
        elif line_length + len(token) <= 72:
            formatted_tokens.append(token)
            line_length += len(token) + 1
            if token.endswith('\n'):
                line_length = 0
        else:
            formatted_tokens.append('\n' + token)
            line_length = len(token) + 1
            
    return formatted_tokens

    
def get_tokens(lines):
    return [w for l in lines for w in l.split(" ")]

    
def remove_newlines(tokens):
    out_tokens = []
    for i in range(len(tokens)):
        if tokens[i].endswith('\n') and can_remove_newline(tokens, i):
            out_tokens.append(tokens[i][:len(tokens[i]) - 1])
            # out_tokens.append('')
        else:
            out_tokens.append(tokens[i])
            
    return out_tokens

    
def can_remove_newline(tokens, i):
    """Returns True or False indicating if the newline
    can be removed from input tokens.

    Args:
    i: index of a token where newline symbol has been found in tokens
    """
    assert(i < len(tokens))
    
    if tokens[i] == '\n':
        return False
    elif i == len(tokens):
        return True
    else:
        return not (tokens[i + 1] == '' or tokens[i + 1] == '\n')


if __name__ == "__main__":
    input_filename = "fmt_input.txt"
    input_lines = []

    for line in fileinput.input(input_filename):
        input_lines.append(line)
    
    print "Input file:"
    print
    print ''.join(input_lines)
    
    print "Output file:"
    print
    print ' '.join(format_lines(input_lines))
