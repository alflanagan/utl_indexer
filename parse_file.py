#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import sys
import os

from utl_lib.utl_lex import UTLLexer
from utl_lib.utl_yacc import parser


def do_parse(filename):
    """Open a file, parse it, return resulting parse."""

    with open(filename, 'r') as utl_in:
        parser().parse(utl_in.read(), tracking=True, lexer=UTLLexer().lexer)


def show_lex(filename):
    '''Run lexical analysis on file `filename`, print out token list.'''
    new_lexer = UTLLexer()
    with open(filename, 'r') as utl_in:
        new_lexer.input(utl_in.read())
    tok = new_lexer.token()
    while tok:
        print(tok)
        tok = new_lexer.token()


if __name__ == '__main__':

    if len(sys.argv) < 2:
        sys.stderr.write("Usage: {} utl_file [--show-lex]\n".format(os.path.basename(sys.argv[0])))
        sys.stderr.write("       Parses a UTL file and outputs info for indexing.\n")
        sys.exit(1)

    if '--show-lex' in sys.argv:
        show_lex(sys.argv[1])

    do_parse(sys.argv[1])
