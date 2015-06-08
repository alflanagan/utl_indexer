#!/usr/bin/env python3

import os
import sys

from utl_lib.utl_lex import lexer

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: {} [--quiet] utl_file\n".format(os.path.basename(sys.argv[0])))
        sys.stderr.write("       Performs lexical analysis on utl_file, reports ")
        sys.stderr.write("tokens and errors found.\n")
        sys.stderr.write("       With --quiet, reports errors only.\n")
        sys.exit(1)

    with open(sys.argv[1], 'r') as utl_in:
        lexer.input(utl_in.read())

    if '--quiet' not in sys.argv:
        while True:
            tok = lexer.token()
            if not tok:
                break      # No more input
            print(tok)
