#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List currently stored Townnews-certified packages.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""

import re
import argparse
from pathlib import Path
from utl_lib.tn_package import TNPackage
from warnings import filterwarnings

DATA_DIR = Path('data/exported/certified')
BLOCKS_DIR = DATA_DIR / Path('blocks')
COMPS_DIR = DATA_DIR / Path('components')
SKINS_DIR = DATA_DIR / Path('skins')
PACKAGE_PARTS = re.compile(r'(.+)?_([0-9.-_]+)')

APPS = {'editorial': 'Editorial',
        'adowl': 'Ad-Owl',
        'business': 'Business',
        'calendar': 'Calendar',
        'classifieds': 'Classifieds',
        'eedition': 'e-Editions',
        'electionsstats': 'Election Stats',
        'form': 'Form',
        'mailinglist': 'mailinglist',
        'search': 'search',
        'sportsstats': 'Sportsstats',
        'staticpages': 'staticpages',
        'user': 'user',
       }


def get_args():
    parser = argparse.ArgumentParser(description="Lists certified packages stored in export directories.")
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument('-c', '--components', action="store_true",
                     help="List components only")
    meg.add_argument('-b', '--blocks', action="store_true",
                     help="List blocks only")
    meg.add_argument('-s', '--skins', action="store_true",
                     help="List skins only")
    return parser.parse_args()


def pkg_format(pkg_name):
    """Formats package name from download to '<package-name> (<version>)'."""
    # TODO: Get block title from .metadata
    match = PACKAGE_PARTS.match(pkg_name)
    if not match:
        return pkg_name
    else:
        return "{} ({})".format(match.group(1), match.group(2))


def main(args):
    """Print lists as filtered by command-line arguments"""
    filterwarnings("ignore", category=Warning)
    block_data = []
    if not (args.components or args.skins):
        print("="*8 + " BLOCKS " + "="*8)
        for block in BLOCKS_DIR.glob('*'):
            if block.is_dir():
                pkg = TNPackage.load_from(block, "{}.zip".format(block.name))
                block_data.append("{} ({})".format(pkg.properties['title'], pkg.version))
    block_data.sort(key=lambda x:x.upper())
    for data in block_data:
        print(data)

    if not(args.blocks or args.skins):
        print("="*8 + " COMPONENTS " + "="*8)
        comp_data = []
        for comp in COMPS_DIR.glob('*'):
            if comp.is_dir():
                pkg = TNPackage.load_from(comp, "{}.zip".format(comp.name))
                comp_data.append("{} ({})".format(pkg.properties['title'], pkg.version))
        comp_data.sort(key=lambda x: x.upper())
        for data in comp_data:
            print(data)

    if not(args.blocks or args.components):
        print("="*8 + " SKINS " + "="*8)
        skin_data = []
        for app_dir in SKINS_DIR.glob('*'):
            if app_dir.is_dir():
                for skin in app_dir.glob('*'):
                    if skin.is_dir():
                        pkg = TNPackage.load_from(skin, "{}.zip".format(skin.name))
                        skin_data.append("{}::{} ({})".format(pkg.app,
                                                              pkg.properties['title'],
                                                              pkg.version))
        skin_data.sort(key=lambda x: x.upper())
        for data in skin_data:
            print(data)


if __name__ == '__main__':
    main(get_args())
