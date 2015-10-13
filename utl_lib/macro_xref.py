#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from collections import defaultdict
import json

from utl_lib.ast_node import ASTNode


class UTLMacro(object):
    """A record of a specific UTL macro, including its definition and/or calls.

    :param object macro_defn: An instance of ASTNode whose type is 'macro_defn', OR a dictionary
    containing the fields [name, file, start, end, line, references].

    :param str code_text: The source code text of the macro definition.

    """

    def __init__(self, macro_defn, code_text):
        if isinstance(macro_defn, ASTNode):
            self.file = macro_defn.attributes["file"]
            # first child of macro_defn is the declaration
            self.name = macro_defn.children[0].attributes["name"]
            self.start = macro_defn.attributes["start"]
            self.end = macro_defn.attributes["end"]
            self.line = macro_defn.attributes["line"]
            self.text = code_text
            self.references = defaultdict(list)
            "A dictionary keyed by source file, of dictionaries keyed by line number"
        else:
            self.name = macro_defn["name"]
            self.file = macro_defn["file"]
            self.start = macro_defn["start"]
            self.end = macro_defn["end"]
            self.line = macro_defn["line"]
            self.text = code_text
            self.references = defaultdict(list)
            for fname in macro_defn["references"]:
                for item in macro_defn["references"][fname]:
                    self.add_call(item)

    def __eq__(self, other):
        """Define functional equality for :py:class:`~utl_lib.macro_xref.UTLMacro` instances."""
        if self is other:
            return True  # optimize a == a
        if not isinstance(other, self.__class__):
            return False  # can''t be equal to an object of different type, even child type
        if self.name != other.name or self.file != other.file or self.line != other.line or\
           self.end != other.end or self.start != other.start or self.text != other.text or\
           self.references != other.references:
            return False
        return True

    def add_call(self, info):
        """Record a call to this macro.

        :param dict info: Mapping from keys to some info about the call.

        """
        self.references[info["file"]].append(info)

    def __str__(self):
        return "{}() ({}:{:,})".format(self.name, self.file, self.line)

    def json(self):
        """Returns a :py:class:`str` containing a JSON structure representing this object."""
        return json.dumps({"name": self.name, "file": self.file, "start": self.start,
                           "end": self.end, "line": self.line, "text": self.text,
                           "references": self.references, })

    @classmethod
    def from_json(cls, json_str):
        """Creates a returns a :py:class:`utl_lib.macro_xref.UTLMacro` instance from a JSON
        string which could be the result of an earlier
        :py:meth:`~utl_lib.macro_xref.UTLMacro.json` call.

        """
        data = json.loads(json_str)
        return UTLMacro(data, data["text"])


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
            for macro in self.macros:
                if ref["macro"] == macro.name:
                    macro.add_call(ref)

    @staticmethod
    def _find_macros(top_node, code_text):
        """Search the AST tree rooted at `top_node` and return a collection of
        :py:class:`~utl_lib.macro_xrf.utl_macro` instances, one for each macro-defn node in the
        tree.

        :param ASTNode top_node: The root of some AST tree representing parsed UTL code

        :param str code_text: The actual text of the code parsed into `top_node`.

        """
        macros = []
        if top_node.symbol == 'macro_defn':
            macro_text = code_text[top_node.attributes["start"]:top_node.attributes["end"]]
            new_macro = UTLMacro(top_node, macro_text)
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
            assert isinstance(attrs["start"], int)
            assert isinstance(attrs["end"], int)
            new_ref = {"file": attrs["file"],
                       "line": attrs["line"],
                       "call_text": code_text[attrs["start"]: attrs["end"]],
                       "macro": attrs["macro_expr"],
                       "start": attrs["start"]}
            refs.append(new_ref)
        for kid in top_node.children:
            refs += UTLMacroXref._find_refs(kid, code_text)
        return refs

    def json(self):
        """Returns a :py:class:`str` containing the list of macros in a JSON format."""
        json_str = '['
        for macro in self.macros:
            json_str += macro.json() + ',\n'
        # remove final , becuase JSON is picky about that
        if self.macros:
            json_str = json_str[:-2]
        json_str += ']'
        return json_str

    def refs_json(self):
        """Returns a :py:class:`str` containing JSON of the list of macro references found."""
        return json.dumps(self.references)
