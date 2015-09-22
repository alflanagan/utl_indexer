#!/usr/bin/env python3
"""Program to generate a macro declaration and use cross-reference from a UTL file."""

import argparse
import os
from collections import defaultdict

from utl_lib.macro_xref import UTLMacroXref
from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.utl_yacc import UTLParser


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
    handler = UTLParseHandlerAST()
    myparser = UTLParser([handler])
    utldoc = myparser.parse(program_text, debug=args.debug, print_tokens=False,
                            filename=os.path.basename(args.utl_file.name))
    xref = UTLMacroXref(utldoc, program_text)
    if xref.macros:
        print("-- MACROS DEFINED --")
        for macro in xref.macros:
            # print('-' * 120)
            print('    {}'.format(macro))
    if xref.references:
        print('-- MACRO REFS --')
        lines_summary = defaultdict(list)
        for ref in xref.references:
            lines_summary[ref["macro"]].append(ref["line"])
        for mname in lines_summary:
            print('    {}: {}'.format(mname, lines_summary[mname]))


def main(args):
    """Main function. Reads file, calls parse routine."""
    utl_text = args.utl_file.read()

    do_parse(utl_text, args)


if __name__ == '__main__':
    main(get_args())
