#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from utl_lib.utl_lex import UTLLexer



class UTLLexerComments(UTLLexer):
    """A version of :py:class:`utl_lib.utl_lex.UTLLexer` that returns a token for comments,
    instead of ignoring them.

    """

    # PROBLEMS: comments *can* be nested
    #          delimiters outside template ([% .. %]) should be ignored
    # probably need another lexer state
    def t_utl_COMMENT(self, t):
        r'(/\*(.|\n)*?\*/)'
        return t
