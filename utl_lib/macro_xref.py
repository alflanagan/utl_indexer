#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from collections import defaultdict


class UTLMacro(object):
    """A record of a specific UTL macro, including its definition and/or calls."""

    def __init__(self, macro_defn, code_text):
        self.name = macro_defn.attributes["name"]
        self.file = macro_defn.attributes["file"]
        # first child of macro_defn is the initial declaration
        self.start = macro_defn.children[0].attributes["macro_start"]
        self.end = macro_defn.attributes["end"]
        self.line = macro_defn.children[0].attributes["line"]
        self.text = code_text[self.start:self.end]
        self.references = {}
        "A dictionary keyed by source file, of dictionaries keyed by line number"

    def add_call(self, info):
        """Record a call to this macro.

        :param dict info: Mapping from keys to some info about the call.

        """
        if info["file"] not in self.references:
            self.references[info["file"]] = defaultdict(list)
        self.references[info["file"]].append(info)

    def __str__(self):
        return "{}() ({}:{:,})".format(self.name, self.file, self.line)


class UTLMacroXref(object):
    """A cross-reference of macro calls and macro definitions from UTL source.

    :param ASTNode utldoc_node: A node from an AST tree.

    """

    def __init__(self, utldoc_node, program_text):
        # make a list of top nodes, since we may have multiple
        self.topnodes = [utldoc_node]
        self.texts = {utldoc_node.attributes["file"]: program_text}
        self.macros = self._find_macros(utldoc_node, program_text)
        self.references = self._find_refs(utldoc_node, program_text)
        for ref in self.references:
            if ref["macro"] in self.macros:
                self.macros[ref["macro"]].add_call(ref)

    @staticmethod
    def _find_macros(top_node, code_text):
        macros = []
        if top_node.symbol == 'macro-defn':
            new_macro = UTLMacro(top_node, code_text)
            macros.append(new_macro)
        for kid in top_node.children:
            macros += UTLMacroXref._find_macros(kid, code_text)
        return macros

    @staticmethod
    def _find_refs(top_node, code_text):
        """Find all macro calls in the tree rooted at `top_node`, return as list."""
        refs = []
        if top_node.symbol == 'macro_call':
            attrs = top_node.attributes
            assert isinstance(attrs["call_start"], int)
            assert isinstance(attrs["end"], int)
            new_ref = {"file": attrs["file"],
                       "line": attrs["line"],
                       "call_text": code_text[attrs["call_start"]: attrs["end"]+1],
                       "macro": attrs["macro_expr"],}
            refs.append(new_ref)
        for kid in top_node.children:
            refs += UTLMacroXref._find_refs(kid, code_text)
        return refs
