#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`handler_ast`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import json
from testplus import unittest_plus

from utl_lib.handler_ast import UTLParseHandlerAST
from utl_lib.ast_node import ASTNode
from utl_lib.utl_yacc import UTLParser


class UTLParseHandlerASTTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST`."""

    def test_create(self):
        """Unit test for :py:meth:`utl_lib.handler_ast.UTLParseHandlerAST`."""
        handler = UTLParseHandlerAST()
        utldoc = handler.utldoc(ASTNode('statement_list', False, {}, []))
        self.assertEqual(utldoc, ASTNode('statement_list', False, {}, []))

    def test_basic_assign(self):
        """Unit test of :py:class:`~utl_lib.handler_ast.UTLParseHandlerAST` with simple
        assignment statements.

        """
        with open("test_data/basic_assign_ast.json", "r") as expin:
            expected = json.load(expin)
        handler = UTLParseHandlerAST()
        parser = UTLParser(handler)
        with open("test_data/basic_assign.utl", "r") as datain:
            test_data = datain.read()
        results = parser.parse(test_data)
        results = json.loads(results.json_format())
        with open("test_data/basic_assign_ast_result.json", "w") as expout:
            json.dump(results, expout)
        self.maxDiff = None
        self.assertEqual(expected['name'], results['name'])
        if "attributes" in expected:
            self.assertDictEqual(expected["attributes"], results["attributes"])
        self.assertEqual(len(expected['children']), len(results['children']))
        for index in range(len(expected['children'])):
            expected_dict = expected['children'][index]
            results_dict = results['children'][index]
            self.assertSetEqual(set(expected_dict.keys()), set(results_dict.keys()))
            for key in expected_dict:
                if isinstance(expected_dict[key], list):
                    for index, item in enumerate(expected_dict[key]):
                        self.assertEqual(item, results_dict[key][index])
                else:
                    self.assertEqual(expected_dict[key], results_dict[key])


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
