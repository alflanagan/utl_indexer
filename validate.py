#!/usr/bin/env python3
"""Script to run parser over a UTL file, solely to check syntax."""
import sys
import argparse

from utl_lib.utl_yacc import UTLParser
# parent class for handlers does nothing, which is exactly what we want
from utl_lib.utl_parse_handler import UTLParseHandler, UTLParseError


def get_args():
    """Parses command-line arguments, returns namespace with values."""
    parser = argparse.ArgumentParser(description="Validates a UTL file and reports syntax errors.")
    parser.add_argument('utl_file', type=argparse.FileType('r'),
                        help="A UTL template file.")
    parser.add_argument('--debug', action='store_true',
                        help="Print debugging info of parse process.")
    parser.add_argument('--stop-on-error', action='store_true',
                        help="Stop after first error encountered (default: report and continue)")
    return parser.parse_args()


def main(args):
    """Main function. Opens file, parses it.

    :param argparse.NameSpace args: The parsed command-line arguments.

    """
    myparser = UTLParser([UTLParseHandler(args.stop_on_error)])
    try:
        if args.stop_on_error:
            try:
                myparser.parse(args.utl_file.read(), debug=args.debug)
            except UTLParseError as upe:
                sys.stderr.write("{} syntax error: {}\n".format(args.utl_file.name, upe))
                sys.exit(1)
        else:
            myparser.parse(args.utl_file.read(), debug=args.debug)
            if myparser.error_count > 0:
                print("{} contained {} syntax errors!"
                      "".format(args.utl_file.name, myparser.error_count))
                sys.exit(1)
            else:
                print("{} appears valid.".format(args.utl_file.name))
    except UnicodeDecodeError as ude:
        sys.stderr.write("Unicode error in '{}': {}\n"
                         "".format(args.utl_file.name, ude))
        sys.exit(2)


if __name__ == '__main__':
    main(get_args())
