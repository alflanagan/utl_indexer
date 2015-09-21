#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import argparse
import sys
import os

from utl_lib.utl_yacc import UTLParser
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.handler_parse_tree import UTLParseHandlerParseTree
from utl_lib.handler_print_productions import UTLPrintProductionsHandler


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
    parser.add_argument('--print', action='store_true',
                        help="Print out each production as it is encountered")
    parser.add_argument('--printonly', action='store_true',
                        help="Print each production as encountered, don't print parse result")
    return parser.parse_args()


def do_parse(program_text, args):
    """Open a file, parse it, return resulting parse."""
    if args.ast:
        handlers = [UTLParseHandlerAST()]
    elif args.printonly:
        handlers = [UTLPrintProductionsHandler()]
    else:
        handlers = [UTLParseHandlerParseTree()]

    if args.print and not args.printonly:
        handlers.append(UTLPrintProductionsHandler())

    myparser = UTLParser(handlers)
    results = myparser.parse(program_text, debug=args.debug, print_tokens=args.show_lex,
                             filename=os.path.basename(args.utl_file.name))
    if results:
        print(results.json_format() if args.json else results.format())
    elif not args.printonly:
        sys.stderr.write('Parse FAILED!\n')


def main(args):
    """Main function. Optionally prints lexical analysis, then prints parse tree."""
    utl_text = args.utl_file.read()

    do_parse(utl_text, args)


if __name__ == '__main__':
    main(get_args())
