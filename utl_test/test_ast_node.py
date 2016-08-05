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

from utl_lib.ast_node import ASTNode, FrozenASTNode, ASTNodeError
from utl_lib.immutable import FrozenDict


class ASTNodeTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~utl_lib.ast_node.ASTNode`."""

    test_nodes = ASTNode('fred', {"wilma": "betty"}, [
        ASTNode("barney", {"hobby": "rock-throwing"}, [
            ASTNode("bam-bam", {"hobby": "plotting revenge"}, [])
        ]),
        ASTNode("wilma", {"hobby": "s&m"}, [
            ASTNode("pebbles", {"hobby": "tormenting bam-bam"}, [])
        ])
    ])

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.ast_node.ASTNode`."""
        item1 = ASTNode('symbol', {}, [])
        self.assertEqual(item1.symbol, 'symbol')
        self.assertDictEqual(dict(item1.attributes), {})
        self.assertIsInstance(item1.attributes, FrozenDict)
        # since context is just a synonym for attributes in this impl.
        self.assertDictEqual(dict(item1.context), {})
        self.assertSequenceEqual(item1.children, [])
        self.assertIsNone(item1.parent)
        item2 = ASTNode('fred', {'a': 2, 'b': 'wilma'}, [item1])
        self.assertEqual(item2.symbol, 'fred')
        self.assertDictEqual(dict(item2.attributes), {'a': 2, 'b': 'wilma'})
        self.assertDictEqual(dict(item2.context), {'a': 2, 'b': 'wilma'})
        self.assertIsInstance(item2.attributes, FrozenDict)
        self.assertSequenceEqual(item2.children, [item1])
        self.assertIs(item2.children[0].parent, item2)
        item3 = ASTNode('barney', None, [item1, item2])
        self.assertSequenceEqual(item3.children, [item1, item2])
        self.assertIsInstance(item3.attributes, FrozenDict)
        self.assertDictEqual(dict(item3.attributes), {})
        item3.attributes = {"fred": "barney", "wilma": "betty", "pebbles": "bam-bam"}
        self.assertIsInstance(item3.attributes, FrozenDict)
        self.assertDictEqual(dict(item3.attributes),
                             {"fred": "barney", "wilma": "betty", "pebbles": "bam-bam"})

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
        self.assertIsInstance(item3.attributes, FrozenDict)
        # pylint: disable=E1101
        # why does pylint insist on regarding attributes as a dict?
        item3.attributes = item3.attributes.combine({"john": "ringo"})
        self.assertNotEqual(item2, item3)
        item2.attributes = item2.attributes.combine({"john": "george"})
        self.assertNotEqual(item2, item3)
        item3.attributes = item3.attributes.combine({"john": "george"})
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
        item1 = ASTNode("first", {"second": "test"}, [])
        self.assertEqual(str(item1), "first:  {second: 'test'}")
        # pylint: disable=E1101
        item1.attributes = item1.attributes.combine({"third": "Π"})  # Unicode, capital pi
        self.assertIn(str(item1), ["first:  {third: 'Π', second: 'test'}",
                                   "first:  {second: 'test', third: 'Π'}"])
        item2 = ASTNode("unary-op", {"operator": "!"}, [])
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
        item1 = ASTNode("first", {"second": "test"}, [])
        self.assertEqual(repr(item1), 'ASTNode("first", ..., [])')
        item1.add_child(ASTNode("third", {}, []))
        self.assertEqual(repr(item1), 'ASTNode("first", ..., [third])')
        item1.add_child(ASTNode("fourth", {}, []))
        self.assertEqual(repr(item1), 'ASTNode("first", ..., [third, fourth])')

    def test_format(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.format`."""
        anode = ASTNode('top', {}, [])
        test_out = anode.format()
        self.assertRegex(test_out, r'top:\s*')
        anode.add_child(ASTNode('first_kid', {}, []))
        test_out = anode.format()
        self.assertRegex(test_out, r'top:\s+first_kid')

    def test_json_format(self):
        """Unit tests for :py:meth:`~utl_lib.ast_node.ASTNode.json_format`."""
        anode = ASTNode('top', {}, [])
        test_out = anode.json_format()
        self.assertEqual(test_out, '{"name": "top"}')
        # pylint: disable=E1101
        anode.attributes = anode.attributes.combine({'first': 'last'})
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
        anode.attributes = anode.attributes.combine({'int': 7})
        test_out = anode.json_format()
        self.assertIn(test_out,
                      ('{"name": "top",\n"attributes": {"int": 7,\n"fred": "has \\"double\\" '
                       'quotes"}}',
                       '{"name": "top",\n"attributes": {"fred": "has \\"double\\" quotes",\n'
                       '"int": 7}}'))
        anode.attributes = anode.attributes.delkey('int')
        anode.attributes = anode.attributes.combine({'bool': True})
        test_out = anode.json_format()
        self.assertIn(test_out,
                      ('{"name": "top",\n"attributes": {"bool": true,\n"fred": "has \\"double\\"'
                       ' quotes"}}',
                       '{"name": "top",\n"attributes": {"fred": "has \\"double\\" quotes",\n"bool"'
                       ': true}}'))
        anode.attributes = anode.attributes.delkey('bool')
        anode.attributes = anode.attributes.combine({'float': 23.0})
        test_out = anode.json_format()
        self.assertIn(test_out,
                      ('{"name": "top",\n"attributes": {"float": 23.0,\n"fred": "has \\"double\\"'
                       ' quotes"}}',
                       '{"name": "top",\n"attributes": {"fred": "has \\"double\\" quotes",\n'
                       '"float": 23.0}}'))
        anode = ASTNode('top', {"fred": "has 'single' quotes"}, [])
        test_out = anode.json_format()
        self.assertEqual(test_out,
                         '{"name": "top",\n"attributes": {"fred": "has \'single\' quotes"}}')
        document = ASTNode('document', {"text": '<div>some " embedded HTML</div>'}, [])
        self.assertEqual(document.json_format(),
                         '{"name": "document",\n"attributes": {"text": ' +
                         '"<div>some &quot; embedded HTML</div>"}}')
        document = ASTNode('document', {"text": 2}, [])
        self.assertEqual(document.json_format(), '{"name": "document",\n"attributes": {"text": 2}}')

    def test_find_first(self):
        """Tests for :py:meth:`~utl_lib.ast_node.ASTNode.find_first`."""
        pebbles = self.test_nodes.find_first("pebbles")
        self.assertEqual(pebbles, ASTNode("pebbles", {"hobby": "tormenting bam-bam"}, []))

    def test_find_all(self):
        """Tests for :py:meth:`~utl_lib.ast_node.ASTNode.find_first`."""
        pebbles = self.test_nodes.find_all("pebbles")
        self.assertSequenceEqual(pebbles, [ASTNode("pebbles", {"hobby": "tormenting bam-bam"}, [])])
        barney = self.test_nodes.find_first("barney")
        barney.add_child(ASTNode("pebbles", {"hobby": "sweet innocent child"}, []))
        pebbles2 = self.test_nodes.find_all("pebbles")
        self.assertSequenceEqual(pebbles2,
                                 [ASTNode("pebbles", {"hobby": "sweet innocent child"}, []),
                                  ASTNode("pebbles", {"hobby": "tormenting bam-bam"}, [])])
        barney.children = [barney.children[0]]

    def test_walk(self):
        item1 = ASTNode('fred', {}, [])
        self.assertListEqual(list(item1.walk()), [item1])
        item2 = ASTNode('wilma', {}, [])
        item1.add_child(item2)
        self.assertListEqual(list(item1.walk()), [item1, item2])
        item3 = ASTNode('barney', {}, [])
        item1.add_child(item3)
        self.assertListEqual(list(item1.walk()), [item1, item2, item3])
        item4 = ASTNode('pebbles', {}, [])
        item5 = ASTNode('bam-bam', {}, [])
        item2.add_child(item4)
        item3.add_child(item5)
        self.assertListEqual(list(item1.walk()), [item1, item2, item4, item3, item5])


class FrozenASTNodeTestCase(unittest_plus.TestCasePlus):
    """Unit tests for :py:class:`utl_lib.ast_node.FrozenASTNode`, an
    immutable, hashable copy of an :py:class:`utl_lib.ast_node.ASTNode`.

    """

    def test_create(self):
        """Test :py:meth:`~utl_lib.ast_node.FrozenASTNode`."""
        source_node = ASTNode("fred", {"pebbles": "wilma", "bam-bam": "betty"},
                              [ASTNode("barney", {"friend": True}, [])])
        frozen_node = FrozenASTNode(source_node)
        self.assertEqual(frozen_node.symbol, source_node.symbol)
        self.assertEqual(frozen_node.attributes, source_node.attributes)

    def test_bad_create(self):
        """Test attempt to create a
        :py:class:`~utl_lib.ast_node.FrozenASTNode` with a source which is
        not an :py:class:`~utl_lib.ast_node.ASTNode`.

        """
        source_bad = {"fred": "barney"}
        self.assertRaises(ValueError, FrozenASTNode, source_bad)

    def test_equality(self):
        """Test that :py:class:`~utl_lib.ast_node.FrozenASTNode` behaves
        correctly with the `==` operator.

        """
        source_node = ASTNode("fred", {"pebbles": "wilma", "bam-bam": "betty"},
                              [ASTNode("barney", {"friend": True}, [])])
        frozen1 = FrozenASTNode(source_node)
        # and of course
        self.assertNotEqual(frozen1, source_node)
        frozen2 = FrozenASTNode(source_node)
        # although it actually wouldn't hurt if `frozen1 is frozen2 == True`,
        # since they're immutable
        self.assertIsNot(frozen1, frozen2)
        self.assertEqual(frozen1, frozen2)
        source_node.attributes = {"pebbles": "Marilyn Monroe",
                                  "bam-bam": "Lyanna Stark"}
        frozen3 = FrozenASTNode(source_node)
        self.assertEqual(frozen1, frozen2)
        self.assertNotEqual(frozen1, frozen3)

    def test_str(self):
        """Test :py:class:`~utl_lib.ast_node.FrozenASTNode` conversion to
        :py:class:`str`.

        """
        source_node = ASTNode("fred", {"pebbles": "wilma", "bam-bam": "betty"},
                              [ASTNode("barney", {"friend": True}, [])])
        frozen1 = FrozenASTNode(source_node)
        self.assertIn(str(frozen1), ["fred:  {bam-bam: 'betty', pebbles: 'wilma'}",
                                     "fred:  {pebbles: 'wilma', bam-bam: 'betty'}"])
        source_node = ASTNode("wilma", {}, [])
        frozen2 = FrozenASTNode(source_node)
        self.assertEqual(str(frozen2), "wilma: ")
        source_node = ASTNode("barney", {},
                              [ASTNode("bam-bam", {"sex": "male"},
                                       [ASTNode("John Snow", {}, []), ])])
        frozen3 = FrozenASTNode(source_node)
        self.assertEqual(str(frozen3), "barney: ")
        source_node = ASTNode("literal", {"value": "fred"}, [])
        frozen4 = FrozenASTNode(source_node)
        self.assertEqual(str(frozen4), "literal: 'fred'")
        source_node = ASTNode("id", {"symbol": "abcd", }, [])
        frozen5 = FrozenASTNode(source_node)
        self.assertEqual(str(frozen5), "id: abcd")
        source_node = ASTNode("document", {"text": "fred",}, [])
        frozen6 = FrozenASTNode(source_node)
        self.assertEqual(str(frozen6), "document: 'fred'")

    def test_repr(self):
        """"""
        source_node = ASTNode("fred", {"pebbles": "wilma", "bam-bam": "betty"},
                              [ASTNode("barney", {"friend": True}, [])])
        frozen1 = FrozenASTNode(source_node)
        self.assertEqual(repr(frozen1), 'FrozenASTNode("fred", ..., [barney])')

        source_node = ASTNode("wilma", {}, [])
        frozen2 = FrozenASTNode(source_node)
        self.assertEqual(repr(frozen2), 'FrozenASTNode("wilma", ..., [])')

        source_node = ASTNode("barney", {},
                              [ASTNode("bam-bam", {"sex": "male"},
                                       [ASTNode("John Snow", {}, []), ])])
        frozen3 = FrozenASTNode(source_node)
        self.assertEqual(repr(frozen3), 'FrozenASTNode("barney", ..., [bam-bam])')

        source_node = ASTNode("literal", {"value": "fred"}, [])
        frozen4 = FrozenASTNode(source_node)
        self.assertEqual(repr(frozen4), 'FrozenASTNode("literal", ..., [])')

        source_node = ASTNode("id", {"symbol": "abcd", }, [])
        frozen5 = FrozenASTNode(source_node)
        self.assertEqual(repr(frozen5), 'FrozenASTNode("id", ..., [])')

        source_node = ASTNode("document", {"text": "fred",}, [])
        frozen6 = FrozenASTNode(source_node)
        self.assertEqual(repr(frozen6), 'FrozenASTNode("document", ..., [])')

        source_node = ASTNode("barney", {},
                              [ASTNode("bam-bam", {"sex": "male"},
                                       [ASTNode("John Snow", {}, []), ]),
                               ASTNode("id", {"value": "JFK",}, [])])
        frozen3 = FrozenASTNode(source_node)
        self.assertEqual(repr(frozen3), 'FrozenASTNode("barney", ..., [bam-bam, id])')

    def test_walk(self):
        item1 = ASTNode('fred', {}, [])
        item2 = ASTNode('wilma', {}, [])
        item1.add_child(item2)
        self.assertListEqual(list(FrozenASTNode(item1).walk()),
                             [FrozenASTNode(item1), FrozenASTNode(item2)])
        item3 = ASTNode('barney', {}, [])
        item1.add_child(item3)
        self.assertListEqual(list(FrozenASTNode(item1).walk()),
                             [FrozenASTNode(item1), FrozenASTNode(item2),
                              FrozenASTNode(item3)])
        item4 = ASTNode('pebbles', {}, [])
        item5 = ASTNode('bam-bam', {}, [])
        item2.add_child(item4)
        item3.add_child(item5)
        self.assertListEqual(list(FrozenASTNode(item1).walk()),
                             [FrozenASTNode(item1), FrozenASTNode(item2), FrozenASTNode(item4),
                              FrozenASTNode(item3), FrozenASTNode(item5)])


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
