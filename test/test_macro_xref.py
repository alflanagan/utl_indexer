#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_lib.macro_xref`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods
import json

import utl_parse_test
from utl_lib.macro_xref import UTLMacro
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


if __name__ == '__main__':
    utl_parse_test.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
