#!/usr/bin/env python3
"""Script to run parser over a UTL file, solely to check syntax."""
import sys
import argparse

from utl_lib.utl_yacc2 import UTLParser
from utl_lib.test_yacc import TestParser
# parent class does nothing, which is exactly what we want
from utl_lib.utl_parse_handler import UTLParseHandler, UTLParseError


def get_args():
    """Parses command-line arguments, returns namespace with values."""
    parser = argparse.ArgumentParser(description="Validates a UTL file and reports syntax errors.")
    parser.add_argument('utl_file', type=argparse.FileType('r'),
                        help="A UTL template file.")
    parser.add_argument('--debug', action='store_true',
                        help="Print debugging info of parse process.")
    return parser.parse_args()


def main(args):
    """Main function. Opens file, parses it."""
    myparser = UTLParser([UTLParseHandler()])
    #myparser = TestParser()
    myparser.parse(args.utl_file.read(), debug=args.debug)
    if myparser.error_count > 0:
        print("{} contained {} syntax errors!".format(args.utl_file.name, myparser.error_count))
    else:
        print("{} appears valid.".format(args.utl_file.name))

if __name__ == '__main__':
    main(get_args())
