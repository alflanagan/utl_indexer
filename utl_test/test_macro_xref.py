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


class UTLMacroTestCase(utl_parse_test.TestCaseUTL):
    """Unit tests for class :py:class:`~utl_lib.macro_xref.UTLMacro`."""

    defn_attributes = {"name": "fred",
                       "file": "fred.utl",
                       "end": 0, }
    decl_attributes = {"start": 0,
                       "line": 1, }

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.macro_xref.UTLMacro`."""
        macro_code = "macro fred;\nend;"
        defn_attributes = self.defn_attributes.copy()
        defn_attributes["end"] = len(macro_code)
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attributes,
                                 [ASTNode("macro_decl", self.decl_attributes, [])]),
                         macro_code)
        self.assertEqual(item1.end, len(macro_code))
        self.assertEqual(item1.file, "fred.utl")
        self.assertEqual(item1.line, 1)
        self.assertEqual(item1.name, "fred")
        self.assertEqual(item1.references, {})
        self.assertEqual(item1.start, 0)
        self.assertEqual(item1.text, macro_code)

        macro_defn = {"name": "fred",
                      "file": "barney.utl",
                      "start": 7,
                      "end": 53,
                      "line": 1,
                      "references": {
                          "wilma.utl": [{
                              "file": "wilma.utl",
                              "line": 53,
                              "call_text": "fred()",
                              "macro": "fred"}]}}
        item2 = UTLMacro(macro_defn, macro_code)
        self.assertEqual(item2.end, 53)
        self.assertEqual(item2.file, "barney.utl")
        self.assertEqual(item2.line, 1)
        self.assertEqual(item2.name, "fred")
        self.assertDictEqual(item2.references,
                             {"wilma.utl": [{
                                 "file": "wilma.utl",
                                 "line": 53,
                                 "call_text": "fred()",
                                 "macro": "fred"}]})
        self.assertEqual(item2.start, 7)
        self.assertEqual(item2.text, macro_code)

    def test_add_call(self):
        """Unit test for :py:meth:`utl_lib.macro_xref.UTLMacro.add_call`."""
        macro_code = "macro fred;\nend;"
        defn_attributes = self.defn_attributes.copy()
        defn_attributes["end"] = len(macro_code)
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attributes,
                                 [ASTNode("macro_decl", self.decl_attributes, [])]),
                         macro_code)
        call_info1 = {"file": "big_file.utl", "line": 512, "call_text": "fred();", }
        item1.add_call(call_info1)
        self.assertIn("big_file.utl", item1.references)
        self.assertEqual(len(item1.references[call_info1["file"]]), 1)
        self.assertDictEqual(item1.references[call_info1["file"]][0], call_info1)

    def test_str(self):
        """Unit test for str(:py:class:`~utl_lib.macro_xref.UTLMacro`)."""
        macro_code = "macro fred;\nend;"
        defn_attributes = self.defn_attributes.copy()
        defn_attributes["end"] = len(macro_code)
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attributes,
                                 [ASTNode("macro_decl", self.decl_attributes, [])]),
                         macro_code)
        self.assertEqual(str(item1), 'fred() (fred.utl:1)')

    def test_json(self):
        """Unit test for :py:meth:`~utl_lib.macro_xref.UTLMacro.json`."""
        macro_code = "macro fred;\nend;"
        defn_attributes = self.defn_attributes.copy()
        defn_attributes["end"] = len(macro_code)
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attributes,
                                 [ASTNode("macro_decl", self.decl_attributes, [])]),
                         macro_code)
        self.assertDictEqual(json.loads(item1.json()),
                             {"file": "fred.utl",
                              "start": 0,
                              "name": "fred",
                              "references": {},
                              "end": 16,
                              "line": 1,
                              "text": "macro fred;\nend;"})
        self.assertEqual(item1, UTLMacro.from_json(item1.json()))

    def test_equal(self):
        """Test implementation of == for :py:class:`~utl_lib.macro_xrf.UTLMacro`."""
        macro_code = "macro fred;\nend;"
        defn_attributes = self.defn_attributes.copy()
        defn_attributes["end"] = len(macro_code)
        item1 = UTLMacro(ASTNode("macro_defn",
                                 defn_attributes,
                                 [ASTNode("macro_decl", self.decl_attributes, [])]),
                         macro_code)
        self.assertEqual(item1, item1)
        item2 = UTLMacro.from_json(item1.json())
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

    test_doc_1 = ASTNode(
        'statement_list',
        {'line': 7, 'end': 72, 'file': 'macros.utl', 'start': 74},
        [ASTNode('macro_defn',
                 {'line': 7, 'start': 3, 'file': 'macros.utl', 'end': 72, 'name': 'fred'},
                 [ASTNode('macro_decl',
                          {'line': 1, 'start': 3, 'file': 'macros.utl', 'end': 13, 'name': 'fred'},
                          [ASTNode('statement_list',
                                   {'line': 7, 'end': 72, 'file': 'macros.utl', 'start': 69},
                                   [ASTNode('expr',
                                            {'line': 2, 'end': 26, 'file': 'macros.utl', 'start': 25, 'operator': '='},
                                            [ASTNode('id',
                                                     {'symbol': 'a'},
                                                     []),
                                             ASTNode('expr',
                                                     {'line': 2, 'end': 26, 'file': 'macros.utl', 'start': 25,
                                                      'operator': '+'},
                                                     [ASTNode('id',
                                                              {'symbol': 'b'},
                                                              []),
                                                      ASTNode('literal',
                                                              {'value': 3.0},
                                                              [])])]),
                                    ASTNode('echo',
                                            {'line': 3, 'end': 34, 'file': 'macros.utl', 'start': 30},
                                            []),
                                    ASTNode('echo',
                                            {'line': 4, 'end': 44, 'file': 'macros.utl', 'start': 43},
                                            [ASTNode('id', {'symobl': 'a'}, [])]),
                                    ASTNode('macro_call',
                                            {'line': 5, 'macro_expr': 'fred', 'file': 'macros.utl',
                                             'end': 54, 'start': 48},
                                            [ASTNode('id', {'symbol': 'fred'}, []),
                                             ASTNode('arg_list',
                                                     {'line': 5, 'end': 54, 'file': 'macros.utl', 'start': 53},
                                                     [ASTNode('arg',
                                                              {'line': 5, 'end': 54, 'file': '', 'start': 53},
                                                              [ASTNode('literal', {'value': 7}, [])])])]),
                                    ASTNode('macro_call',
                                            {'end': 66, 'file': 'macros.utl', 'macro_expr': 'wilma',
                                             'line': 6, 'start': 59},
                                            [ASTNode('id', {'symbol': 'wilma'}, []),
                                             ASTNode('arg_list',
                                                     {'start': 65, 'end': 66, 'line': 6, 'file': 'macros.utl'},
                                                     [ASTNode('arg',
                                                              {'start': 65, 'end': 66, 'line': 6, 'file': 'macros.utl'},
                                                              [ASTNode('literal', {'value': 8.0}, [])])])])])])])])

    doc_text_1 = """[% macro fred;
  a = b + 3;
  echo;
  echo a;
  fred(7);
  wilma(8);
end; %]"""

    def test_create(self):
        """Unit tests for :py:meth:`~utl_lib.macro_xref.UTLMacroXref`."""
        from utl_lib.utl_yacc import UTLParser
        from utl_lib.handler_ast import UTLParseHandlerAST
        p = UTLParser([UTLParseHandlerAST()])
        p.parse(self.doc_text_1)
        item1 = UTLMacroXref(self.test_doc_1, self.doc_text_1)
        self.assertIs(item1.topnodes[0], self.test_doc_1)
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
        item1 = UTLMacroXref(self.test_doc_1, self.doc_text_1)
        json_str = item1.json()
        # order not gauranteed in JSON string, but key/value pairs are
        self.assertIn('"end": 72', json_str)
        self.assertIn('"start": 3', json_str)
        # of course, embedded newlines are escaped for JSON string
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
        item1 = UTLMacroXref(self.test_doc_1, self.doc_text_1)
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
