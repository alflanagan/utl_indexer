#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Module to represent a Townnews template package."""

from pathlib import Path
import json


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

    def __init__(self, props, is_certified, dependencies):
        self.properties = props
        self.is_certified = is_certified
        self.name = props["name"]
        self.version = props["version"]
        self.app = props.get("app", "global")
        self.deps = dependencies

    def __str__(self):
        return "{}/{}/{}".format(self.app, self.name, self.version)

    @classmethod
    def _get_props(cls, directory):
        """Helper method; load package properties from `directory`, return as :py:class:`dict`."""
        # TODO: fix to use files info.json and .metadata/.meta.json, config.ini not always present
        if not hasattr(directory, 'name'):
            directory = Path(directory)
        props = {}
        # known config properties are:
        # apparently required: block_types capabilities name title type version
        # optional: app
        config_file = directory / 'package/config.ini'
        if not config_file.exists():
            raise PackageError("Package configuration file not found.")
        with config_file.open('r') as propin:
            for line in propin:
                key, value = line[:-1].split('=')
                props[key] = value[1:-1]
        return props

    @classmethod
    def load_from(cls, directory):
        """Loads a Townnews package from a directory (and subdirectories)."""
        props = cls._get_props(directory)

        certified = Path(directory, '.certification').exists()

        deps = {}
        dep_file = directory / 'package/dependencies.ini'
        if dep_file.exists:
            with dep_file.open('r') as depin:
                for line in depin:
                    key, value = line[:-1].split('=')
                    deps[key] = value.replace('"', '')
        # dependencies aren't critical information, don't raise error if file missing
        return cls(props, certified, deps)

    @classmethod
    def _get_props2(cls, directory):
        """Helper method; load package properties from `directory`, return as :py:class:`dict`."""
        if not hasattr(directory, 'name'):
            directory = Path(directory)
        props = {}
        info_file = Path(directory) / Path("info.json")
        meta_file = Path(directory) / Path(".metadata/.meta.json")
        with info_file.open('r') as infoin:
            info = json.load(infoin)
        with meta_file.open('r') as metain:
            meta = json.load(metain)
        print("from info.json:")
        for key in info:
            print("    {}: {}".format(key, info[key]))
        print("\nfrom .metadata/.meta.json:")
        for key in meta:
            print("    {}: {}".format(key, meta[key]))
