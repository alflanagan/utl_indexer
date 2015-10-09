#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lib.utl_yacc`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods
import os
import json
import re

import ply

from utl_test import utl_parse_test
from testplus.mock_objects import MockStream
from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_lex import UTLLexer
from utl_lib.utl_parse_handler import UTLParseHandler, UTLParseError
from utl_lib.handler_parse_tree import UTLParseHandlerParseTree


class UTLParserTestCase(utl_parse_test.TestCaseUTL):
    """Unit tests for class :py:class:`~utl_lib.utl_yacc.UTLParser`."""

    data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_data')

    @classmethod
    def data_file(cls, filename):
        """Returns a full path for test data file named `filename`."""
        return os.path.join(cls.data_dir, filename)

    def assertJSONFileMatches(self, utl_filename, json_filename):  # pylint: disable=W0221
        """Wrapper function that supplies correct handler to
        :py:meth:`utl_lib.utl_parse_test.assertJSONFileMatches`.

        """
        return super().assertJSONFileMatches(UTLParseHandlerParseTree(),
                                             utl_filename, json_filename)

    def test_create(self):
        """Unit tests for :py:meth:`~utl_lib.utl_yacc.UTLParser`."""
        parser = UTLParser([], debug=False)
        self.assertIsInstance(parser.lexer, ply.lex.Lexer)
        self.assertSetEqual(set(parser.tokens), set(UTLLexer.tokens) - set(parser.filtered_tokens))
        self.assertSequenceEqual(parser.handlers, [])
        handler = UTLParseHandlerParseTree()
        parser2 = UTLParser([handler], debug=False)
        self.assertIs(parser2.handlers[0], handler)
        parser3 = UTLParser(handler, debug=False)
        self.assertIs(parser3.handlers[0], handler)
        self.assertRaises(ValueError, UTLParser, ['not_a_handler'], debug=False)
        self.assertRaises(ValueError, UTLParser, [handler, 'not_a_handler'], debug=False)

    def test_assigns(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with input of assignment
        statements.

        """
        self.assertJSONFileMatches('basic_assign.utl', 'basic_assign.json')

    # def test_double_assigns(self):
    #     """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with input of assignment
    #     statements using the operator '=' more than once ([% a = b = c = 5; %]).

    #     """
    #     self.assertJSONFileMatches('double_assign.utl', 'double_assign.json')

    def test_print_tokens(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with
        ``print_tokens``=:py:attr:`True`.

        """
        parser = UTLParser([], debug=False)
        expected = (('ID', 'a'), ('PLUS', '+'), ('ID', 'b'), ('SEMI', ';'), ('NUMBER', 5.0),
                    ('MINUS', '-'), ('NUMBER', 7.0), ('SEMI', ';'), ('STRING', 'barney rubble'),
                    ('FILTER', '|'), ('ID', 'html'), ('SEMI', ';'), ('ID', 'sally'), ('DOT', '.'),
                    ('ID', 'isfine'), ('ASSIGN', '='), ('NUMBER', 12.0), ('DIV', '/'),
                    ('NUMBER', 6.0), ('SEMI', ';'), ('ID', 'sally'), ('DOT', '.'), ('ID', 'fineis'),
                    ('ASSIGN', '='), ('STRING', 'bat'), ('SEMI', ';'), ('ID', 'sally'),
                    ('OP', 'is '), ('ID', 'fine'), ('SEMI', ';'), ('ID', 'fred'), ('DOT', '.'),
                    ('ID', 'breakthis'), ('ASSIGN', '='), ('NUMBER', 0.0), ('SEMI', ';'),
                    ('ID', 'fred'), ('DOT', '.'), ('ID', 'thisbreak'), ('ASSIGN', '='),
                    ('NUMBER', 2.0), ('SEMI', ';'), ('ID', 'empty'), ('ASSIGN', '='),
                    ('STRING', ''), ('SEMI', ';'), ('ID', 'barney'), ('ASSIGN', '='),
                    ('ID', 'fred'),
                    ('TIMES', '*'), ('NUMBER', 3.0), ('SEMI', ';'), ('END_UTL', '%]'),
                    ('DOCUMENT', "\\n here's some text\\n "), ('ID', 'abool'), ('ASSIGN', '='),
                    ('NUMBER', 3.0), ('OP', '=='), ('NUMBER', 4.0), ('SEMI', ';'), ('ID', 'a'),
                    ('ASSIGN', '='), ('NUMBER', 3.0), ('SEMI', ';'), ('ID', 'b'), ('ASSIGN', '='),
                    ('ID', 'fred'), ('SEMI', ';'), ('ID', 'wilma'), ('ASSIGN', '='), ('ID', 'e'),
                    ('LBRACKET', '['), ('NUMBER', 12.0), ('RBRACKET', ']'), ('SEMI', ';'),
                    ('ID', 'c'),
                    ('ASSIGN', '='), ('ID', 'a'), ('TIMES', '*'), ('LPAREN', '('), ('ID', 'a'),
                    ('PLUS', '+'), ('ID', 'b'), ('RPAREN', ')'), ('TIMES', '*'), ('ID', 'b'),
                    ('SEMI', ';'), ('ID', 'd'), ('ASSIGN', '='), ('ID', 'a'), ('TIMES', '*'),
                    ('ID', 'a'), ('PLUS', '+'), ('ID', 'b'), ('TIMES', '*'), ('ID', 'b'),
                    ('SEMI', ';'), ('ID', 'e'), ('ASSIGN', '='), ('ID', 'a'), ('MODULUS', '%'),
                    ('ID', 'b'), ('MINUS', '-'), ('ID', 'b'), ('MODULUS', '%'), ('ID', 'c'),
                    ('SEMI', ';'), ('DEFAULT', 'default'), ('ID', 'a'), ('ASSIGN', '='),
                    ('NUMBER', 3.0), ('SEMI', ';'), ('DEFAULT', 'default'), ('ID', 'b'),
                    ('ASSIGNOP', '+='), ('ID', 'fred'), ('SEMI', ';'), ('DEFAULT', 'default'),
                    ('ID', 'e'), ('ASSIGN', '='), ('ID', 'a'), ('MODULUS', '%'), ('ID', 'b'),
                    ('MINUS', '-'), ('ID', 'b'), ('MODULUS', '%'), ('ID', 'c'), ('SEMI', ';'),
                    ('ID', 'array'), ('ASSIGN', '='), ('LBRACKET', '['), ('NUMBER', 1.0),
                    ('COMMA', ','), ('NUMBER', 2.0), ('COMMA', ','), ('STRING', 'fred'),
                    ('COMMA', ','), ('NUMBER', 3.0), ('COMMA', ','), ('ID', 'wilma'),
                    ('LPAREN', '('), ('NUMBER', 7.0), ('RPAREN', ')'), ('FILTER', '|'),
                    ('ID', 'fred'), ('RBRACKET', ']'), ('SEMI', ';'), ('ID', 'obj'),
                    ('ASSIGN', '='),
                    ('LBRACKET', '['), ('STRING', 'one'), ('COLON', ':'), ('NUMBER', 2.0),
                    ('COMMA', ','), ('STRING', 'two'), ('COLON', ':'), ('NUMBER', 3.0),
                    ('RBRACKET', ']'), ('SEMI', ';'), ('ID', 'obj'), ('DOT', '.'), ('ID', 'one'),
                    ('ASSIGN', '='), ('NUMBER', 3.0), ('SEMI', ';'), ('ID', 'obj'),
                    ('LBRACKET', '['), ('STRING', 'two'), ('RBRACKET', ']'), ('ASSIGN', '='),
                    ('NUMBER', 7.0), ('SEMI', ';'), ('ID', 'n'), ('ASSIGN', '='), ('LBRACKET', '['),
                    ('RBRACKET', ']'), ('SEMI', ';'), ('END_UTL', '%]'), ('DOCUMENT', '\\n'), )

        with utl_parse_test.mock_objects.MockStream().capture_stdout() as fake_stdout:
            with open(self.data_file('basic_assign.utl'), 'r') as utlin:
                parser.parse(utlin.read(), debug=False, print_tokens=True)
            for ndx, line in enumerate(fake_stdout.logged.split('\n')):
                if line:
                    match = re.search(r'LexToken\(([A-Z_]+), ?\'?([^\',]*)\'?,', line)
                    if not match:
                        match = re.search(r'LexToken\(([A-Z_]+), ?"?([^",]*)"?,', line)
                    if not match:
                        self.fail('Unable to match output line: {}'.format(line))
                    self.assertEqual(match.group(1), expected[ndx][0])
                    if match.group(1) != 'COMMA':  # our brain-dead RE misses the comma
                        self.assertEqual(match.group(2), str(expected[ndx][1]))

    def test_calls(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with macro calls."""
        self.assertJSONFileMatches('calls.utl', 'calls.json')

    def test_for_stmts(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with for statements."""
        self.assertJSONFileMatches('for_stmt.utl', 'for_stmt.json')

    def test_if_stmts(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with if statements."""
        self.assertJSONFileMatches('if_stmts.utl', 'if_stmts.json')

    def test_include_stmts(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with include statements."""
        self.assertJSONFileMatches('includes.utl', 'includes.json')

    def test_keywords(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with various keywords not
        otherwise tested.

        """
        self.assertJSONFileMatches('keywords.utl', 'keywords.json')

    def test_macro(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with macro definitions."""
        self.assertJSONFileMatches('macros.utl', 'macros.json')

    def test_while(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with a while statement."""
        self.assertJSONFileMatches('while.utl', 'while.json')

    def test_unary_expr(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with expressions containing
        unary operators.

        """
        self.assertJSONFileMatches('unary_exprs.utl', 'unary_exprs.json')

    def test_syntax_error(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with invalid syntax."""
        handler = UTLParseHandlerParseTree(exception_on_error=True)
        parser = UTLParser([handler], debug=False)
        with open(self.data_file('syntax_error.utl'), 'r') as datain:
            self.assertRaises(UTLParseError, parser.parse, datain.read())
        # just to verify that symstack works
        self.assertEqual(parser.symstack[0].type, '$end')

    def test_syntax_error_stderr(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with invalid syntax when no
        handlers are defined.

        """
        parser = UTLParser([], debug=False)
        with utl_parse_test.mock_objects.MockStream().capture_stderr() as fake_stderr:
            with open(self.data_file('syntax_error.utl'), 'r') as datain:
                parser.parse(datain.read())
        self.assertIn('in statement', fake_stderr.logged)
        self.assertIn('line 2', fake_stderr.logged)

    def _check_multiple_handlers(self, parser, filepart):
        """Helper function: use parser to parse UTL file named `filepart`.utl, compare to JSON
        results in file `filepart`.json.

        """
        with open(self.data_file(filepart + '.utl'), 'r') as utlin:
            item1 = parser.parse(utlin.read(), filename=filepart+'.utl')
        with open(self.data_file(filepart + '.json'), 'r') as jsonin:
            expected = json.load(jsonin)
        self.assertMatchesJSON(item1, expected)

    def test_with_multiple_handlers(self):
        """Unit test of :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with more than one handler
        attached.

        """
        handler1 = UTLParseHandlerParseTree()
        # parse tree as second handler could modify previous results
        handler2 = UTLParseHandler()  # but doing nothing is fine
        # FIXME: need a second handler that returns values from productions
        #     but does not modify existing p[0] values
        parser = UTLParser([handler1, handler2], debug=False)
        # results of parse should depend ONLY on handler1
        self._check_multiple_handlers(parser, 'basic_assign')
        parser.restart()
        self._check_multiple_handlers(parser, 'calls')
        parser.restart()
        self._check_multiple_handlers(parser, 'for_stmt')
        parser.restart()
        self._check_multiple_handlers(parser, 'if_stmts')
        parser.restart()
        self._check_multiple_handlers(parser, 'includes')
        parser.restart()
        self._check_multiple_handlers(parser, 'keywords')
        parser.restart()
        self._check_multiple_handlers(parser, 'macros')
        del parser.handlers
        self.assertIsNone(parser.handlers)
        parser.handlers = None
        self.assertSequenceEqual(parser.handlers, [])

    def test_empty_file(self):
        """Test :py:meth:`~utl_lib.utl_yacc.UTLParser` when the input file is zero-byte."""
        handler = UTLParseHandlerParseTree()
        parser = UTLParser([handler], debug=False)
        utl_doc = parser.parse('', filename='empty.utl')
        self.assertEqual(utl_doc.symbol, 'utldoc')
        self.assertSequenceEqual(utl_doc.children, [])
        self.assertDictEqual(dict(utl_doc.attributes),
                             {'end': 1, 'file': 'empty.utl', 'start': 1, 'line': 1})

    def test_restart(self):
        """Unit tests for :py:meth:`~utl_lib.utl_yacc.UTLParser.restart`."""
        handler = UTLParseHandlerParseTree()
        parser = UTLParser([handler], False)
        testpart1 = "[% macro fred; echo 'hello'; bite it; echo 'goodbye'; end; %]"
        with MockStream().capture_stderr() as _:
            parser.parse(testpart1, filename='fred.utl')
        # print(fred)
        self.assertEqual(parser.filename, 'fred.utl')
        self.assertEqual(parser.error_count, 2)
        self.assertEqual(parser.lexer.lexpos, 63)
        parser.parse("[% macro jane; echo 'hi'; end; %]")
        self.assertEqual(parser.filename, '')
        self.assertEqual(parser.error_count, 2)
        self.assertEqual(parser.lexer.lexpos, 35)
        self.assertIs(parser.handlers[0], handler)
        parser.restart([])
        parser.parse("[% macro jane; echo 'hi'; end; %]")
        self.assertEqual(parser.error_count, 0)
        self.assertSequenceEqual(parser.handlers, [])
        parser = UTLParser([handler], False)
        # verify restart on parser that's never run
        parser.restart()
        # and we don't replace handlers
        self.assertIs(parser.handlers[0], handler)


if __name__ == '__main__':
    utl_parse_test.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
