#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import argparse

from utl_lib.utl_lex import UTLLexer
from utl_lib.utl_yacc_mini import UTLParser
from utl_lib.ast_node import ASTNodeFormatter


def get_args():
    """Parses command-line arguments, returns namespace with values."""
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
    print(ASTNodeFormatter(results).format())


def show_lex(program_text):
    '''Run lexical analysis on stream, print out token list.'''
    new_lexer = UTLLexer()
    new_lexer.input(program_text)
    tok = new_lexer.token()
    while tok:
        print(tok)
        tok = new_lexer.token()


def main(args):
    """Main function. Optionally prints lexical analysis, then prints parse tree."""
    utl_text = args.utl_file.read()

    if args.show_lex:
        show_lex(utl_text)

    do_parse(utl_text, args.debug)


if __name__ == '__main__':
    main(get_args())
