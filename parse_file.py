#!/usr/bin/env python3
"""Routines to implement a yacc-like parser for Townnews' UTL template language"""

import argparse
import sys
import os

from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_parse_handler import UTLParseError
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.handler_parse_tree import UTLParseHandlerParseTree
from utl_lib.handler_print_productions import UTLPrintProductionsHandler


def get_args():
    """Parses command-line arguments, returns namespace with values."""
    parser = argparse.ArgumentParser(description="Parses a UTL file into one of several formats.")
    parser.add_argument('utl_file', type=argparse.FileType('r'), nargs='+',
                        help="One or more UTL template files.")
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
    parser.add_argument('--verbose', action='store_true',
                        help="Enable output about conflicts, and create parser.out file.")
    return parser.parse_args()


def do_parse(program_file, args):
    """Open a file, parse it, return resulting parse."""
    if args.ast:
        handlers = [UTLParseHandlerAST(exception_on_error=True)]
    elif args.printonly:
        handlers = [UTLPrintProductionsHandler(exception_on_error=True)]
    else:
        handlers = [UTLParseHandlerParseTree(exception_on_error=True)]

    if args.print and not args.printonly:
        handlers.append(UTLPrintProductionsHandler(exception_on_error=True))

    program_text = program_file.read()

    myparser = UTLParser(handlers, args.verbose)
    results = None

    def error_handler(the_parser, lex_token, line_offset, source_file):
        """Handle a syntax error encountered during parsing.

        :param utl_lib.utl_yacc.UTLParser the_parser: Parser object which
            detected the error.

        :param LexToken lex_token: The current token when the error was
            detected.

        :param int line_offset: The character offset within the line
            (`lex_token.lineno`) at which the error was detected.

        :param str source_file: The name of the file (or whatever) being
            parsed.

        """
        pass


    # setting exception_on_error=True then catching UTLParseError allows us to associate
    # file name with error, but only reports first error.
    # TODO: UTLParseHandler should accept a error function callback
    # or, put p_error in mixin classes
    try:
        results = myparser.parse(program_text, debug=args.debug, print_tokens=args.show_lex,
                                 filename=program_file.name)
    except UTLParseError as upe:
        sys.stderr.write("Parse error in file '{}'.\n".format(program_file.name))
        sys.stderr.write(str(upe) + "\n")

    if results:
        print(results.json_format() if args.json else results.format())
    elif not args.printonly:
        sys.stderr.write('Parse FAILED!\n')


def main(args):
    """Main function. Optionally prints lexical analysis, then prints parse tree."""
    for utl_file in args.utl_file:
        do_parse(utl_file, args)


if __name__ == '__main__':
    main(get_args())
