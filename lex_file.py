#!/usr/bin/env python3
"""A script to run lexical analysis on a file, and print results."""
import os
import sys

from utl_lib.utl_lex import UTLLexer


def main(filename, quiet=False):
    """Lexically analyse a file.

    :param str filename: The name of an existing UTL file.

    :param boolean quiet: If True, errors will be reported to :py:obj:`sys.stderr` but tokens
        will not be printed.
    """
    lexer = UTLLexer()

    with open(filename, 'r') as utl_in:
        lexer.input(utl_in.read())

    if '--quiet' not in sys.argv:
        tok = lexer.token()
        while tok:
            print(tok)
            tok = lexer.token()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: {} [--quiet] utl_file\n".format(os.path.basename(sys.argv[0])))
        sys.stderr.write("       Performs lexical analysis on utl_file, reports ")
        sys.stderr.write("tokens and errors found.\n")
        sys.stderr.write("       With --quiet, reports errors only.\n")
        sys.exit(1)

    main(sys.argv[1])
