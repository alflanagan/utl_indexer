#!/usr/bin/env python3
"""Script to use UTL parser to print out include file trees for a given source file."""

import argparse
from pathlib import Path

from utl_lib.utl_yacc import UTLParser
from utl_lib.handler_ast import UTLParseHandlerAST, UTLParseError


class OrderedSet(object):  # pylint:disable=R0903
    """A collection with set-like behavior, except it preserves the order in which the first
    occurence of each item was seen.

    """
    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        """Iterator that returns the items from the source iterator, omitting all duplicates."""
        already_seen = set()
        for item in self.iterator:
            if item not in already_seen:
                yield item
                already_seen.add(item)


class FileWithIncludes(object):
    """A .utl file, which may include other UTL files.

    :param (str or Path) filename: The file, relative to the top-level directory
        (`args.utl_path`), or the global or application skin directories. Note that the file
        doesn't have to actually exist as long as no operation that requires a parse is
        performed.

    :param args: The command-line arguments collected by the :py:mod:`argparse` parser.

    """
    def __init__(self, filename, args):
        if hasattr(filename, "name"):
            self.fname = filename
        else:
            self.fname = Path(filename)
        self._included = []
        self.args = args
        self.is_parsed = False
        self._disk_path = None
        self._source = ""  # will get set by disk_path() if found

    @property
    def included(self):
        """Returns an iterator over the files included in this file.

        :raises FileNotFoundError: if the file does not exist relative to any of
            `args.utl_path`, the global skin, or the application skin.

        """
        if not self.is_parsed and self.disk_path:
            self.do_parse(self.args)
        return self._included

    @property
    def source(self):
        """Which skin the file was found in.

        :returns str: 'global' if file found in global skin, 'application' if in application skin,
            '' otherwise

        """
        _ = self.disk_path  # make sure we've looked for file
        return self._source

    def add(self, new_include):
        """Adds `new_include` to our list of included files.

        :param (str or FileWithIncludes) new_included: the include file to add.

        """
        if not hasattr(new_include, 'included'):
            new_include = FileWithIncludes(new_include, self.args)
        self._included.append(new_include)

    @classmethod
    def get_includes(cls, ast_node):
        """Walks the tree rooted at `ast_node` looking for ``include`` statements.

        :param utl_lib.ast_node.AstNode ast_node: The root of an AST.

        :returns iterator: The included filenames found (as :py:class:`str`), in the order
            found. Files included more than once will occur in the sequence more than once.

        """
        # it would, of course, be faster to do this as a loop.
        if ast_node.symbol == 'include':
            if ast_node.attributes["file"] != '<expr>':
                yield ast_node.attributes["file"]
            else:
                # the include statement referenced a dynamic expression instead of a literal name
                # we check for this string in is_expression(): if you change this, change that
                yield 'expression: ' + str(ast_node.children[0])
        for child_node in ast_node.children:
            yield from cls.get_includes(child_node)

    def do_parse(self, args, program_text=''):
        """Parse the file and get list of included files.

        :param args: The arguments returned by the :py:mod:`argparse` parser.

        :param str program_text: The text of the file to be parsed.

        :raise FileNotFoundError: if the file does not exist relative to the `args.utl_path`
            directory, the global skin, or the application skin.

        """
        # build AST tree for later processing
        handlers = [UTLParseHandlerAST()]
        myparser = UTLParser(handlers, args.verbose)
        if not program_text:
            if not self.disk_path:
                raise FileNotFoundError(self.disk_path)
            with self.disk_path.open('r') as textin:
                program_text = textin.read()
        results = myparser.parse(program_text, debug=args.debug, print_tokens=False,
                                 filename=self.fname.name)
        if results:
            self.is_parsed = True
            included = self.get_includes(results)
            if args.norepeat:
                # pylint: disable=R0204
                included = OrderedSet(included)
            for include in included:
                self.add(include)
        else:
            raise UTLParseError('Parse FAILED: {}'.format(self.fname))

    @property
    def disk_path(self):
        """The full path on disk to the named file, if such file exists.

        If the file does not exist, returns ``None``. No error is raised.

        """
        if self._disk_path is None:  # cached for efficiency
            if self.is_expression:
                # whoops, we're up a creek
                return None
            if self.fname.exists():
                # generally only true for top-level file
                self._disk_path = self.fname
                return self._disk_path
            # check for override in global skin
            if self.args.global_skin:
                the_file = (Path(self.args.utl_path) / Path("global_skins") /
                            Path(self.args.global_skin) / Path("includes") / Path(self.fname))
                if the_file.exists():
                    self._disk_path = the_file
                    self._source = "global"
                    return self._disk_path
            # now try the application skin
            if self.args.skin:
                the_file = (Path(self.args.utl_path) / Path("skins") / Path(self.args.skin) /
                            Path('includes') / Path(self.fname))
                if the_file.exists():
                    self._source = "application"
                    self._disk_path = the_file
        return self._disk_path

    @property
    def is_expression(self):
        """Returns ``True`` if this include file is named by an expression, not a literal string."""
        return self.fname.name.startswith('expression: ')

    def display(self, initial_indent='', top_level=True):
        """Display this file's name followed by an indented list of files it includes.

        :param str initial_indent: String to prepend to each output line.

        :param bool top_level: If ``True``, prints a top-level header.

        """
        if top_level:
            print("{}Included by {}{}:".format(initial_indent, self.fname,
                                               " (repeats omitted)" if self.args.norepeat
                                               else ""))
        else:
            suffix = ''
            if not self.disk_path and not self.args.nofilecheck and not self.is_expression:
                suffix = " (not found)"
            elif self.source:
                suffix = " ({})".format(self.source)

            print("{}{}{}".format(initial_indent, self.fname, suffix))

        if top_level or not (self.args.norecurse or self.args.nofilecheck):
            new_indent = initial_indent + ' ' * 4
            for include in self.included:
                include.display(new_indent, False)


def get_args():
    """Parses command-line arguments, returns namespace with values."""
    parser = argparse.ArgumentParser(
        description="Searches UTL files and reports include dependencies.")
    parser.add_argument('utl_path', type=str,
                        help="The top-level directory of the collection of UTL files to be parsed.")
    parser.add_argument('utl_file', type=argparse.FileType('r'),
                        help="The UTL template file whose dependencies are reported.")
    parser.add_argument('--verbose', action='store_true',
                        help="Enable output about conflicts, and create parser.out file.")
    parser.add_argument('--norepeat', action='store_true',
                        help="Report each file only on the first include (otherwise reports all)")
    parser.add_argument('--norecurse', action='store_true',
                        help="Report only files directly included into utl_file")
    parser.add_argument('--nofilecheck', action='store_true',
                        help=("Omit usual attempt to verify include file exists"
                              " (implies --norecurse)"))
    parser.add_argument('--global_skin', type=str,
                        help="Name of the global skin (to check for site override)")
    parser.add_argument('--skin', type=str,
                        help="The name of the skin to apply (ex. 'editorial/core/base-1.53.0.1')")
    # TODO: Fix --skin so it takes the skin name displayed in TN URL map
    parser.add_argument('--debug', action='store_true',
                        help="Print grungy parsing details.")
    return parser.parse_args()


def main(args):
    """Main function. Creates an instance of :py:class:`FileWithIncludes`, displays it."""
    utl = FileWithIncludes(args.utl_file.name, args)

    utl.display()


if __name__ == '__main__':
    main(get_args())
