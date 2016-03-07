#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Script to take a set of Townnews export .zip files and create a useful directory heirarchy.

##############
ZIP File Names
##############

ZIP files are automatically named by the Townnews editor on export. They are prefixed by the main
section from the Design/Templates editor: global\_, skin\_, component\_, block\_

* global_(skin_name).zip
* skin_(application)_(library_name).zip
* component_(library_name).zip
* block_(block_name).zip

The version info, etc. is in within the .zip file so we unzip to a temporary location, then set
up the destination directory, then unzip to there

#######################
Destination Directories
#######################

A Townnews-certified package with a certain name and version should be identical from site to
site. So, we store certified packages under a common "certified" directory, and custom packages
under the site name.

Under "certified" and the site directories we split up packages by type: "global_skins", "skins",
"blocks", and "components". "certified" never has "global_skins", while site directories may not
have any packages for any given type *except* "global_skins".

The "skins" directories in turn have subdirectories for each application: "adowl", "business",
"editorial", etc.

At the bottom level, the directory for a specific global skin package is just the skin name
(they're not versioned). The directories for skins, block and component packages are in the format
*name_version*.

Example Directory Tree
======================

.. code-block:: none

    exports/
        certified/
            skins/
                adowl/
                    adowl-core-base_1.53.0.0/
                business/
                ...
            blocks/
                core-asset-audio-playlist_1.10/
                core-asset-index-bulletins_1.21.1/
            components/
                core_base_business_1.51.0.1/
                core_base_eedition_1.46.0.0/
        dothaneagle/
            global_skins/
                dothaneagle-redesign/
            skins/
            blocks/
            components/
        richmond/
            global_skins/
            skins/
            blocks/
            components/

###################
Types And Functions
###################

"""
import sys
import warnings
from shutil import rmtree

from utl_lib.tn_package import TNPackage

# TODO: For certified packages, create/maintain a database in the site directory that specifies
# that the site uses certified package X, version Y

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


def get_args() -> argparse.Namespace:
    """Parse command-line arguments, return namespace with values.

    Validate that first two arguments are existing directories; if not, write error message and
    abort program.

    """
    mydesc = ("Writes the contents of a group of ZIP files to a standard directory structure "
              "for Townnews template exports.")
    parser = argparse.ArgumentParser(description=mydesc)
    parser.add_argument('site', type=str,
                        help="The site name (or name of directory for custom packages)")
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


def mktmpdir() -> Path:
    """Create an empty temporary directory.

    :returns: Name of the created directory.

    """
    args = ['mktemp', '-d', 'utl_indexer_XXXXXX', '-t']
    # run mktemp, get printed name, convert to Unicode and remove trailing '\n'
    return Path(subprocess.check_output(args).decode()[:-1])


def unzip_file(filename: Path, parent_dir: Path):
    """Unzip file to a temporary directory.

    :param pathlib.Path filename: The name of the ZIP file.

    :param pathlib.Path parent_dir: The directory to receive the contents of `filename`.

    """
    # Usage: unzip [-Z] [-opts[modifiers]] file[.zip] [list] [-x xlist] [-d exdir]
    # -d  extract files into exdir
    # -q  quiet mode (-qq => quieter)
    # -a  auto-convert any text files
    args = ['unzip', '-d', str(parent_dir), '-q', str(filename)]
    subprocess.check_call(args)


# pylint: disable=W0613, R0913
def showwarning(message, category, filename, lineno, file=None, line=None):
    """Hook to write a warning to a file; override of :py:func:`warnings.showwarning`

    :param str message: The warning message.

    :param str category: The warning category.

    :param str filename: The filename of the file where the warning was generated.

    :param int lineno: The line of file `filename` where the warning occurred.

    :param file: Output file (defaults to :py:attr:`sys.stderr`).

    :param line: The text of the line where the error was generated (defaults to line number
        `lineno` in internal line cache.)

    """
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


def main(args: argparse.Namespace):
    """Unzip each file, placing contents in desired directory structure.

    :param argparse.Namespace args: The parsed command-line arguments.

    """
    for zip_file in Path(args.source_dir).glob('*.zip'):
        tmp_dir = mktmpdir()
        try:
            unzip_file(zip_file, tmp_dir)
            tmp_pkg = TNPackage.load_from(tmp_dir, zip_file, args.site)
            new_parent = args.dest_dir / tmp_pkg.install_dir
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
