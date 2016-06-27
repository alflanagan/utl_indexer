#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Module to represent a Townnews template package."""

from pathlib import Path
import json
from warnings import warn
import re


class PackageError(Exception):
    """Catchall for exceptions raised by Package class."""

    pass


# pylint: disable=too-many-instance-attributes
class TNPackage(object):
    """A Townnews module that includes files classified as includes, resources, or templates.

    Some packages are TN 'certified' and should always have the same content for a given name
    and version. Packages can be customized on a site-by-site basis and these may contain some
    portion of custom code.

    In most cases, you'll want to use the :py:meth:`Package.load_from` method to read package
    information from a directory. You can specify the exact values to :py:meth:`Package` for
    debugging, etc.

    :see utl_lib.TNPackageZIP: for how an exported ZIP file is written to the directory.

    :param dict props: name-value pairs of package properties

    :param bool is_certified: True if TownNews certification file is found.

    :param dict dependencies: Dictionary (package name ==> version) of required packages.

    :param Path zip_file: Name of the Townnews export ZIP file.

    :param str site_name: The name of the site the ZIP file was exported from. Strictly
        necessary only for customized packages (non-certified).
    """

    # Regexes to match standard Townnews export file names
    block_re = re.compile(r'block_(.+)\.zip')
    global_re = re.compile(r'global_(.+)\.zip')
    component_re = re.compile(r'component_(.+)\.zip')
    skin_re = re.compile(r'skin_([^_]+)_(.+)\.zip')

    GLOBAL_SKIN = "g"
    SKIN = "s"
    BLOCK = "b"
    COMPONENT = "c"
    PACKAGE_TYPES = (
        (GLOBAL_SKIN, "global skin"),
        (SKIN, "application skin"),
        (BLOCK, "block"),
        (COMPONENT, "component"),
    )

    PKG_DIRS = {BLOCK: 'blocks', SKIN: 'skins',
                GLOBAL_SKIN: "global_skins", COMPONENT: 'components', }
    "Name of package parent directory for block package types"

    def __init__(self, props: dict, is_certified: bool, dependencies: dict, zip_file: Path,
                 site_name=None):
        """Build package from parts. Usually call
        :py:meth:`~utl_lib.TNPackage.load_from` instead.

        """
        self.properties = props
        self.is_certified = is_certified
        self.deps = dependencies
        self.zipfile = zip_file
        self.site = site_name

        try:
            self.name = props["name"]
        except KeyError as kerr:
            raise PackageError("Can't get name of package in '{}'. Are you sure it's a "
                               "package file?".format(zip_file)) from kerr

        # global skins don't have version or app values
        self.version = props.get("version")
        if not self.version:
            self.version = "0"
        self.app = props.get("app")
        if not self.app:
            self.app = "global"

    def __str__(self):
        """String representation of package, like 'app/package/version'."""
        site_part = app_part = name_part = ''
        if self.site:
            site_part = "{}: ".format(self.site)
        if self.app:
            app_part = "{}/".format(self.app)
        name_part = "{}/{}".format(self.name, self.version)
        return site_part + app_part + name_part

    @classmethod
    def load_from(cls, directory: Path, zip_name: str, site_name=None) -> "TNPackage":
        """Read a Townnews package from a directory (and subdirectories).

        :param Path directory: The directory containing the unzipped export file.

        :param str zip_name: The name of the export file (for error messages).

        :param str site_name: The name of the site the package was exported from.

        :return: A new TNPackage instance.

        """
        if not isinstance(directory, Path):
            directory = Path(str(directory))
        props = cls._read_properties(directory, zip_name)

        certified = Path(directory, '.certification').exists()

        deps = {}
        dep_file = directory / 'package/dependencies.ini'
        # declaring dependencies is optional, not unusual for file to be missing
        if dep_file.exists():
            with dep_file.open('r') as depin:
                for line in depin:
                    key, value = line[:-1].split('=')
                    deps[key] = value.replace('"', '')
        return cls(props, certified, deps, Path(zip_name), site_name)

    @classmethod
    def _read_meta_config(cls, directory: Path, zip_name: str) -> dict:
        """Read the .meta.json file in `directory`/.metadata/ (if present).

        :param str directory: Directory into which Townnews export ZIP was unzipped.

        :param str zip_name: The name of the Townnews export ZIP file.

        :returns: the key-value pairs from the config file.

        """
        cap_const = 'capabilities'
        meta_file = Path(directory) / ".metadata/.meta.json"

        if meta_file.exists():
            with meta_file.open('r') as metain:
                meta = json.load(metain)
            if cap_const in meta and meta[cap_const] == [""]:
                meta[cap_const] = []
            return meta

        warn("Package {} has no .meta.json file".format(zip_name))
        return {}

    @classmethod
    def _read_config_ini(cls, directory):
        """Read the config.ini file in `directory`/package/ (if present).

        :param str directory: Directory into which Townnews export ZIP was unzipped.

        :returns dict: the key-value pairs from the config file.

        """
        cap_const = 'capabilities'  # protect against misspelling frequently used string :)
        config_file = directory / 'package/config.ini'
        config = {}

        if config_file.exists():
            with config_file.open('r') as propin:
                for line in propin:
                    key, value = line[:-1].split('=')
                    config[key] = value[1:-1]  # drop outer quotes
            if cap_const in config:
                # change to list to match JSON files
                if config[cap_const]:
                    config[cap_const] = config[cap_const].split(',')
                else:
                    config[cap_const] = []

        return config

    @classmethod
    def _read_properties(cls, directory, zip_name):
        """Helper method; load package properties from `directory`.

        :param Path directory: The directory containing the unzipped export file.

        :param str zip_name: The name of the export file (for error messages).

        :returns dict: A ditionary of property: value pairs.

        """

        # ------ Read the 3 possible config files ----------------
        try:
            with (directory / "info.json").open('r') as infoin:
                info = json.load(infoin)
        except FileNotFoundError:
            info = {}

        meta = cls._read_meta_config(directory, zip_name)
        config = cls._read_config_ini(directory)

        # ------ Consolidate values ----------------------

        for key in meta:
            # print("    {}: {}".format(key, meta[key]))
            if key not in info:
                info[key] = meta[key]
            # don't report as error cases where key given value in one file, but empty
            # in the other.
            # BUG: currently won't report error if files have different values that
            # are both falsey, e.g info -> key=0 and meta -> key=[]
            elif info[key] and meta[key] and info[key] != meta[key]:
                # one case where different values is apparently normal
                if not (key == 'type' and info[key] == 'skin' and meta[key] == 'app'):
                    warn("{}: info.json has {}: {} but .metadata.json has {}: {}"
                         "".format(zip_name, key, info[key], key, meta[key]))

        for key in config:
            # .meta.json and config.ini both have version, but config.ini is only correct one
            if key not in info or key == 'version':
                info[key] = config[key]

        return info

    @property
    def install_dir(self):
        """The installation directory name determined by the properties of this package."""
        def warn_inconsistent(matched_name: str):
            """Warns user if name from ZIP file is inconsistent with internal name.

            :param str matched_name: The package name parsed from the ZIP file name.

            """
            if self.name != matched_name:
                warn("Package in {} has inconsistent name: {}".format(self.zipfile, self.name))

        if not self.is_certified and not self.site:
            raise PackageError('Package {} ({}) is non-certified, but no site name was specified.'
                               ''.format(self.name, self.version))

        if self.is_certified:
            top_dir = "certified"
        else:
            top_dir = self.site

        bottom_dir = Path("{}_{}".format(self.name, self.version))

        match = self.block_re.match(self.zipfile.name)
        if match:
            warn_inconsistent(match.group(1))
            middle_dir = Path(self.PKG_DIRS[self.BLOCK])
        else:
            match = self.component_re.match(self.zipfile.name)
            if match:
                warn_inconsistent(match.group(1))
                middle_dir = Path(self.PKG_DIRS[self.COMPONENT])
            else:
                match = self.skin_re.match(self.zipfile.name)
                if match:
                    warn_inconsistent(match.group(2))
                    middle_dir = Path(self.PKG_DIRS[self.SKIN]) / Path(match.group(1))
                else:
                    match = self.global_re.match(self.zipfile.name)
                    if match:
                        warn_inconsistent(match.group(1))
                        # note: globals don't have version
                        bottom_dir = Path(self.name)
                        middle_dir = Path(self.PKG_DIRS[self.GLOBAL_SKIN])
                    else:
                        # oops
                        raise ValueError("I don't know how to unzip file {}: unrecognized prefix."
                                         "".format(self.zipfile))

        assert top_dir and middle_dir and bottom_dir
        return top_dir / middle_dir / bottom_dir
