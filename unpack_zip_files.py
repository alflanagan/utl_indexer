#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Script to take a set of Townnews export .zip files and create a useful directory heirarchy."""

# zip files are prefixed by the main section in the Design/Templates editor:
#  global_, skin_, component_, block_
# global_(skin_name).zip
# skin_(application)_(library_name).zip
# component_(library_name).zip
# block_(block_name).zip
# version info, etc. is in within the .zip
# so will need to unzip to a temporary location, then set up parent directory(ies), then move

import sys
import re
import warnings
from shutil import rmtree

from utl_lib.tn_package import TNPackage, PackageError


def validate_python_version():
    """Check current python version: must be 3.5 or greater, for :py:mod:`pathlib` and
    :py:mod:`subprocess` features added in that release.

    """
    this_version = sys.version_info
    if this_version.major < 3 or (this_version.major == 3 and this_version.minor < 5):
        sys.stderr.write("Sorry, this program requires standard features from python version 3.5"
                         " or higher.\n")
        sys.exit(255)


# die without trying to run rest of file
validate_python_version()

# delay import of recently added libraries, to use version error message instead of "not found"
# pylint: disable=wrong-import-position,wrong-import-order
import subprocess
from pathlib import Path
import argparse


def get_args():
    """Parse command-line arguments, return namespace with values.

    Validate that first two arguments are existing directories; if not, write error message and
    abort program.

    """
    mydesc = ("Writes the contents of a group of ZIP files to a standard directory structure "
              "for Townnews template exports.")
    parser = argparse.ArgumentParser(description=mydesc)
    parser.add_argument('source_dir', type=str,
                        help="The directory containing source ZIP files.")
    parser.add_argument('dest_dir', type=str,
                        help="The directory under which the new directories will be created.")
    parser.add_argument('--overwrite', action='store_true',
                        help="Replace contents if destination directory exists "
                        "(default: exit w/error)")
    parsed = parser.parse_args()
    parsed.source_dir = Path(parsed.source_dir)
    parsed.dest_dir = Path(parsed.dest_dir)
    if not parsed.source_dir.is_dir():
        sys.stderr.write("{} not found, or is not a directory.\n".format(parsed.source_dir))
        sys.exit(1)
    if not parsed.dest_dir.is_dir():
        sys.stderr.write("{} not found, or is not a directory.\n".format(parsed.dest_dir))
        sys.exit(2)
    return parsed


class BadPackageError(Exception):
    """Raised when important package information is invalid or missing."""
    pass


def mktmpdir():
    """Create an empty temporary directory.

    :returns Path: Name of the created directory.

    """
    args = ['mktemp', '-d', 'utl_indexer_XXXXXX', '-t']
    # run mktemp, get printed name, convert to Unicode and remove trailing '\n'
    return Path(subprocess.check_output(args).decode()[:-1])


def unzip_file(filename, parent_dir):
    """Unzip file to a temporary directory.

    :param Path filename: The name of the ZIP file.

    :param Path parent_dir: The directory to receive the contents of `filename`.

    """
    # Usage: unzip [-Z] [-opts[modifiers]] file[.zip] [list] [-x xlist] [-d exdir]
    # -d  extract files into exdir
    # -q  quiet mode (-qq => quieter)
    # -a  auto-convert any text files
    args = ['unzip', '-d', str(parent_dir), '-q', str(filename)]
    subprocess.check_call(args)


def determine_dest_dir(zip_file, reference_dir, destination):
    """From ZIP file name and contents, determine name of destination directory where files
    should be placed.

    :param Path zip_file: The ZIP file being unzipped.
    :param Path reference_dir: The directory with the contents of `zip_file` unzipped.
    :param object args: The namespace containing command-line arguments.

    """
    block_re = re.compile(r'block_(.+)\.zip')
    global_re = re.compile(r'global_(.+)\.zip')
    component_re = re.compile(r'component_(.+)\.zip')
    skin_re = re.compile(r'skin_([^_]+)_(.+)\.zip')

    try:
        pkg = TNPackage.load_from(reference_dir)
    except PackageError as perr:
        raise BadPackageError(str(zip_file)) from perr

    subdir = Path("{}_{}".format(pkg.name, pkg.version))
    match = block_re.match(zip_file.name)
    if match:
        if pkg.name != match.group(1):
            warnings.warn("Package in {} has inconsistent name: {}".format(zip_file, pkg.name))
        return destination / Path('blocks') / subdir

    match = component_re.match(zip_file.name)
    if match:
        if pkg.name != match.group(1):
            warnings.warn("Package in {} has inconsistent name: {}".format(zip_file, pkg.name))
        return destination / Path('components') / subdir

    match = skin_re.match(zip_file.name)
    if match:
        if pkg.name != match.group(2):
            warnings.warn("Package in {} has inconsistent name: {}".format(zip_file, pkg.name))
        return destination / Path('skins') / Path(match.group(1)) / subdir

    match = global_re.match(zip_file.name)
    if match:
        if pkg.name != match.group(1):
            warnings.warn("Warning: package in {} has inconsistent name: {}"
                          "".format(zip_file, pkg.name))
        # note: globals don't have version
        return destination / Path('global_skins') / pkg.name
    # oops
    raise ValueError("I don't know how to unzip file {}: unrecognized prefix."
                     "".format(zip_file))


# pylint: disable=W0613, R0913
def showwarning(message, category, filename, lineno, file=None, line=None):
    """Hook to write a warning to a file; override of warnings.showwarning"""
    if file is None:
        file = sys.stderr
        if file is None:
            # sys.stderr is None when run with pythonw.exe - warnings get lost
            return
    try:
        # our only difference from warnings.showwarning: pass '' as line
        file.write(warnings.formatwarning(message, category, filename, lineno, ''))
    except OSError:
        pass  # the file (probably stderr) is invalid - this warning gets lost.
warnings.showwarning = showwarning


def main(args):
    """Unzip each file, placing contents in desired directory structure."""
    # MAYBE: remove repetitive source line output from warning messages by overriding
    #  warnings.showwarning(message, category, filename, lineno, file=None, line=None)
    for zip_file in Path(args.source_dir).glob('*.zip'):
        tmp_dir = mktmpdir()
        try:
            unzip_file(zip_file, tmp_dir)
            new_parent = determine_dest_dir(zip_file, tmp_dir, args.dest_dir)
            if new_parent.exists():
                if args.overwrite:
                    rmtree(str(new_parent))
                else:
                    sys.stderr.write("Won't overwrite existing directory '{}'.\n"
                                     "".format(new_parent))
                    continue
            print("Creating {}".format(new_parent))
            new_parent.mkdir(parents=True)
            unzip_file(zip_file, new_parent)
        finally:
            rmtree(str(tmp_dir))


if __name__ == '__main__':
    main(get_args())
