#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module to maintain a JSON file of meta-information in a site directory.

We store certified packages in the certified/ directory to prevent duplication, etc. We can set
up symlinks from the site directories to the packages in certified/. That, however, is kind of
fragile (what if certified/ moves? etc.) so we should have a standard place to record the
certified packages from the site (and of course it allows us to record the version used even if
the certified library is not yet installed.)

This database could easily be extended to store other metadata about the site.

| © 2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
import json
from pathlib import Path


class TNSiteMeta(object):
    """A collection of structured metadata about a TN site which uses TN packages.

    :param str site_name: A name identifying the site, also the name of the top directory for
        site's customized packages.

    :param Path parent_dir: The directory where all the packages are stored; usually this is
        the site directory which is a sibling of "certified"

    :param Path meta_file_path: The data file for the site's meta-information. Usually this is
        ommitted, in which case the file defaults to
        `parent_dir / TNSiteMeta.STANDARD_META_DIR / TNSiteMeta.STANDARD_META_FILENAME`.

    """
    # TODO: Record date/time a package was exported from a site

    # "meta" was chosen as base of names, instead of e.g. "config", to match Townnews usage in
    # packages
    STANDARD_META_FILENAME = Path('site_meta.json')
    STANDARD_META_DIR = Path('.')  # this is relative to the site directory

    def __init__(self, site_name: str, parent_dir: Path, meta_file_path: Path=None):
        self.site = site_name
        self.parent = parent_dir
        if meta_file_path is None:
            self.file = self.parent / self.STANDARD_META_DIR / self.STANDARD_META_FILENAME
        else:
            self.file = meta_file_path
        self.data = {}
        self.loaded = False
        "True if this TNSiteMeta data was loaded from disk."
        if self.file.exists():
            with self.file.open('r') as metain:
                self.data = json.load(metain)
            self.loaded = True
        self.modified = False  # 'dirty' flag

    def save(self):
        """Saves current state in the designated file. If file exists, it will be overwritten."""
        # TODO: save a backup copy
        if self.modified or not self.file.exists():
            with self.file.open('w') as metaout:
                json.dump(self.data, metaout, indent=2)
            print("Wrote meta file {}.".format(self.file))
            self.modified = False

    def add(self, key: str, value: object):
        """Adds a key: value pair to the site config.

        :param str key: A lookup key.

        :param object value: A value of any JSON-serializable type.

        """
        # convert key to string just to be sure
        self.data[str(key)] = value

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
