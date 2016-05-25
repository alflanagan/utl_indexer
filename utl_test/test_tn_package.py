#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`tn_package`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods

from testplus import unittest_plus
from utl_lib.tn_package import TNPackage


class TNPackageTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~tn_package.TNPackage`."""

    def test_create(self):
        """Unit test for :py:meth:`tn_package.TNPackage`. Verify public properties are set."""
        item1 = TNPackage({"app": "fred", "version": "1.2.3", "name": "some_package",},
                          True,
                          {"some_other_package": "3.4.5",},
                          "downloaded/zippped/some_package_1.2.3.zip",
                          "http://package.example.com")
        self.assertEqual(item1.name, "some_package")
        self.assertEqual(item1.app, "fred")
        self.assertEqual(item1.version, "1.2.3")
        self.assertEqual(item1.is_certified, True)
        self.assertEqual(item1.site, "http://package.example.com")
        self.assertEqual(item1.zipfile, "downloaded/zippped/some_package_1.2.3.zip")
        self.assertDictEqual(item1.deps, {"some_other_package": "3.4.5",})
        self.assertDictEqual(item1.properties, {"app": "fred", "version": "1.2.3",
                                                "name": "some_package",})


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
