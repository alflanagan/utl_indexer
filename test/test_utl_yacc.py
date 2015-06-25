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
import sys
from html import unescape  # since we escape entities in DOCUMENT text

import ply

from testplus import unittest_plus, mock_objects

from utl_lib.ast_node import ASTNode
from utl_lib.utl_yacc import UTLParser
from utl_lib.utl_lex import UTLLexer
from utl_lib.utl_parse_handler import UTLParseHandler, UTLParseError
from utl_lib.handler_ast import UTLParseHandlerAST


class UTLParserTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~utl_lib.utl_yacc.UTLParser`."""

    data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_data')

    @classmethod
    def data_file(cls, filename):
        """Returns a full path for test data file named `filename`."""
        return os.path.join(cls.data_dir, filename)

    def test_create(self):
        """Unit tests for :py:meth:`~utl_lib.utl_yacc.UTLParser`."""
        self.assertRaises(TypeError, UTLParser, debug=False)
        parser = UTLParser([], debug=False)
        self.assertIsInstance(parser.lexer, ply.lex.Lexer)
        self.assertSetEqual(set(parser.tokens), set(UTLLexer.tokens) - set(parser.filtered_tokens))
        self.assertSequenceEqual(parser.handlers, [])
        handler = UTLParseHandlerAST()
        parser2 = UTLParser([handler], debug=False)
        self.assertIs(parser2.handlers[0], handler)
        parser3 = UTLParser(handler, debug=False)
        self.assertIs(parser3.handlers[0], handler)
        self.assertRaises(ValueError, UTLParser, ['not_a_handler'], debug=False)
        self.assertRaises(ValueError, UTLParser, [handler, 'not_a_handler'], debug=False)

    def assertMatchesJSON(self, node, expected):  # pylint: disable=invalid-name
        """Asserts that the :py:class:`~utl_lib.ast_node.ASTNode` tree with top node `node`
        matches the JSON data structure in `expected`, given our algorithm for creating JSON
        from an :py:class:`~utl_lib.ast_node.ASTNode`.

        The purpose of this assert is to allow us to express expected results in a simple,
        readable format.
        """
        self.assertIsInstance(node, ASTNode)
        self.assertIsInstance(expected, dict)
        # node is symbol + attributes + children
        # symbol
        self.assertEqual(node.symbol, expected["name"])

        # attributes
        try:
            expected_attrs = expected["attributes"]
        except KeyError:
            expected_attrs = {}
        self.assertSetEqual(set(node.attributes.keys()), set(expected_attrs.keys()))
        for key in node.attributes:
            attr = node.attributes[key]
            if isinstance(attr, ASTNode):  # special case
                self.assertMatchesJSON(attr, expected_attrs[key])
            else:
                # if values are text, either one could be escape()d
                node_value = node.attributes[key]  # escaped depending on source document
                if isinstance(node_value, str):
                    node_value = unescape(node_value)
                expected_value = expected_attrs[key]  # escaped to make it JSON-safe
                if isinstance(expected_value, str):
                    expected_value = unescape(expected_value)
                self.assertEqual(node_value, expected_value)

        # children
        expected_kids = []
        if "children" in expected:
            expected_kids = [kid['name'] for kid in expected["children"]]
        self.assertListEqual([kid.symbol for kid in node.children],
                             expected_kids)
        for index, child in enumerate(node.children):
            self.assertMatchesJSON(child, expected['children'][index])

    def assertJSONFileMatches(self, utl_filename, json_filename):  # pylint: disable=invalid-name
        """Asserts :py:meth:`assertMatchesJSON` on the contents of ``utl_filename`` and
        ``json_filename``, which must exist in our test data directory.

        """
        handler = UTLParseHandlerAST()
        parser = UTLParser([handler], debug=False)
        with open(self.data_file(utl_filename), 'r') as utlin:
            item1 = parser.parse(utlin.read())
        with open(self.data_file(json_filename), 'r') as jsonin:
            expected = json.load(jsonin)
        self.assertMatchesJSON(item1, expected)

    def test_assigns(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with input of assignment
        statements.

        """
        self.assertJSONFileMatches('basic_assign.utl', 'basic_assign.json')

    def test_print_tokens(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with
        ``print_tokens``=:py:attr:`True`.

        """
        parser = UTLParser([], debug=False)
        expected = (('ID', 'a'), ('PLUS', '+'), ('ID', 'b'), ('SEMI', ';'), ('NUMBER', 5.0), ('MINUS', '-'),
                    ('NUMBER', 7.0), ('SEMI', ';'), ('STRING', 'barney rubble'), ('FILTER', '|'),
                    ('ID', 'html'), ('SEMI', ';'), ('ID', 'sally'), ('ASSIGN', '='), ('NUMBER', 12.0),
                    ('DIV', '/'), ('NUMBER', 6.0), ('SEMI', ';'), ('ID', 'empty'), ('ASSIGN', '='),
                    ('STRING', ''), ('SEMI', ';'), ('ID', 'barney'), ('ASSIGN', '='), ('ID', 'fred'),
                    ('TIMES', '*'), ('NUMBER', 3.0), ('SEMI', ';'), ('END_UTL', '%]'),
                    ('DOCUMENT', "\\n here's some text\\n "), ('ID', 'abool'), ('ASSIGN', '='),
                    ('NUMBER', 3.0), ('OP', '=='), ('NUMBER', 4.0), ('SEMI', ';'), ('ID', 'a'),
                    ('ASSIGN', '='), ('NUMBER', 3.0), ('SEMI', ';'), ('ID', 'b'), ('ASSIGN', '='),
                    ('ID', 'fred'), ('SEMI', ';'), ('ID', 'wilma'), ('ASSIGN', '='), ('ID', 'e'),
                    ('LBRACKET', '['), ('NUMBER', 12.0), ('RBRACKET', ']'), ('SEMI', ';'), ('ID', 'c'),
                    ('ASSIGN', '='), ('ID', 'a'), ('TIMES', '*'), ('LPAREN', '('), ('ID', 'a'),
                    ('PLUS', '+'), ('ID', 'b'), ('RPAREN', ')'), ('TIMES', '*'), ('ID', 'b'),
                    ('SEMI', ';'), ('ID', 'd'), ('ASSIGN', '='), ('ID', 'a'), ('TIMES', '*'), ('ID', 'a'),
                    ('PLUS', '+'), ('ID', 'b'), ('TIMES', '*'), ('ID', 'b'), ('SEMI', ';'), ('ID', 'e'),
                    ('ASSIGN', '='), ('ID', 'a'), ('MODULUS', '%'), ('ID', 'b'), ('MINUS', '-'),
                    ('ID', 'b'), ('MODULUS', '%'), ('ID', 'c'), ('SEMI', ';'), ('DEFAULT', 'default'),
                    ('ID', 'a'), ('ASSIGN', '='), ('NUMBER', 3.0), ('SEMI', ';'), ('DEFAULT', 'default'),
                    ('ID', 'b'), ('ASSIGNOP', '+='), ('ID', 'fred'), ('SEMI', ';'),
                    ('DEFAULT', 'default'), ('ID', 'e'), ('ASSIGN', '='), ('ID', 'a'), ('MODULUS', '%'),
                    ('ID', 'b'), ('MINUS', '-'), ('ID', 'b'), ('MODULUS', '%'), ('ID', 'c'),
                    ('SEMI', ';'), ('END_UTL', '%]'), ('DOCUMENT', '\\n'), )

        with mock_objects.MockStream().capture_stdout() as fake_stdout:
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

    def test_syntax_error(self):
        """Unit test :py:meth:`utl_lib.utl_yacc.UTLParser.parse` with invalid syntax."""
        handler = UTLParseHandlerAST()
        parser = UTLParser([handler], debug=False)
        with open(self.data_file('syntax_error.utl'), 'r') as datain:
            self.assertRaises(UTLParseError, parser.parse, datain.read())

    def test_with_multiple_handlers(self):
        handler1 = UTLParseHandlerAST()
        # second handler can't be AST, that one can modify previous results
        handler2 = UTLParseHandler()  # but doing nothing is fine
        # FIXME: need a second handler that returns values from productions
        #     but does not modify existing p[0] values
        parser = UTLParser([handler1, handler2], debug=False)
        # results of parse should depend ONLY on handler1
        with open(self.data_file('macros.utl'), 'r') as utlin:
            item1 = parser.parse(utlin.read())
        with open(self.data_file('macros.json'), 'r') as jsonin:
            expected = json.load(jsonin)
        self.assertMatchesJSON(item1, expected)


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
