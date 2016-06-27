#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Unit tests for :py:mod:`tn_package`.

| Copyright: 2015 BH Media Group, Inc.
| Organization: BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
# pylint: disable=too-few-public-methods
from pathlib import Path
from warnings import simplefilter

from testplus import unittest_plus
from utl_lib.tn_package import TNPackage, PackageError


class TNPackageTestCase(unittest_plus.TestCasePlus):
    """Unit tests for class :py:class:`~tn_package.TNPackage`."""

    TEST_DATA = Path(__file__).parent / 'test_data/pkgs'

    def test_create(self):
        """Unit test for :py:meth:`tn_package.TNPackage`. Verify public properties are set."""
        item1 = TNPackage({"app": "fred", "version": "1.2.3", "name": "some_package", },
                          True,
                          {"some_other_package": "3.4.5", },
                          "downloaded/zippped/some_package_1.2.3.zip",
                          "http://package.example.com")
        self.assertEqual(item1.name, "some_package")
        self.assertEqual(item1.app, "fred")
        self.assertEqual(item1.version, "1.2.3")
        self.assertEqual(item1.is_certified, True)
        self.assertEqual(item1.site, "http://package.example.com")
        self.assertEqual(item1.zipfile, "downloaded/zippped/some_package_1.2.3.zip")
        self.assertDictEqual(item1.deps, {"some_other_package": "3.4.5", })
        self.assertDictEqual(item1.properties, {"app": "fred", "version": "1.2.3",
                                                "name": "some_package", })

    def test__str__(self):
        """Unit tests for :py:meth:`utl_lib.tn_package.TNPackage.__str__`."""
        item1 = TNPackage({"app": "fred", "version": "1.2.3", "name": "some_package", },
                          True,
                          {"some_other_package": "3.4.5", },
                          "downloaded/zippped/some_package_1.2.3.zip",
                          None)
        self.assertEqual(str(item1), "fred/some_package/1.2.3")
        item2 = TNPackage({"app": "fred", "version": "1.2.3", "name": "some_package", },
                          False, {}, "downloaded/zippped/some_package_1.2.3.zip",
                          "http://package.example.com")
        self.assertEqual(str(item2), "http://package.example.com: fred/some_package/1.2.3")

    def test_load_from_certified(self):
        """Unit test for :py:meth:`utl_lib.tn_package.TNPackage.load_from`
        with sample data from a certified package.

        """
        pkg_dir = self.TEST_DATA / 'editorial-core-mobile-1.54'
        self.assertTrue(pkg_dir.exists())
        the_pkg = TNPackage.load_from(pkg_dir,
                                      'skin_editorial_core-mobile-1.54.0.0.zip')
        self.assertIsInstance(the_pkg, TNPackage)
        isinstance(the_pkg, TNPackage)
        self.assertEqual(the_pkg.name, 'editorial-core-mobile')
        self.assertEqual(the_pkg.version, '1.54.0.0')
        simplefilter("ignore")  # skip UserWarning about inconsistent name
        try:
            self.assertEqual(the_pkg.install_dir,
                             Path('certified/skins/editorial/editorial-core-mobile_1.54.0.0'))
        finally:
            simplefilter("default")

    def test_load_from_block(self):
        """Unit test for :py:meth:`utl_lib.tn_package.TNPackage.load_from`
        with sample data from a block package.

        """
        pkg_dir = self.TEST_DATA / 'core-asset-index-gallery_showcase'
        self.assertTrue(pkg_dir.exists())
        the_pkg = TNPackage.load_from(pkg_dir,
                                      'block_core-asset-index-gallery_showcase_1.41.0.1.zip')
        self.assertIsInstance(the_pkg, TNPackage)
        isinstance(the_pkg, TNPackage)
        self.assertEqual(the_pkg.name, 'core-asset-index-gallery_showcase')
        self.assertEqual(the_pkg.version, '1.41.0.1')
        simplefilter("ignore")  # skip UserWarning about inconsistent name
        try:
            self.assertEqual(the_pkg.install_dir,
                             Path('certified/blocks/core-asset-index-gallery_showcase_1.41.0.1'))
        finally:
            simplefilter("default")

    def test_load_from_comp(self):
        """Unit test for :py:meth:`utl_lib.tn_package.TNPackage.load_from`
        with sample data from a component package.

        """
        pkg_dir = self.TEST_DATA / 'components/kh_core_base_library_1.0'
        self.assertTrue(pkg_dir.exists())
        the_pkg = TNPackage.load_from(pkg_dir,
                                      'component_kh_core_base_library_1.0.zip',
                                      site_name='kearneyhub.com')
        self.assertIsInstance(the_pkg, TNPackage)
        isinstance(the_pkg, TNPackage)
        self.assertEqual(the_pkg.name, 'kh_core_base_library')
        self.assertEqual(the_pkg.version, '1.0')
        simplefilter("ignore")  # skip UserWarning about inconsistent name
        try:
            self.assertEqual(the_pkg.install_dir,
                             Path('kearneyhub.com/components/kh_core_base_library_1.0'))
        finally:
            simplefilter("default")

    def test_load_from_error(self):
        """Unit test for :py:meth:`utl_lib.tn_package.TNPackage.load_from`
        with invalid params.

        """
        pkg_dir = self.TEST_DATA / 'no_such_directory'
        self.assertFalse(pkg_dir.exists())
        simplefilter("ignore")
        try:
            self.assertRaises(PackageError, TNPackage.load_from, pkg_dir,
                              'editorial-cover-mobile-1.54.0.0.zip')
        finally:
            simplefilter("default")  # reset since test order not guaranteed

    def test_load_global_skin(self):
        """Unit test for :py:meth:`utl_lib.tn_package.TNPackage.load_from`
        with a global skin directory.

        """
        pkg_dir = str(self.TEST_DATA) + '/agnet_global'
        self.assertTrue(Path(pkg_dir).exists())
        the_pkg = TNPackage.load_from(pkg_dir, 'global_agnet.zip')
        self.assertEqual(the_pkg.app, "global")
        self.assertEqual(the_pkg.name, 'global-agnet')
        self.assertDictEqual(the_pkg.properties,
                             {'app': None,
                              'blockTypes': [],
                              'capabilities': [],
                              'certified': False,
                              'dependencies': [],
                              'description': '',
                              'name': 'global-agnet',
                              'previewImageHeight': None,
                              'previewImageWidth': None,
                              'previewThumbHeight': None,
                              'previewThumbWidth': None,
                              'properties': [],
                              'theme': None,
                              'title': '',
                              'type': 'global',
                              'version': 0})
        self.assertEqual(the_pkg.deps, {})
        self.assertRaises(PackageError, lambda: the_pkg.install_dir)
        the_pkg.site = 'richmond.com'
        simplefilter("ignore")
        # will warn about name discrepancy
        try:
            self.assertEqual(the_pkg.install_dir,
                             Path('richmond.com/global_skins/global-agnet'))
            simplefilter("error")
            self.assertRaises(UserWarning, lambda: the_pkg.install_dir)
        finally:
            simplefilter("default")

    def test_load_warnings(self):
        """Unit test for :py:meth:`utl_lib.tn_package.TNPackage.load_from`
        cases that generate a :py:class:`UserWarning`.

        """

        pkg_dir = self.TEST_DATA / 'empty_global'
        meta_dir = Path(pkg_dir) / '.metadata'
        meta_info = meta_dir / '.meta.json'
        meta_bkp = meta_dir / 'meta.bkp'
        meta_w_discrepancy = meta_dir / 'meta.with_discrepancy'

        self.assertFSAllExist(pkg_dir, meta_info, meta_w_discrepancy)
        self.assertFSNotExists(meta_bkp)

        simplefilter("error")  # easier to catch errors than warnings
        try:
            self.assertDoesNotRaise(Exception, TNPackage.load_from, str(pkg_dir),
                                    'empty_global.zip')
            meta_info.rename(meta_bkp)
            self.assertRaises(UserWarning, TNPackage.load_from, pkg_dir, 'empty_global.zip')
            meta_w_discrepancy.rename(meta_info)
            self.assertRaises(UserWarning, TNPackage.load_from, pkg_dir, 'empty_global.zip')
        finally:
            if meta_info.exists() and not meta_w_discrepancy.exists():
                meta_info.rename(meta_w_discrepancy)
            if not meta_info.exists() and meta_bkp.exists():
                meta_bkp.rename(meta_info)

    def test_bad_zip_name(self):
        """Unit test for :py:meth:`utl_lib.tn_package.TNPackage.install_dir`
        case that generates a :py:class:`ValueError`.

        """
        pkg_dir = self.TEST_DATA / 'core-asset-index-gallery_showcase'
        self.assertTrue(pkg_dir.exists())
        the_pkg = TNPackage.load_from(pkg_dir,
                                      # bad zip name: no pkg type prefix
                                      'core-asset-index-gallery_showcase_1.41.0.1.zip')
        self.assertIsInstance(the_pkg, TNPackage)
        self.assertRaises(ValueError, lambda: the_pkg.install_dir)


if __name__ == '__main__':
    unittest_plus.main()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
