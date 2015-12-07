#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lib.macro_xref`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods
import json
import re
from collections import defaultdict

from utl_test import utl_parse_test
from utl_lib.macro_xref import UTLMacro, UTLMacroXref
from utl_lib.ast_node import ASTNode
from utl_lib.utl_yacc import UTLParser
from utl_lib.handler_ast import UTLParseHandlerAST


class UTLMacroTestCase(utl_parse_test.TestCaseUTL):
    """Unit tests for class :py:class:`~utl_lib.macro_xref.UTLMacro`."""

    test_macro_text = [
        """[% macro fred;
echo a;
end; %]""",
        """[% macro fred;
wilma(7);
end; %] """]

    @classmethod
    def setUpClass(cls):
        """Uses :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST` to get the attributes of the
        :py:class:`~utl_lib.ast_node.ASTNode` instances we use for tests.

        This is done to ensure that our test data is in synch with the parser and handlers.

        """
        handler = UTLParseHandlerAST()
        parser = UTLParser([handler])
        fred = parser.parse(cls.test_macro_text[0], filename="fred.utl")
        fred = fred.children[0]  # from statment_list to macro_defn
        assert fred.symbol == 'macro_defn'
        cls.defn_attributes = [fred.attributes]
        cls.decl_attributes = [fred.children[0].attributes]
        parser.restart()  # start over
        # why is Wilma in Barney's file? Suspicious!
        wilma = parser.parse(cls.test_macro_text[1], filename="barney.utl").children[0]
        cls.defn_attributes.append(wilma.attributes)
        cls.decl_attributes.append(wilma.children[0].attributes)

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.macro_xref.UTLMacro`."""
        first_macro, second_macro = self.test_macro_text
        defn_attrs = self.defn_attributes[0]
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attrs,
                                 [ASTNode("macro_decl", self.decl_attributes[0], [])]),
                         first_macro[defn_attrs["start"]:defn_attrs["end"]])
        self.assertEqual(item1.end, 26)
        self.assertEqual(item1.file, defn_attrs["file"])
        self.assertEqual(item1.line, defn_attrs["line"])
        self.assertEqual(item1.references, {})
        self.assertEqual(item1.start, defn_attrs["start"])
        self.assertEqual(item1.text, first_macro[item1.start:item1.end])

        macro_defn = {"name": "fred",
                      "file": "barney.utl",
                      "start": 3,
                      "end": 28,
                      "line": 1,
                      "references": {
                          "wilma.utl": [{
                              "file": "wilma.utl",
                              "line": 53,
                              "call_text": "fred()",
                              "macro": "fred"}]}}
        item2 = UTLMacro(macro_defn, second_macro[3:-5])
        self.assertEqual(item2.end, self.defn_attributes[1]["end"])
        self.assertEqual(item2.file, "barney.utl")
        self.assertEqual(item2.line, 1)
        self.assertEqual(item2.name, "fred")
        self.assertDictEqual(item2.references,
                             {"wilma.utl": [{
                                 "file": "wilma.utl",
                                 "line": 53,
                                 "call_text": "fred()",
                                 "macro": "fred"}]})
        self.assertEqual(item2.start, 3)
        self.assertEqual(item2.text, self.test_macro_text[1][item2.start:item2.end])

    def test_add_call(self):
        """Unit test for :py:meth:`utl_lib.macro_xref.UTLMacro.add_call`."""
        macro_code = "macro fred;\nend;"
        defn_attrs = dict(self.defn_attributes[0])
        defn_attrs["end"] = len(macro_code)
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attrs,
                                 [ASTNode("macro_decl", self.decl_attributes[0], [])]),
                         macro_code)
        call_info1 = {"file": "big_file.utl", "line": 512, "call_text": "fred();", }
        item1.add_call(call_info1)
        self.assertIn("big_file.utl", item1.references)
        self.assertEqual(len(item1.references[call_info1["file"]]), 1)
        self.assertDictEqual(item1.references[call_info1["file"]][0], call_info1)

    def test_str(self):
        """Unit test for str(:py:class:`~utl_lib.macro_xref.UTLMacro`)."""
        macro_code = "macro fred;\nend;"
        defn_attributes = dict(self.defn_attributes[0])
        defn_attributes["end"] = len(macro_code)
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attributes,
                                 [ASTNode("macro_decl", self.decl_attributes[0], [])]),
                         macro_code)
        self.assertEqual(str(item1), 'fred() (fred.utl:1)')

    def test_json(self):
        """Unit test for :py:meth:`~utl_lib.macro_xref.UTLMacro.json`."""
        macro_code = "macro fred;\nend;"
        defn_attrs = self.defn_attributes[0]
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attrs,
                                 [ASTNode("macro_decl", self.decl_attributes[0], [])]),
                         macro_code)
        self.assertDictEqual(json.loads(item1.json()),
                             {"file": "fred.utl",
                              "start": 3,
                              "name": "fred",
                              "references": {},
                              "end": 26,
                              "line": 1,
                              "text": "macro fred;\nend;"})
        self.assertEqual(item1, UTLMacro.from_json(item1.json()))

    def test_equal(self):
        """Test implementation of == for :py:class:`~utl_lib.macro_xrf.UTLMacro`."""
        macro_code = "macro fred;\nend;"
        defn_attrs = self.defn_attributes[0]
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attrs,
                                 [ASTNode("macro_decl", self.decl_attributes[0], [])]),
                         macro_code)
        self.assertEqual(item1, item1)
        item2 = UTLMacro.from_json(item1.json())
        self.assertIsNot(item1, item2)
        self.assertEqual(item1, item2)
        self.assertNotEqual(item1, "fred")
        for attr in dir(item2):
            orig_value = getattr(item2, attr)
            if not attr.startswith('_') and not callable(orig_value):
                setattr(item2, attr, "wilma")
                self.assertNotEqual(item1, item2)
                setattr(item2, attr, orig_value)
        # did we mess up item2 above?
        self.assertEqual(item1, item2)
        item1.add_call({"file": "barney.utl",
                        "line": 7,
                        "call_text": "fred()",
                        "macro": "fred", })
        self.assertNotEqual(item1, item2)
        item2.add_call({"file": "barney.utl",
                        "line": 7,
                        "call_text": "fred()",
                        "macro": "fred", })
        self.assertEqual(item1, item2)
        item2.references["barney.utl"][0]["line"] = 8
        self.assertNotEqual(item1, item2)


class UTLMacroXrefTestCase(utl_parse_test.TestCaseUTL):
    """Unit tests for :py:class:`utl_lib.macro_xref.UTLMacroXref`."""

    doc_text_1 = """[% macro fred;
  a = b + 3;
  echo;
  echo a;
  fred(7);
  wilma(8);
end; %]"""

    # pylint:disable=line-too-long
    test_json_1 = {"name": "statement_list",
                   "attributes": {"end": 77, "start": 3, "file": "macros.utl", "line": 1},
                   "children": [
                       {"name": "macro_defn",
                        "attributes": {"end": 72, "start": 3, "file": "macros.utl", "line": 1},
                        "children": [
                            {"name": "macro_decl",
                             "attributes": {"end": 13, "start": 3, "file": "macros.utl", "line": 1, "name": "fred"}},
                            {"name": "statement_list",
                             "attributes": {"end": 67, "start": 17, "file": "macros.utl", "line": 2},
                             "children": [
                                 {"name": "expr",
                                  "attributes": {"end": 26, "start": 17, "file": "macros.utl", "operator": "=", "line": 2},
                                  "children": [
                                      {"name": "id",
                                       "attributes": {"end": 18, "start": 17, "file": "macros.utl", "line": 2, "symbol": "a"}},
                                      {"name": "expr",
                                       "attributes": {"end": 26, "start": 21, "file": "macros.utl", "operator": "+", "line": 2},
                                       "children": [
                                           {"name": "id", "attributes": {"end": 22, "start": 21, "file": "macros.utl", "line": 2, "symbol": "b"}},
                                           {"name": "literal",
                                            "attributes": {"start": 25, "end": 26, "file": "macros.utl", "line": 2, "type": "number", "value": 3.0}}]}]},
                                 {"name": "echo",
                                  "attributes": {"end": 34, "start": 30, "file": "macros.utl", "line": 3}},
                                 {"name": "echo",
                                  "attributes": {"end": 44, "start": 38, "file": "macros.utl", "line": 4},
                                  "children": [
                                      {"name": "id",
                                       "attributes": {"end": 44, "start": 43, "file": "macros.utl", "line": 4, "symbol": "a"}}]},
                                 {"name": "macro_call",
                                  "attributes": {"end": 55, "start": 48, "file": "macros.utl", "line": 5, "macro_expr": "fred"},
                                  "children": [
                                      {"name": "id",
                                       "attributes": {"end": 52, "start": 48, "file": "macros.utl", "line": 5, "symbol": "fred"}},
                                      {"name": "arg_list",
                                       "attributes": {"end": 54, "start": 53, "file": "macros.utl", "line": 5},
                                       "children": [
                                           {"name": "arg",
                                            "attributes": {"end": 54, "start": 53, "file": "macros.utl", "line": 5},
                                            "children": [
                                                {"name": "literal",
                                                 "attributes": {"start": 53, "end": 54, "file": "macros.utl", "line": 5, "type": "number", "value": 7.0}}]}]}]},
                                 {"name": "macro_call",
                                  "attributes": {"end": 67, "start": 59, "file": "macros.utl", "line": 6, "macro_expr": "wilma"},
                                  "children": [
                                      {"name": "id",
                                       "attributes": {"end": 64, "start": 59, "file": "macros.utl", "line": 6, "symbol": "wilma"}},
                                      {"name": "arg_list",
                                       "attributes": {"end": 66, "start": 65, "file": "macros.utl", "line": 6},
                                       "children": [
                                           {"name": "arg",
                                            "attributes": {"end": 66, "start": 65, "file": "macros.utl", "line": 6},
                                            "children": [
                                                {"name": "literal",
                                                 "attributes": {"start": 65, "end": 66, "file": "macros.utl", "line": 6, "type": "number", "value": 8.0}}]}]}]}]}]}]}

    def test_create(self):
        """Unit tests for :py:meth:`~utl_lib.macro_xref.UTLMacroXref`."""
        p = UTLParser([UTLParseHandlerAST()])
        parsed = p.parse(self.doc_text_1, filename='macros.utl')
        # with open('temp.json', 'w') as jsout:
        #     jsout.write(parsed.json_format())
        # self.assertEqual(parsed, self.test_doc_1)
        self.assertMatchesJSON(parsed, self.test_json_1)
        item1 = UTLMacroXref(parsed, self.doc_text_1)
        self.assertIs(item1.topnodes[0], parsed)
        self.assertEqual(item1.texts["macros.utl"], self.doc_text_1)
        self.assertEqual(item1.references,
                         [{'call_text': 'fred(7)', 'file': 'macros.utl',
                           'line': 5, 'macro': 'fred', 'start': 48},
                          {'call_text': 'wilma(8)', 'file': 'macros.utl',
                           'line': 6, 'macro': 'wilma', 'start': 59}])
        self.assertEqual(len(item1.macros), 1)
        themacro = item1.macros[0]
        isinstance(themacro, UTLMacro)
        self.assertEqual(themacro.file, "macros.utl")
        self.assertEqual(themacro.name, "fred")
        self.assertEqual(themacro.end, len(self.doc_text_1) - 4)  # end excludes "; %]"
        self.assertEqual(themacro.line, 1)
        self.assertEqual(themacro.start, 3)
        self.assertEqual(themacro.text, self.doc_text_1[3:-4])
        expected_refs = defaultdict(list)
        expected_refs['macros.utl'] = [{'call_text': 'fred(7)',
                                        'file': 'macros.utl',
                                        'line': 5,
                                        'start': 48,
                                        'macro': 'fred'}]
        self.assertEqual(themacro.references, expected_refs)

    def test_json(self):
        """unit tests for :py:meth:`~utl_lib.macro_xref.UTLMacroXref.json`."""
        p = UTLParser([UTLParseHandlerAST()])
        parsed = p.parse(self.doc_text_1, filename='macros.utl')
        item1 = UTLMacroXref(parsed, self.doc_text_1)
        json_str = item1.json()
        # order not gauranteed in JSON string, but key/value pairs are
        self.assertIn('"end": 72', json_str)
        self.assertIn('"start": 3', json_str)
        # of course, embedded newlines are escaped for JSON string
        expected = ('"text": "macro fred;\\n  a = b + 3;\\n  echo;\\n  echo '
                    'a;\\n  fred(7);\\n  wilma(8);\\nend')

        self.assertIn('"text": "{}"'.format(self.doc_text_1[3:-4]).replace('\n', '\\n'),
                      json_str)
        self.assertIn('"references": {"macros.utl": ', json_str)
        refs_match = re.search(r'macros.utl": \[\{(.+?)\}\]', json_str)
        refs_str = refs_match.group(1)
        self.assertIn('"file": "macros.utl"', refs_str)
        self.assertIn('"call_text": "fred(7)"', refs_str)
        self.assertIn('"macro": "fred"', refs_str)
        self.assertIn('"line": 5', refs_str)
        self.assertIn('"file": "macros.utl"', json_str)
        self.assertIn('"name": "fred"', json_str)
        self.assertIn('"line": 1', json_str)
        self.assertTrue(json_str.startswith('[{'))
        self.assertTrue(json_str.endswith('}]'))
        # handle case where there are no macros found
        item1.macros = []
        json_str = item1.json()
        self.assertEqual(json_str, '[]')

    def test_refs_json(self):
        """unit tests for :py:meth:`~utl_lib.macro_xref.UTLMacroXref.refs_json`."""
        p = UTLParser([UTLParseHandlerAST()])
        parsed = p.parse(self.doc_text_1, filename='macros.utl')
        item1 = UTLMacroXref(parsed, self.doc_text_1)
        json_str = item1.refs_json()
        self.assertIn('"line": 5', json_str)
        self.assertIn('"call_text": "fred(7)"', json_str)
        self.assertIn('"file": "macros.utl"', json_str)
        self.assertIn('"macro": "fred"', json_str)


if __name__ == '__main__':
    utl_parse_test.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
