#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import argparse
import sys

from utl_lib.utl_yacc import UTLParser
from utl_lib.ast_node import ASTNodeFormatter, ASTNodeJSONFormatter
from utl_lib.handler_ast import UTLParseHandlerAST


def get_args():
    """Parses command-line arguments, returns namespace with values."""
    parser = argparse.ArgumentParser(description="Parses a UTL file.")
    parser.add_argument('utl_file', type=argparse.FileType('r'),
                        help="A UTL template file.")
    parser.add_argument('--show-lex', action='store_true',
                        help="Show lexical analysis prior to parsing.")
    parser.add_argument('--debug', action='store_true',
                        help="Print debugging info of parse process.")
    parser.add_argument('--json', action='store_true',
                        help="Format output as JSON (default: human-readable)")
    return parser.parse_args()


def do_parse(program_text, args):
    """Open a file, parse it, return resulting parse."""

    myparser = UTLParser([UTLParseHandlerAST()])
    results = myparser.parse(program_text, debug=args.debug, print_tokens=args.show_lex)
    if results:
        if args.json:
            print(ASTNodeJSONFormatter(results).format())
        else:
            print(ASTNodeFormatter(results).format())
    else:
        sys.stderr.write('Parse FAILED!\n')


def main(args):
    """Main function. Optionally prints lexical analysis, then prints parse tree."""
    utl_text = args.utl_file.read()

    do_parse(utl_text, args)


if __name__ == '__main__':
    main(get_args())
