#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import argparse
import sys

from utl_lib.utl_yacc import UTLParser
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.handler_parse_tree import UTLParseHandlerParseTree


def get_args():
    """Parses command-line arguments, returns namespace with values."""
    parser = argparse.ArgumentParser(description="Parses a UTL file into one of several formats.")
    parser.add_argument('utl_file', type=argparse.FileType('r'),
                        help="A UTL template file.")
    parser.add_argument('--show-lex', action='store_true',
                        help="Show lexical analysis prior to parsing.")
    parser.add_argument('--debug', action='store_true',
                        help="Print debugging info of parse process.")
    parser.add_argument('--json', action='store_true',
                        help="Format output as JSON (default: human-readable)")
    parser.add_argument('--ast', action='store_true',
                        help="Generate an Abstract Syntax Tree (default: parse tree)")
    return parser.parse_args()


def do_parse(program_text, args):
    """Open a file, parse it, return resulting parse."""
    if args.ast:
        handler = UTLParseHandlerAST()
    else:
        handler = UTLParseHandlerParseTree()
    myparser = UTLParser([handler])
    results = myparser.parse(program_text, debug=args.debug, print_tokens=args.show_lex)
    if results:
        print(results.json_format() if args.json else results.format())
    else:
        sys.stderr.write('Parse FAILED!\n')


def main(args):
    """Main function. Optionally prints lexical analysis, then prints parse tree."""
    utl_text = args.utl_file.read()

    do_parse(utl_text, args)


if __name__ == '__main__':
    main(get_args())
