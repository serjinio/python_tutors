

import logging
import unittest


_type_names = ['int', 'long', 'float', 'double', 'char']
_type_qualifiers = ['signed', 'unsigned', 'volatile', 'const', '*']


class AST(object):
    """Abstract node."""

    def __init__(self):
        self.children = []

    def visit(self, visitor):
        """Visitor method to implement parser actions."""
        raise NotImplementedError(('This method should be implemented '
                                   'in child classes.'))

    def __str__(self):
        return 'Abstract node, should NOT be used directly!'


class ASTRoot(AST):
    """Root node of every AST."""

    def __init__(self, children=[]):
        super(ASTRoot, self).__init__()
        self.children = children

    def visit(self, visitor):
        visitor.visit_root_node(self)

    def __str__(self):
        return 'AST root marker node'


class TypeName(AST):
    """Represents a type name."""

    def __init__(self, type_name):
        super(TypeName, self).__init__()
        self.type_name = type_name
        self.is_pointer_to_type = False

    def visit(self, visitor):
        visitor.visit_type_name_node(self)

    def __str__(self):
        return '"{}" type name'.format(self.type_name)


class TypeQualifier(AST):
    """Qualifiers for type declaration like * const etc."""

    def __init__(self, qualifier):
        super(TypeQualifier, self).__init__()
        self.qualifier = qualifier

    def visit(self, visitor):
        visitor.visit_type_qualifier_node(self)

    def __str__(self):
        return '"{}" type qualifier'.format(self.qualifier)


class Name(AST):
    """Identifier name."""

    def __init__(self, identifier_name):
        super(Name, self).__init__()
        self.identifier_name = identifier_name

    def visit(self, visitor):
        visitor.visit_identifier_name_node(self)

    def __str__(self):
        return '"{}" identifier name'.format(self.identifier_name)


class ArrayDeclarator(AST):
    """Array types declarator."""

    def __init__(self, size=None):
        super(ArrayDeclarator, self).__init__()
        self.size = size

    def visit(self, visitor):
        visitor.visit_array_declarator_node(self)

    def __str__(self):
        return 'array declarator of size: "{}"'.format(self.size)


class Translator:
    """Translates declaration into human readable form."""

    typename_translations = {
        'int': 'integer',
        'char': 'character'
    }

    def __init__(self, ast_root_node):
        self.ast_root = ast_root_node
        self.translated_form = ''

    def translate(self):
        self.translated_form = ''
        self._traverse_ast()
        self.translated_form = self.translated_form.strip()
        return self.translated_form

    def _traverse_ast(self):
        logging.debug('traversing ast:')
        self._discovered_nodes = set()
        self._visited_nodes = set()
        self._traverse_node(self.ast_root)

    def _traverse_node(self, node):
        self._discovered_nodes.add(node)
        self._do_node_preorder_action(node)
        children = [child for child in node.children if
                    child not in self._discovered_nodes]
        for child in children:
            self._traverse_node(child)
        self._do_node_postorder_action(node)

    def _do_node_preorder_action(self, node):
        if isinstance(node, Name):
            logging.debug('\t visiting node "{}"'.format(node))
            node.visit(self)

    def _do_node_postorder_action(self, node):
        logging.debug('\t visiting node "{}"'.format(node))
        if not isinstance(node, Name):
            node.visit(self)

    def _is_leaf_node(self, node):
        return len(node.children) == 0

    def visit_root_node(self, node):
        pass

    def visit_type_name_node(self, node):
        self.translated_form += \
            Translator.typename_translations[node.type_name] + ' '

    def visit_identifier_name_node(self, node):
        self.translated_form += 'declare ' + node.identifier_name + ' as '

    def visit_type_qualifier_node(self, node):
        if node.qualifier == 'const':
            self.translated_form += 'read-only '
        elif node.qualifier == '*':
            self.translated_form += 'pointer-to '
        elif node.qualifier == 'volatile':
            self.translated_form += 'volatile '
        else:
            raise SyntaxError('Invalid type qualifier encountered: "{}"'
                              .format(node.qualifier))

    def visit_array_declarator_node(self, node):
        if node.size is not None:
            self.translated_form += \
                'array of {} elements of '.format(node.size)
        else:
            self.translated_form += \
                'array of '


def is_type_declaration(src):
    assert(len(src) > 0)
    tokens = src.split(' ')
    if tokens[0] in _type_names or tokens[0] in _type_qualifiers:
        return True
    else:
        return False


def parse_simple_declaration(declaration):
    if not is_type_declaration(declaration):
        raise SyntaxError('Passed fragment: "{}" is not a valid declaration.'
                          .format(declaration))
    tokens = tokenize_decl(declaration)
    ident_idx, identifier = _find_decl_identifier(tokens)
    name_node = Name(identifier)
    left, right = tokens[0:ident_idx], tokens[ident_idx + 1:]
    direction = +1
    t = _get_next_decl_token(left, right, direction)
    while t is not None:
        if t in [')', '(']:
            direction *= -1
        else:
            node = _construct_ast_node_from_token(t, left, right)
            name_node.children.append(node)
        t = _get_next_decl_token(left, right, direction)
    return name_node


def _find_decl_identifier(tokens):
    for idx, t in enumerate(tokens):
        if _is_identifier(t):
            return idx, t
    raise ValueError('No identifier found in the declaration: "{}"'
                     .format(tokens))


def _get_next_decl_token(left, right, direction):
    if len(left) == 0 and len(right) == 0:
        return None
    token = None
    if len(left) == 0:
        token = right[0]
        del right[0]
        return token
    elif len(right) == 0:
        token = left[-1]
        del left[-1]
        return token

    if direction > 0:
        token = right[0]
        del right[0]
        return token
    else:
        token = left[-1]
        del left[-1]
        return token


def _construct_ast_node_from_token(t, left, right):
    if _is_type_qualifier(t):
        return TypeQualifier(t)
    elif _is_type_name(t):
        return TypeName(t)
    elif _is_array_declarator(t):
        return _make_array_declarator(right)
    else:
        raise SyntaxError('Unexpected token encountered: "{}".'
                          .format(t))


def _make_array_declarator(right):
    logging.debug('making array declarator:')
    if len(right) < 1 or ']' not in right:
        raise SyntaxError(('Opening array declarator: "[" should '
                           'follow optional size specification and a '
                           'closing "]".'))
    size_specifier = None
    array_t = right[0]
    del right[0]
    while array_t != ']':
        if array_t.isdigit():
            size_specifier = int(array_t)
            logging.debug('\t read array size specifier: "{}"'.format(array_t))
        else:
            raise SyntaxError(('Array size specifier should be an '
                               'integer number.'))
        array_t = right[0]
        del right[0]
    return ArrayDeclarator(size=size_specifier)


def tokenize_decl(src):
    logging.debug('tokenizing declaration: "{}"'.format(src))
    res = []
    t = ''
    s, f = 0, 1
    while f <= len(src):
        f = _find_next_token(src, s)
        t = src[s:f].strip()
        if len(t) > 0:
            logging.debug('read token: "{}"'.format(t))
            res.append(t)
        s = f
    logging.debug('finished tokenization')
    return res


def _is_identifier(token):
    if token.isalnum() and token not in _type_names \
       and token not in _type_qualifiers:
        return True
    else:
        return False


def _is_type_name(token):
    return token in _type_names


def _is_type_qualifier(token):
    return token in _type_qualifiers


def _is_array_declarator(token):
    return token == '['


def _find_next_token(src, start_idx):
    end_idx = start_idx + 1
    while (end_idx < len(src)):
        t = src[start_idx:end_idx]
        if t == ' ':
            start_idx += 1
            end_idx += 1
            continue
        if t in ['*', '(', ',', '[', ']']:
            return end_idx
        if src[end_idx] in ['(', ')', '[', ']', '*', ' ']:
            return end_idx
        end_idx += 1
    return end_idx


class TestScanner(unittest.TestCase):
    """Tests tokenization."""

    def setUp(self):
        self.decl1 = 'int var1'
        self.decl2 = 'int *var2'
        self.decl3 = 'const int * const var2'
        self.decl4 = 'int **var'
        self.decl5 = 'int (*var)'

    def test_simple_decl1(self):
        res = tokenize_decl(self.decl1)
        self.assertEquals(res[0], 'int')
        self.assertEquals(res[1], 'var1')

    def test_simple_decl2(self):
        res = tokenize_decl(self.decl2)
        self.assertEquals(res[0], 'int')
        self.assertEquals(res[1], '*')
        self.assertEquals(res[2], 'var2')

    def test_simple_decl3(self):
        res = tokenize_decl(self.decl3)
        self.assertEquals(res[0], 'const')
        self.assertEquals(res[1], 'int')

    def test_simple_decl4(self):
        res = tokenize_decl(self.decl4)
        self.assertEquals(res[0], 'int')
        self.assertEquals(res[1], '*')
        self.assertEquals(res[2], '*')
        self.assertEquals(res[3], 'var')

    def test_decl5(self):
        res = tokenize_decl(self.decl5)
        self.assertEquals(res[0], 'int')
        self.assertEquals(res[1], '(')
        self.assertEquals(res[2], '*')
        self.assertEquals(res[3], 'var')
        self.assertEquals(res[4], ')')


class TestParser(unittest.TestCase):
    """Tests declarations parser."""

    def setUp(self):
        self.decl1 = 'int var1'
        self.decl2 = 'const int var'
        self.decl3 = 'const int *var'
        self.decl4 = 'const int * const var'
        self.decl5 = 'const int var[100]'
        self.decl6 = 'int *var[100]'
        self.decl7 = 'int *var[]'
        self.decl8 = 'int (((*var)))'
        self.decl9 = 'char ** const * const x'
        self.decl10 = 'const int (* volatile bar)[64]'

    def _parse_simple_decl(self, decl):
        name_node = parse_simple_declaration(decl)
        ast_root = ASTRoot([name_node])
        return ast_root

    def _translate_simple_decl(self, decl):
        ast_root = self._parse_simple_decl(decl)
        trans = Translator(ast_root)
        target_phrase = trans.translate()
        return target_phrase

    def test_decl1(self):
        self.assertEquals(self._translate_simple_decl(self.decl1),
                          'declare var1 as integer')

    def test_decl2(self):
        self.assertEquals(self._translate_simple_decl(self.decl2),
                          'declare var as integer read-only')

    def test_decl3(self):
        self.assertEquals(self._translate_simple_decl(self.decl3),
                          'declare var as pointer-to integer read-only')

    def test_decl4(self):
        self.assertEquals(
            self._translate_simple_decl(self.decl4),
            'declare var as read-only pointer-to integer read-only')

    def test_decl5(self):
        self.assertEquals(
            self._translate_simple_decl(self.decl5),
            'declare var as array of 100 elements of integer read-only')

    def test_decl6(self):
        self.assertEquals(
            self._translate_simple_decl(self.decl6),
            'declare var as array of 100 elements of pointer-to integer')

    def test_decl7(self):
        self.assertEquals(
            self._translate_simple_decl(self.decl7),
            'declare var as array of pointer-to integer')

    def test_decl8(self):
        self.assertEquals(
            self._translate_simple_decl(self.decl8),
            'declare var as pointer-to integer')

    def test_decl9(self):
        self.assertEquals(
            self._translate_simple_decl(self.decl9),
            ('declare x as read-only pointer-to read-only '
             'pointer-to pointer-to character'))

    def test_decl10(self):
        self.assertEquals(
            self._translate_simple_decl(self.decl10),
            ('declare bar as volatile pointer-to array of '
             '64 elements of integer read-only'))


def configure_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:  %(message)s')


if __name__ == '__main__':
    configure_logging()
    unittest.main()

