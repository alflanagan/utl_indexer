#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Class for support of unit tests for :py:mod:`utl_lib` package.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods
import os
import json
from html import unescape  # since we escape entities in DOCUMENT text

from testplus import unittest_plus, mock_objects

from utl_lib.ast_node import ASTNode
from utl_lib.utl_yacc import UTLParser
from utl_lib.handler_parse_tree import UTLParseHandlerParseTree


class TestCaseUtl(unittest_plus.TestCasePlus):
    """A base class providing :py:mod:`unittest`-like assertions to aid testing of
    :py:mod:`utl_lib` code.

    """

    data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_data')

    @classmethod
    def data_file(cls, filename):
        """Returns a full path for test data file named `filename`."""
        return os.path.join(cls.data_dir, filename)

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

    def assertJSONFileMatches(self, handler, utl_filename, json_filename):  # pylint: disable=invalid-name
        """Asserts :py:meth:`assertMatchesJSON` on the contents of ``utl_filename`` and
        ``json_filename``, which must exist in our test data directory.

        """
        parser = UTLParser([handler], debug=False)
        with open(self.data_file(utl_filename), 'r') as utlin:
            item1 = parser.parse(utlin.read())
        with open(self.data_file(json_filename), 'r') as jsonin:
            expected = json.load(jsonin)
        self.assertMatchesJSON(item1, expected)


# re-export other stuff from unittest_plus, so callers don't have to import it
main = unittest_plus.main

mock_objects = mock_objects

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
