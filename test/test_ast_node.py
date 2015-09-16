#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lib.ast_node`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

import json
from testplus import unittest_plus

from utl_lib.ast_node import ASTNode, ASTNodeError


class ASTNodeTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~utl_lib.ast_node.ASTNode`."""

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.ast_node.ASTNode`."""
        item1 = ASTNode('symbol', {}, [])
        self.assertEqual(item1.symbol, 'symbol')
        self.assertDictEqual(item1.attributes, {})
        self.assertSequenceEqual(item1.children, [])
        self.assertIsNone(item1.parent)
        item2 = ASTNode('fred', {'a': 2, 'b': 'wilma'}, [item1])
        self.assertEqual(item2.symbol, 'fred')
        self.assertDictEqual(item2.attributes, {'a': 2, 'b': 'wilma'})
        self.assertSequenceEqual(item2.children, [item1])
        self.assertIs(item2.children[0].parent, item2)
        item3 = ASTNode('barney', {}, [item1, item2])
        self.assertSequenceEqual(item3.children, [item1, item2])

    def test_bad_create(self):
        """Unit tests for error handling in :py:meth:`utl_lib.ast_node.ASTNode`."""
        self.assertRaises(ASTNodeError, ASTNode, None, {}, [])
        self.assertRaises(ASTNodeError, ASTNode, '', {}, [])

    def test_add_child(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.add_child`."""
        item1 = ASTNode("fred", {'name': "Flintstone"}, [])
        item2 = ASTNode("wilma", {}, [ASTNode("pebbles", {}, [])])
        item3 = ASTNode("barney", {}, [])
        item4 = ASTNode("flintstones", {}, [item1])
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
        # Got to make sure that item2 stored as child of item1 still shows parent item1
        self.assertIs(item2.parent, item1)
        self.assertIs(item2, item1.children[0])
        self.assertIsNot(item2, item4.children[1])
        self.assertIs(item1.children[0].parent, item1)

    def test_add_child_bad(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.add_child` error cases."""
        item1 = ASTNode('fred', {}, [])
        self.assertRaises(ASTNodeError, item1.add_child, item1)
        self.assertRaises(ASTNodeError, item1.add_child, None)

    def test_add_first_child(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.add_first_child`."""
        item1 = ASTNode("wilma", {}, [ASTNode("first", {}, [])])
        item1.add_child(ASTNode("second", {}, []))
        self.assertSequenceEqual([kid.symbol for kid in item1.children],
                                 ["first", "second"])
        item1.add_first_child(ASTNode("really_first", {}, []))
        self.assertSequenceEqual([kid.symbol for kid in item1.children],
                                 ["really_first", "first", "second"])

    def test_add_children(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.add_children`."""
        item1 = ASTNode("wilma", {}, [])
        item1.add_children([ASTNode("first", {}, []), ASTNode("second", {}, [])])
        self.assertSequenceEqual([kid.symbol for kid in item1.children],
                                 ["first", "second"])
        item1.add_children([None, None])
        self.assertSequenceEqual([kid.symbol for kid in item1.children],
                                 ["first", "second"])

    def test_equal(self):
        """Unit test for equality testing of :py:class:`~utl_lib.ast_node.ASTNode` instances."""
        item1 = ASTNode('wilma', {}, [])
        self.assertNotEqual(item1, 'wilma')
        self.assertEqual(item1, ASTNode('wilma', {}, []))
        self.assertEqual(item1, item1)
        item2 = ASTNode('two',
                        {"pebbles": "daughter", "dino": "pet"},
                        [ASTNode('fred', {"barney": "friend"},
                                 [ASTNode("wilma", {}, [])])])
        item3 = ASTNode('two',
                        {"pebbles": "daughter", "dino": "pet"},
                        [ASTNode('fred', {"barney": "friend"},
                                 [ASTNode("wilma", {}, [])])])
        self.assertEqual(item2, item3)
        item3.attributes["john"] = "ringo"
        self.assertNotEqual(item2, item3)
        item2.attributes["john"] = "george"
        self.assertNotEqual(item2, item3)
        item3.attributes["john"] = "george"
        self.assertEqual(item2, item3)
        item2.add_child(ASTNode('extra', {}, []))
        self.assertNotEqual(item2, item3)
        item2 = ASTNode('two',
                        {},
                        [ASTNode('fred', {"barney": "friend"}, []),
                         ASTNode('wilma', {"betty": "friend"}, [])])
        item3 = item2.copy()
        self.assertEqual(item2, item3)
        temp = item2.children[0]
        item2.children[0] = item2.children[1]
        item2.children[1] = temp
        self.assertNotEqual(item2, item3)

    def test_str(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.__str__`."""
        item1 = ASTNode("first", {}, [])
        self.assertEqual(str(item1), "first: ")
        item1.attributes["second"] = "test"
        self.assertEqual(str(item1), "first:  {second: 'test'}")
        item1.attributes["third"] = "Π"  # Unicode, capital pi
        self.assertIn(str(item1), ["first:  {third: 'Π', second: 'test'}",
                                   "first:  {second: 'test', third: 'Π'}"])
        item2 = ASTNode("unary-op", {}, [])
        item2.attributes["operator"] = "!"
        self.assertEqual(str(item2), 'unary-op: !')
        item2 = ASTNode("literal", {"value": 12.0}, [])
        self.assertEqual(str(item2), 'literal: 12.0')
        lit2 = ASTNode("literal", {"value": 3.0}, [])
        item2 = ASTNode("literal",
                        {"value": ASTNode('array_literal', {},
                                          [ASTNode('array_elems', {}, [item2, lit2])])},
                        [])
        self.assertEqual(str(item2), 'literal (array): array_elems')
        item1 = ASTNode("operator", {"symbol": "-"}, [])
        item1.children.append(ASTNode("literal", {"value": 5}, []))
        item1.children.append(ASTNode("literla", {"value": 12.0}, []))
        self.assertEqual(str(item1), 'operator: -')
        item2 = ASTNode("document", {"text": '<h1>This is a test</h1>'}, [])
        self.assertEqual(str(item2), "document: '<h1>This is a test</h1>'")

    def test_repr(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.__repr__`."""
        item1 = ASTNode("first", {}, [])
        self.assertEqual(repr(item1), 'ASTNode("first", ..., [])')
        item1.attributes["second"] = "test"
        self.assertEqual(repr(item1), 'ASTNode("first", ..., [])')
        item1.add_child(ASTNode("third", {}, []))
        self.assertEqual(repr(item1), 'ASTNode("first", ..., [third])')
        item1.add_child(ASTNode("fourth", {}, []))
        self.assertEqual(repr(item1), 'ASTNode("first", ..., [third, fourth])')

    def test_format(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.format`."""
        anode = ASTNode('top', {}, [])
        test_out = anode.format()
        self.assertRegex(test_out, 'top:\s*')
        anode.add_child(ASTNode('first_kid', {}, []))
        test_out = anode.format()
        self.assertRegex(test_out, r'top:\s+first_kid')

    def test_json_format(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.json_format`."""
        anode = ASTNode('top', {}, [])
        test_out = anode.json_format()
        self.assertEqual(test_out, '{"name": "top"}')
        anode.attributes['first'] = 'last'
        test_json = json.loads(anode.json_format())
        self.assertDictEqual(test_json, {"name": "top", "attributes": {"first": "last"}})
        anode.add_child(ASTNode('second', {"fred": "husband"}, []))
        test_json = json.loads(anode.json_format())
        self.assertDictEqual(test_json, {"name": "top", "attributes": {"first": "last"},
                                         "children": [{"name": "second",
                                                       "attributes": {"fred": "husband"}}]})
        anode.add_child(ASTNode('third',
                                {"wife": ASTNode('wilma', {"husband": "fred"}, [])},
                                []))
        test_json = json.loads(anode.json_format())
        self.assertDictEqual(test_json,
                             {'name': 'top',
                              'attributes': {'first': 'last'},
                              'children': [
                                  {'name': 'second',
                                   'attributes': {'fred': 'husband'}},
                                  {'name': 'third',
                                   'attributes': {'wife': {'name': 'wilma',
                                                           'attributes': {'husband': 'fred'}}}}]})
        anode = ASTNode('top', {"fred": 'has "double" quotes'}, [])
        test_out = anode.json_format()
        self.assertEqual(test_out,
                         '{"name": "top",\n"attributes": {"fred": "has \\"double\\" quotes"}}')
        anode.attributes['int'] = 7
        test_out = anode.json_format()
        self.assertIn(test_out,
                      ('{"name": "top",\n"attributes": {"int": 7,\n"fred": "has \\"double\\" quotes"}}',
                       '{"name": "top",\n"attributes": {"fred": "has \\"double\\" quotes",\n"int": 7}}'))
        del anode.attributes['int']
        anode.attributes['bool'] = True
        test_out = anode.json_format()
        self.assertIn(test_out,
                      ('{"name": "top",\n"attributes": {"bool": true,\n"fred": "has \\"double\\" quotes"}}',
                       '{"name": "top",\n"attributes": {"fred": "has \\"double\\" quotes",\n"bool": true}}'))
        del anode.attributes['bool']
        anode.attributes['float'] = 23.0
        test_out = anode.json_format()
        self.assertIn(test_out,
                      ('{"name": "top",\n"attributes": {"float": 23.0,\n"fred": "has \\"double\\" quotes"}}',
                       '{"name": "top",\n"attributes": {"fred": "has \\"double\\" quotes",\n"float": 23.0}}'))
        anode = ASTNode('top', {"fred": "has 'single' quotes"}, [])
        test_out = anode.json_format()
        self.assertEqual(test_out,
                         '{"name": "top",\n"attributes": {"fred": "has \'single\' quotes"}}')
        document = ASTNode('document', {"text": '<div>some " embedded HTML</div>'}, [])
        self.assertEqual(document.json_format(),
                         '{"name": "document",\n"attributes": {"text": ' +
                         '"<div>some &quot; embedded HTML</div>"}}')


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
