#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lib.ast_node`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

from testplus import unittest_plus

from utl_lib.ast_node import ASTNode, ASTNodeFormatter


class ASTNodeTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~utl_lib.ast_node.ASTNode`."""

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.ast_node.ASTNode`."""
        item1 = ASTNode('symbol', False)
        self.assertEqual(item1.symbol, 'symbol')
        self.assertDictEqual(item1.attributes, {})
        self.assertSequenceEqual(item1.children, [])
        self.assertFalse(item1.terminal)
        self.assertIsNone(item1.parent)
        item2 = ASTNode('fred', True, {'a': 2, 'b': 'wilma'}, [item1])
        self.assertEqual(item2.symbol, 'fred')
        # actually, a non-terminal w/out kids is OK, terminal w/kids, probably not
        self.assertTrue(item2.terminal)
        self.assertDictEqual(item2.attributes, {'a': 2, 'b': 'wilma'})
        self.assertSequenceEqual(item2.children, [item1])
        self.assertIs(item2.children[0].parent, item2)
        item3 = ASTNode('barney', False, {}, [item1, item2])
        self.assertSequenceEqual(item3.children, [item1, item2])

    def test_add_child(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.add_child`."""
        item1 = ASTNode("fred", False, {'name': "Flintstone",}, [])
        item2 = ASTNode("wilma", True, {}, [ASTNode("pebbles", False)])
        item3 = ASTNode("barney", False)
        item4 = ASTNode("flintstones", False, {}, [item1])
        item1.add_child(item2)
        self.assertSequenceEqual(item1.children, [item2])
        self.assertIs(item2.parent, item1)
        item1.add_child(item3)  # Barney didn't know it, but...
        self.assertSequenceEqual(item1.children, [item2, item3])
        for kid in item1.children:
            self.assertIs(kid.parent, item1)
        item4.add_child(item2)
        self.assertSequenceEqual(item4.children, [item1, item2])
        self.assertIs(item1.parent, item4)
        #Got to make sure that item2 stored as child of item1 still shows parent item1
        self.assertIs(item2.parent, item1)
        self.assertIs(item2, item1.children[0])
        self.assertIsNot(item2, item4.children[1])
        self.assertIs(item1.children[0].parent, item1)


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
