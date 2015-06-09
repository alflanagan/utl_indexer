#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import sys
import os
import argparse


from utl_lib.utl_lex import UTLLexer
from utl_lib.utl_yacc import UTLParser


def get_args():
    parser = argparse.ArgumentParser(description="Parses a UTL file.")
    parser.add_argument('utl_file', type=argparse.FileType('r'),
                        help="A UTL template file.")
    parser.add_argument('--show-lex', action='store_true',
                        help="Show lexical analysis prior to parsing.")
    parser.add_argument('--debug', action='store_true',
                        help="Print debugging info of parse process.")
    return parser.parse_args()


def do_parse(program_text, debug):
    """Open a file, parse it, return resulting parse."""

    myparser = UTLParser()
    results = myparser.parse(program_text, debug=debug)
    print(results)
    for node in myparser.asts:
        print(node)
    print('{0} Symbols {0}'.format('=' * 12))
    for symbol_name in myparser.symbol_table:
        print('{}: {}'.format(symbol_name, myparser.symbol_table[symbol_name]))


def show_lex(program_text):
    '''Run lexical analysis on stream, print out token list.'''
    new_lexer = UTLLexer()
    new_lexer.input(program_text)
    tok = new_lexer.token()
    while tok:
        print(tok)
        tok = new_lexer.token()


def main(args):
    utl_text = args.utl_file.read()

    if args.show_lex:
        show_lex(utl_text)

    do_parse(utl_text, args.debug)


if __name__ == '__main__':
    main(get_args())
