#!/usr/bin/env python3

import ply.lex as lex

states = (
    # our initial state is always non-UTL, switch on '[%'
    ('utl', 'inclusive'),
)

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'elseif': 'ELSEIF',
    'then': 'THEN',
    'while': 'WHILE',
    'call': 'CALL',
    'macro': 'MACRO',
    'end': 'END',
    'return': 'RETURN',
    'exit': 'EXIT',
    'include': 'INCLUDE',
    'true': 'TRUE',
    'false': 'FALSE',
    'for': 'FOR',
    'continue': 'CONTINUE',
    'break': 'BREAK',
    'echo': 'ECHO',
    'default': 'DEFAULT',
    'as': 'AS',
    'foreach': 'FOR',
    'null': 'NULL',
    # special variable names
    'this': 'THIS',
    'cms': 'CMS'
}

# does UTL support all these? From PHP docs
PHP_operators = [r'\[', r'\*\*', r'\+\+', r'--', r'~', r'(int)',
                 r'(float)', '(string)', '(array)', '(object)',
                 '(bool)', '@', 'instanceof', '!', r'\.', '<<', '>>',
                 '<', '<=', '>', '>=', '==', '!=', '===', '!==', '<>',
                 '&&', r'\|\|', r'\?', ':', '=>', 'and', 'xor', 'or',
                 ',', 'is', 'is not', r'\.\.']

assignment_ops = [r'\+=', '-=', r'\*=', r'\*\*=', '/=', r'\.=',
                  '%=', '&=', r'\|=', r'\^=', '<<=', '>>=']

# '&', '^', '|',

tokens = ['START_UTL',
          'END_UTL',
          'ID',
          'NUMBER',
          'COMMENT',
          'LPAREN',
          'RPAREN',
          'LBRACKET',
          'RBRACKET',
          'COLON',
          'ASSIGN',
          'OP',
          'PLUS',
          'MINUS',
          'TIMES',
          'DIV',
          'MODULUS',
          'ASSIGNOP',
          'SEMI',
          'RANGE',
          'FILTER',
          'STRING',
          'DOCUMENT'] + list(set(reserved.values()))

# ======== Tokens that switch state ==========================


def t_ANY_START_UTL(t):
    r'\[%-?'
    # use push_state() to handle nested [% %]
    t.lexer.push_state('utl')


def t_ANY_END_UTL(t):
    r'-?%]'
    try:
        t.lexer.pop_state()
    except IndexError:
        # attempt to end without beginning code
        print("Lexical error at line {}: unmatched '%]'".format(t.lexer.lineno))

# ======== INITIAL state =====================================
# everything up to START_UTL gets put in one token
t_DOCUMENT = r'[^[]+'


# this gives us
# LexToken(DOCUMENT,'some text',..
# LexToken(DOCUMENT,'[',...
# LexToken(DOCUMENT,'more text',...
# which is not ideal, but workable
# parser will have to paste them together
def t_LBRACKET(t):
    r'\['
    # must detect START_UTL
    if t.lexer.lexdata[t.lexer.lexpos + 1] != '%':
        t.type = 'DOCUMENT'
        t.value = '['
    return t


t_utl_LBRACKET = r'\['


# Define a rule so we can track line numbers
def t_utl_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# ======== UTL state =====================================

# "Identifier scoping is implemented only for macros. All other block
# constructs and included files operate in the same scope as the
# parent file. For macro scoping an identifier will first be sought
# for within the macro, and failing that the containing scope will be
# fallen back upon. A global scope exists and is accessible from all
# scoping levels (including exclusive). Global scope is normally used
# only for predefined filters and identifiers."

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'

t_utl_LPAREN = r'[)]'
t_utl_RPAREN = r'[(]'
t_utl_RBRACKET = r']'
t_utl_COLON = r':'
t_utl_ASSIGN = r'='

t_utl_TIMES = r'\*'
t_utl_DIV = '/'
t_utl_MODULUS = '%'
t_utl_PLUS = r'\+'
t_utl_MINUS = '-'

# comment (ignore)
# PROBLEMS: comments *can* be nested
#          delimiters outside template ([% .. %])
#          should be ignored
# probably need another lexer state
# must come before OP
def t_utl_COMMENT(t):
    r'(/\*(.|\n)*?\*/)'
    pass


# this will not allow us to handle precedence in expressions
@lex.TOKEN("|".join(PHP_operators))
def t_utl_OP(t):
    return t


@lex.TOKEN("|".join(assignment_ops))
def t_utl_ASSIGNOP(t):
    return t


t_utl_SEMI = r';'
t_utl_FILTER = r'\|'


# attributes of t param:
# t.type: the token type (as a string)
# t.value: the lexeme (the actual text matched)
# t.lineno: the current line number
# t.lexpos: the position of the token relative to the beginning of
#     the input text
# t.lexer: the Lexer object

# print attributes that are 'interesting' and not too long
# for x in dir(t.lexer):
#     # not method, special name
#     if (type(getattr(t.lexer, x)) != type(t.lexer.clone)
#             and not x.startswith('_')
#             and x not in ['lexdata', 'lexre', 'lexretext',
#                           'lexstaterenames', 'lexstateretext',
#                           'lextokens', 'lexstatere',
#                           'lextokens_all']):
#         print("{}: {}".format(x, getattr(t.lexer, x)))


def t_utl_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # case-insensitive check for reserved words
    t.type = reserved.get(t.value.lower(), 'ID')
    return t


def t_utl_NUMBER(t):
    r'\d+(\.\d+)?'
    t.value = float(t.value)
    return t


def t_utl_STRING(t):
    r'"(?P<dq>[^"]*)"|\'(?P<sq>[^\']*)\''
    dq = t.lexer.lexmatch.group('dq')
    sq = t.lexer.lexmatch.group('sq')
    t.value = dq if dq else sq
    return t


# Error handling rule
def t_utl_error(t):
    print("Illegal character '%s' in template code." % t.value[0])
    t.lexer.skip(1)


# should never happen, but needed to silence warning
def t_error(t):
    print("Illegal character '%s' in non-template text." % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()
