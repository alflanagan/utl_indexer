#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Module to represent a Townnews template package."""

from pathlib import Path
import json
from warnings import warn


class PackageError(Exception):
    "Catchall for exceptions raised by Package class"
    pass


class TNPackage(object):
    """A Townnews module that includes files classified as includes, resources, or templates.

    Some packages are TN 'certified' and should always have the same content for a given name
    and version. Packages can be customized on a site-by-site basis and these may contain some
    portion of custom code.

    In most cases, you'll want to use the :py:meth:`Package.load_from` method to read package
    information from a directory. You can specify the exact values to :py:meth:`Package` for
    debugging, etc.

    :param dict props: name-value pairs of package properties

    :param Boolean is_certified: True if TownNews certification file is found.

    :param dict dependencies: Dictionary (package name ==> version) of required packages.

    """

    def __init__(self, props: dict, is_certified: bool, dependencies: dict):
        self.properties = props
        self.is_certified = is_certified
        self.name = props["name"]
        # global skins don't have version or app values
        self.version = props.get("version", "0")
        self.app = props.get("app", "global")
        self.deps = dependencies

    def __str__(self):
        return "{}/{}/{}".format(self.app, self.name, self.version)

    @classmethod
    def load_from(cls, directory: Path, zip_name: str) -> "TNPackage":
        """Reads a Townnews package from a directory (and subdirectories).

        :param pathlib.Path directory: The directory containing the unzipped export file.

        :param str zip_name: The name of the export file (for error messages).

        :return: A new TNPackage instance.

        """
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
        return cls(props, certified, deps)

    @classmethod
    def _read_properties(cls, directory, zip_name):
        """Helper method; load package properties from `directory`, return as :py:class:`dict`."""
        CAPABILITIES = 'capabilities'  # protect against misspelling frequently used string :)
        if not hasattr(directory, 'name'):
            directory = Path(directory)
        info = {}
        meta = {}
        config = {}
        info_file = directory / "info.json"
        meta_file = directory / ".metadata/.meta.json"
        config_file = directory / 'package/config.ini'

        # ------ Read the 3 possible config files ----------------
        with info_file.open('r') as infoin:
            info = json.load(infoin)

        if meta_file.exists():
            with meta_file.open('r') as metain:
                meta = json.load(metain)
            if CAPABILITIES in meta and meta[CAPABILITIES] == [""]:
                meta[CAPABILITIES] = []
        else:
            warn("Package {} has no .meta.json file".format(zip_name))

        if config_file.exists():
            with config_file.open('r') as propin:
                for line in propin:
                    key, value = line[:-1].split('=')
                    config[key] = value[1:-1]
            if CAPABILITIES in config:
                # change to list to match JSON files
                if config[CAPABILITIES]:
                    config[CAPABILITIES] = config[CAPABILITIES].split(',')
                else:
                    config[CAPABILITIES] = []

        # ------ Consolidate values ----------------------

        for key in meta:
            # print("    {}: {}".format(key, meta[key]))
            if key not in info:
                info[key] = meta[key]
            elif info[key] != meta[key] and info[key] is not None and meta[key] is not None:
                # one case where different values is apparently normal
                if not (key == 'type' and info[key] == 'skin' and meta[key] == 'app'):
                    warn("{}: info.json has {}: {} but .metadata.json has {}: {}"
                         "".format(zip_name, key, info[key], key, meta[key]))

        for key in config:
            # .meta.json and config.ini both have version, but config.ini is only correct one
            if key not in info or key == 'version':
                info[key] = config[key]
            elif info[key] != config[key] and info[key] is not None and config[key] is not None:
                warn("{}: JSON file has {}: {}, but config.ini has {}: {}"
                     "".format(zip_name, key, info[key], key, config[key]))
        return info
