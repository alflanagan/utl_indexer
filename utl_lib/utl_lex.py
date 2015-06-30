#!/usr/bin/env python3
"""A module to do lexical analysis of UTL documents."""

import ply.lex as lex
import re


class UTLLexerError(RuntimeError):
    """Common class for errors thrown by :py:class:`~utl_lib.utl_lex.UTLLexer`."""
    pass


# PHP tokens implemented in UTL
# T_AS 	as 	foreach
# T_BAD_CHARACTER 	  	anything below ASCII 32 except \t (0x09), \n (0x0a) and \r (0x0d)
# T_BOOLEAN_AND 	&& 	logical operators
# T_BOOLEAN_OR 	|| 	logical operators
# T_BREAK 	break 	break
# T_CLOSE_TAG 	?> or %> 	escaping from HTML
# T_COMMENT 	// or #, and /* */ 	comments
# T_CONSTANT_ENCAPSED_STRING 	"foo" or 'bar' 	string syntax
# T_CONTINUE 	continue 	continue
# T_DEFAULT 	default 	switch
# T_DIV_EQUAL 	/= 	assignment operators
# T_DNUMBER 	0.12, etc. 	floating point numbers
# T_ECHO 	echo 	echo
# T_ELSE 	else 	else
# T_ELSEIF 	elseif 	elseif
# T_EXIT 	exit or die 	exit(), die()
# T_FOR 	for 	for
# T_FOREACH 	foreach 	foreach
# T_IF 	if 	if
# T_INLINE_HTML 	  	text outside PHP
# T_IS_EQUAL 	== 	comparison operators
# T_IS_GREATER_OR_EQUAL 	>= 	comparison operators
# T_IS_NOT_EQUAL 	!= or <> 	comparison operators
# T_IS_SMALLER_OR_EQUAL 	<= 	comparison operators
# T_LNUMBER 	123, 012, 0x1ac, etc. 	integers
# T_LOGICAL_AND 	and 	logical operators
# T_LOGICAL_OR 	or 	logical operators
# T_MINUS_EQUAL 	-= 	assignment operators
# T_MOD_EQUAL 	%= 	assignment operators
# T_MUL_EQUAL 	*= 	assignment operators
# T_OPEN_TAG 	<?php, <? or <% 	escaping from HTML
# T_PLUS_EQUAL 	+= 	assignment operators
# T_RETURN 	return 	returning values
# T_STRING 	parent, self, etc. 	identifiers, e.g. keywords like parent and self,
#                               function names, class names and more are matched. See also
#                               T_CONSTANT_ENCAPSED_STRING.
# T_WHILE 	while 	while, do..while
# T_WHITESPACE 	\t \r\n

# pylint: disable=invalid-name,no-self-use
# method names are dictated by ply introspection
# and many matchers don't affect state, but might later
class UTLLexer(object):
    """A lexer for analysing UTL documents.

    Parameters are same as those for :py:func:`ply.lex`."""

    # UTL code is embedded in an HTML document, usually
    states = (
        # our initial state is always non-UTL, switch on '[%'
        ('utl', 'inclusive'),
    )

    reserved = {
        'and': 'AND',
        'as': 'AS',
        'break': 'BREAK',
        'call': 'CALL',
        'continue': 'CONTINUE',
        'default': 'DEFAULT',
        'each': 'EACH',
        'echo': 'ECHO',
        'else': 'ELSE',
        'elseif': 'ELSEIF',
        'end': 'END',
        'exit': 'EXIT',
        'false': 'FALSE',
        'for': 'FOR',
        'foreach': 'FOR',
        'if': 'IF',
        'is': 'IS',
        'include': 'INCLUDE',
        'macro': 'MACRO',
        'null': 'NULL',
        'not': 'NOT',
        'or': 'OR',
        'return': 'RETURN',
        'then': 'THEN',
        'true': 'TRUE',
        'while': 'WHILE',
    }

    # UTL doesn't support all of the PHP operators
    # NOTE operators that start with other operators must come first i.e. '>=' before '>'
    operators = [r'\.\.', r'\+=', '-=', r'\*=', '/=', '%=', r'\.', r'\*', '-', r'\+', '/', '<=',
                 '>=', '<', '>', '==', '!=', '!', '&&', r'\|\|', r'and', r'or', r'is', r'not',
                 r'\|', ':', ',', '[', '(']

    tokens = ['START_UTL',
              'END_UTL',
              'ID',
              'NUMBER',
              'COMMENT',
              'LPAREN',
              'RPAREN',
              'LBRACKET',
              'RBRACKET',
              # operators
              'COLON',
              'ASSIGN',
              'COMMA',
              'PLUS',
              'MINUS',
              'TIMES',
              'DIV',
              'MODULUS',
              'ASSIGNOP',
              'FILTER',
              'EQ',
              'NEQ',
              'RANGE',
              'LT',
              'LTE',
              'GT',
              'GTE',
              'DOT',
              'DOUBLEAMP',  # &&
              'DOUBLEBAR',  # ||
              'EXCLAMATION',  # ! (not)
              # other
              'SEMI',
              'STRING',
              'DOCUMENT', ] + list(set(reserved.values()))

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def input(self, s):
        """Push new input `s` to the lexer."""
        # lexer doesn't handle equivalence well
        s, _ = re.subn(r'else\s+if', 'elseif', s)
        self.lexer.input(s)

    def token(self):
        """Returns the next token from the input."""
        return self.lexer.token()

    def skip(self, count):
        """Causes the lexer to skip ahead `count` characters."""
        self.lexer.skip(count)

    # note: can't use @property because of the way lexer is dynamically constructed
    def lineno(self):
        ''':returns int: the current line number of the text being analyzed.'''
        return self.lexer.lineno

    @property
    def lexpos(self):
        ''':returns int: the current position (in characters) in the text.'''
        # lex attempts to access this unbound, but it doesn't have to do anything then
        if hasattr(self, 'lexer'):
            return self.lexer.lexpos

    @property
    def lexdata(self):
        ''':returns str: The input data on which the lexer operates.'''
        if hasattr(self, 'lexer'):
            return self.lexer.lexdata

    # ======== Tokens that switch state ==========================
    def t_ANY_START_UTL(self, t):
        r'\[%-?'
        # use push_state() to handle nested [% %]
        t.lexer.push_state('utl')
        # parser needs token to detect syntax errors (e.g. '[% [% %]')
        return t

    def t_ANY_END_UTL(self, t):
        r'-?%]'
        try:
            t.lexer.pop_state()
            return t  # parser needs token to detect end of statement
        except IndexError:
            # attempt to end without beginning code
            raise UTLLexerError("Lexical error at line {}: unmatched '%]'".format(t.lexer.lineno))

    # ======== INITIAL state =====================================
    # everything up to START_UTL gets put in one token
    # this gives us
    # LexToken(DOCUMENT,'some text',..
    # LexToken(DOCUMENT,'[',...
    # LexToken(DOCUMENT,'more text',...
    # which is not ideal, but workable
    # parser will have to paste them together
    def t_DOCUMENT(self, t):
        r'[^[]+'
        t.lexer.lineno += t.value.count('\n')
        return t

    def t_LBRACKET(self, t):
        r'\['
        # must detect START_UTL (??)
        # if t.lexer.lexdata[t.lexer.lexpos + 1] != '%':
        t.type = 'DOCUMENT'
        return t

    # ======== UTL state =====================================
    t_utl_LBRACKET = r'\['

    # Define a rule so we can track line numbers (counting UTL not document)
    def t_utl_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # "Identifier scoping is implemented only for macros. All other block
    # constructs and included files operate in the same scope as the
    # parent file. For macro scoping an identifier will first be sought
    # for within the macro, and failing that the containing scope will be
    # fallen back upon. A global scope exists and is accessible from all
    # scoping levels (including exclusive). Global scope is normally used
    # only for predefined filters and identifiers."

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    t_utl_LPAREN = r'[(]'
    t_utl_RPAREN = r'[)]'
    t_utl_RBRACKET = r']'
    t_utl_COLON = r':'   # bar = ['key1': 'value', 'key2': 'value']
    t_utl_ASSIGN = r'='

    t_utl_TIMES = r'\*'
    t_utl_DIV = '/'
    t_utl_MODULUS = '%'
    t_utl_PLUS = r'\+'
    t_utl_MINUS = '-'
    t_utl_COMMA = ','  # may be operator, may be separator
    t_utl_EXCLAMATION = '!'
    t_utl_DOT = r'\.'
    t_utl_DOUBLEAMP = r'&&'  # means same as "and" , but that is reserved word not op
    t_utl_DOUBLEBAR = r'\|\|'  # means same as "or"
    t_utl_EQ = '=='
    t_utl_NEQ = '!='

    t_utl_LT = '<'
    t_utl_LTE = '<='
    t_utl_GT = '>'
    t_utl_GTE = '>='

    t_utl_RANGE = r'\.\.'

    # comment (ignore)
    # PROBLEMS: comments *can* be nested
    #          delimiters outside template ([% .. %])
    #          should be ignored
    # probably need another lexer state
    # must come before OP
    def t_utl_COMMENT(self, t):
        r'(/\*(.|\n)*?\*/)'
        t.lexer.lineno += t.value.count('\n')

    def t_utl_ASSIGNOP(self, t):  # pylint: disable=missing-docstring
        r'\+=|-=|\*=|/=|%='
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

    def t_utl_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        # case-insensitive check for reserved words
        t.type = self.reserved.get(t.value.lower(), 'ID')
        return t

    def t_utl_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value)
        return t

    def t_utl_STRING(self, t):
        r'"(?P<dq>[^"]*)"|\'(?P<sq>[^\']*)\''
        dq = t.lexer.lexmatch.group('dq')
        sq = t.lexer.lexmatch.group('sq')
        t.value = dq if dq else sq
        # group() returns None for empty string, so...
        t.value = t.value or ''
        return t

    # Error handling rule
    def t_utl_error(self, t):  # pragma: no cover
        """Callback for character errors in UTL code. Currently, bad input matches to DOCUMENT
        instead, so we have to catch with parser (which should give error if DOCUMENT occurs
        after START_UTL).

        :raises UTLLexerError: always. Handlers will want to call
            :py:meth:`~utl_lex.UTLLexer.skip` if parsing is to be continued.
        """
        raise UTLLexerError("Illegal character '%s' in template code." % t.value[0])

    def t_error(self, t):  # pragma: no cover
        """Report error in DOCUMENT (currently, no errors are defined.)

        :raises UTLLexerError: always."""
        raise UTLLexerError("Illegal character '%s' in non-template text.\n" % t.value[0])
