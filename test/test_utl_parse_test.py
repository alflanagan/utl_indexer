#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`utl_indexer.test.utl_parse_test`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods
import json

import utl_parse_test
from utl_lib.ast_node import ASTNode


class TestCaseUTLTestCase(utl_parse_test.TestCaseUTL):
    """Unit tests for class :py:class:`~utl_indexer.test.utl_parse_test.TestCaseUTL`."""

    def test_assertMatchesJSON(self):
        """Unit test for :py:meth:`utl_indexer.test.utl_parse_test.TestCaseUTL.assertMatchesJSON`.

        """
        self.assertEqual(5, 5)
        expected1 = {"name": "id", "attributes": {"symbol": "fred",},}
        node1 = ASTNode("id", True, {"symbol": "fred",}, [])
        self.assertMatchesJSON(node1, expected1)


if __name__ == '__main__':
    utl_parse_test.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
