#!/usr/bin/env python3
"""Program to generate a macro declaration and use cross-reference from a UTL file."""

import argparse
import sys

from utl_lib.utl_yacc import UTLParser
from utl_lib.handler_macro_xref import UTLParseHandlerMacroXref

def get_args():
    """Parses command-line arguments, returns namespace with values."""
    parser = argparse.ArgumentParser(description="Parses a UTL file into one of several formats.")
    parser.add_argument('utl_file', type=argparse.FileType('r'),
                        help="A UTL template file.")
    parser.add_argument('--debug', action='store_true',
                        help="Print debugging info of parse process.")
    parser.add_argument('--json', action='store_true',
                        help="Format output as JSON (default: human-readable)")
    return parser.parse_args()


def do_parse(program_text, args):
    """Open a file, parse it, return resulting parse."""
    handler = UTLParseHandlerMacroXref()
    myparser = UTLParser([handler])
    myparser.parse(program_text, debug=args.debug, print_tokens=False)
    if handler.macro_defns:
        print("-- MACROS DEFINED --")
    for defn in handler.macro_defns:
        print(defn)
    if handler.macro_calls:
        print("-- MACROS CALLED --")
    for call in handler.macro_calls:
        print(call)


def main(args):
    """Main function. Reads file, calls parse routine."""
    utl_text = args.utl_file.read()

    do_parse(utl_text, args)


if __name__ == '__main__':
    main(get_args())
