#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lib.utl_yacc`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

import json
from testplus import unittest_plus

from utl_lib.ast_node import ASTNode, ASTNodeError
from utl_lib.utl_yacc import UTLParser


class UTLParserTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~utl_lib.utl_yacc.UTLParser`."""

    def assertMatchesJSON(self, node, expected):
        """Asserts that the ASTNode tree with top node `node` matches the JSON data structure in
        `expected`, given our algorithm for creating JSON from an ASTNode.

        The purpose of this assert is to allow us to express expected results in a simple,
        readable format.
        """
        self.assertIsInstance(node, ASTNode)
        self.assertIsInstance(expected, dict)
        self.assertEqual(node.symbol, expected["name"])
        self.assertDictEqual(node.attributes,
                             expected['attributes'] if "attributes" in expected else {})
        expected_kids = []
        if "children" in expected:
            expected_kids = [kid['name'] for kid in expected["children"]]
        self.assertListEqual([kid.symbol for kid in node.children],
                             expected_kids)
        for index, child in enumerate(node.children):
            self.assertMatchesJSON(child, expected['children'][index])

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.utl_yacc.UTLParser`."""
        parser = UTLParser(debug=False)
        with open('test_data/basic_assign.utl', 'r') as datain:
            item1 = parser.parse(datain.read())
        isinstance(item1, ASTNode)
        with open('test_data/basic_assign.json', 'r') as bain:
            expected = json.load(bain)
        self.assertMatchesJSON(item1, expected)

if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
