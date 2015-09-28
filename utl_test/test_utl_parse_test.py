#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_indexer.test.utl_parse_test`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods,invalid-name
import json

from utl_test import utl_parse_test
from utl_lib.ast_node import ASTNode
from utl_lib.handler_parse_tree import UTLParseHandlerParseTree


class TestCaseUTLTestCase(utl_parse_test.TestCaseUTL):
    """Unit tests for class :py:class:`~utl_indexer.test.utl_parse_test.TestCaseUTL`."""

    def test_assertMatchesJSON(self):
        """Unit test for :py:meth:`utl_indexer.test.utl_parse_test.TestCaseUTL.assertMatchesJSON`.

        """
        self.assertEqual(5, 5)
        expected1 = {"name": "id", "attributes": {"symbol": "fred"}}
        node1 = ASTNode("id", {"symbol": "fred"}, [])
        self.assertMatchesJSON(node1, expected1)
        node2 = ASTNode('expr',
                        {'value': ASTNode('literal', {'value': 5}, [])},
                        [])
        expected2 = {"name": "expr",
                     "attributes": {"value": {"name": "literal",
                                              "attributes": {"value": 5}},},}
        self.assertMatchesJSON(node2, expected2)

    def test_assertJSONFileMatches(self):
        """Unit tests for
        :py:meth:`utl_indexer.test.utl_parse_test.TestCaseUTL.assertJSONFileMatches`.

        """
        self.assertJSONFileMatches(UTLParseHandlerParseTree(), 'while.utl', 'while.json')


if __name__ == '__main__':
    utl_parse_test.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
