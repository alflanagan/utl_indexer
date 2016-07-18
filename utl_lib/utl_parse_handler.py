#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A base class to handle parsing operations for a UTL file.

| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import sys
import collections


class FrozenDict(collections.Mapping):
    """Immutable dictionary class by Raymond Hettinger himself.

    This allows handlers to return context info in a form that has the goodness of immutability,
    and is hashable.

    :param collections.Mapping somedict: A mapping whose values will be used to initialize the
        FrozenDict. Note this is the only way to add values!

    """
    # TODO: add an .update() method that returns a new FrozenDict
    def __init__(self, somedict=None):
        if somedict is None:
            somedict = {}
        self._dict = dict(somedict)   # make a copy
        # if values of self._dict are not hashable, we're not hashable. Fail now.
        self._hash = hash(frozenset(self._dict.items()))

    def __getitem__(self, key):
        return self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return self._dict == other._dict  # pylint: disable=W0212

    def combine(self, *args, **keys):
        """D.combine([E, ]**F) -> D'.  Create FrozenSet D' from D and dict/iterable E and F.

    D' is initially a copy of D.
    If E is present and has a .keys() method, then does:  for k in E: D'[k] = E[k]
    If E is present and lacks a .keys() method, then does:  for k, v in E: D'[k] = v
    In either case, this is followed by: for k in F:  D'[k] = F[k]

    :param args: one more dictionaries to be combined with this one.

    :param keys: key-value pairs that will be combined with this dictionary.

    :return: A new FrozenDict combining all the keys and values.

    :rtype: FrozenDict

    """
        # yes, above is a direct steal from dict.update() docstring.
        newdict = self._dict.copy()
        newdict.update(*args, **keys)
        return FrozenDict(newdict)

    def delkey(self, *args):
        """D.delkey(key [, ...]) -> D' which contains {key:D[key] for key in D if key not in args}

        :param str args: One or more keys to delete.

        :return: A new dictionary without those keys.
        :rtype: FrozenDict

        """
        newdict = self._dict.copy()
        for arg in args:
            del newdict[arg]
        return FrozenDict(newdict)

    def __str__(self):
        return "frozen: {}".format(self._dict)

    def __repr__(self):
        return "FrozenDict({})".format(repr(self._dict))


# problem with throwing exception on errors is that it halts parsing process
# no good way to resume (?) So error handling is coupled to parser, not user
# of parser
class UTLParseError(Exception):
    """Exceptions raised when a parsing error occurs."""
    pass


# pylint: disable=unused-argument,too-many-public-methods,W9003,W9004
class UTLParseHandler(object):
    """A base class defining an interface for classes which take actions on parse reductions for
    a UTL file. Implementors can inherit this class and only override those reductions where
    they want an action taken.

    This separates the actual parsing logic from the code that does something with the parse,
    enabling the parser to be reused for multiple applications.

    Each method takes the parser object as its first parameter, then one or more parameters
    corresponding to the elements in the parse production. It should in turn return an object
    which can be passed on to subsequent higher-level methods (except for
    :py:meth:`~utl_lib.utl_parse_handler.utldoc` which is the top level).

    An overriden handler method must return an object with an attribute named `context` which
    will be mapping with (at least) the contents of `parser.context`, to be used in higher-level
    productions.

    Note that the parser object passed in will be dynamically updated between calls; methods
    should not store it and expect to retrieve attributes later. Rather the attributes should be
    retrieved and stored during the method call.

    :param boolean exception_on_error: If True, a syntax error will raise a
        :py:class:`UTLParseError`, which will effectively end processing. Usually
        one wants to continue processing and report all syntax errors
        encountered.

    """
    # -------------------------------------------------------------------------------------------
    # admin stuff
    # -------------------------------------------------------------------------------------------
    def __init__(self, exception_on_error=False, *args, **kwargs):
        """Exists to provide an end point for super() calls."""
        super().__init__(*args, **kwargs)
        self.exception_on_error = exception_on_error

    def state(self, value, msg=""):
        """Like assert, but raises a UTLParseError."""
        if not value:
            raise UTLParseError("Assertion failed! Internal error in parser." + msg)

    def error(self, parser, p):
        """Method called when a syntax error occurs. `p` is a production object with the state
        of the parser at the point where the error was detected.

        The default method raises UTLParseError with context information.
        """
        if p is None:
            if self.exception_on_error:
                raise UTLParseError("Syntax error at end of document! Symbol stack is {}"
                                    "".format(parser.symstack))
            else:
                sys.stderr.write("Syntax error at end of document! Symbol stack is {}\n"
                                 "".format(parser.symstack))
        else:
            the_lexer = p.lexer
            lineoffset = the_lexer.lexdata.rfind('\n', 0, the_lexer.lexpos)
            if lineoffset == -1:  # we're on first line
                lineoffset = 0
            lineoffset = the_lexer.lexpos - lineoffset
            if self.exception_on_error:
                raise UTLParseError("Syntax error in input line {}, column {} after '{}'!"
                                    "".format(p.lineno, lineoffset, p.value))
            else:
                sys.stderr.write("Syntax error in input line {}, column {} after '{}'!\n"
                                 "".format(p.lineno, lineoffset, p.value))

    # -------------------------------------------------------------------------------------------
    # top-level productions
    # -------------------------------------------------------------------------------------------
    def utldoc(self, parser, statement_list):
        '''The top-level node for a UTL document.'''
        return None

    def statement_list(self, parser, statement=None, statement_list=None):
        '''A statement_list production. `statement_list`, if not :py:attr:`None`, is the
        statement list seen so far; `statement` is the result of the current statement parse.

        '''
        return None

    def statement(self, parser, statement, eostmt=None):
        """A single statement, usually terminated with a ';' or a '%]'.

        `statement` will be the text of a token, or the result of a production.

        `eostmt` will be the end-of-statement value, if it exists.

        Tokens that may be provided include 'continue', 'break', and 'exit'.

        """
        return None

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, parser, expr, statement):
        """A shortcut if statement, which executes the single statement `statement` if `expr`
        evaluates as true.

        """
        return None

    def arg(self, parser, expr, name=None):
        """An argument, as in a macro call. Arguments can be in two formats, either a plain
        expression or a key-value pair (separated by ':')

        :param expr: the result of an expression production for the argument

        :param name: the name if the argument is named.

        """
        return None

    def arg_list(self, parser, arg, arg_list=None):
        '''An argument list, as in a macro call. `arg` is an argument (see :py:meth:`arg`), or
        None for a call with no arguments.

        `arg_list`, if not None, is the output of previous processing of this argument list.

        '''
        return None

    def array_elems(self, parser, expr, array_elems=None):
        """Elements for a simple array (not key/value pairs).

        :param expr: An expression production for the current element value.

        :param array_elems: The result of a previous array_elems production for this array.

        """
        return None

    def array_literal(self, parser, elements=None):
        """An array literal, like [1, 2, 3] or [1:2, 3:4, 5:6]. `elements`, if present, is the
        result of the expansion of the elements inside the [].

        """
        return None

    def array_ref(self, parser, variable, index):
        """An array reference of the form variable[index]."""
        return None

    def as_clause(self, parser, var1, var2=None):
        """The AS clause of a FOR statement, providing one or two variable names to hold
        successive values from the collection being iterated.

        """
        return None

    def call_stmt(self, parser, macro_call):
        """A call statement, with the keyword call preceding a method call.

        :param macro_call: An expression production, which should resolve to a macro call.

        """
        return None

    def default_assignment(self, parser, assignment):
        """Assignment with a preceding DEFAULT keyword.

        :param assignment: The result of an assignment production (as expression).

        """
        return None

    def dotted_id(self, parser, this_id, id_suffix=None):
        """An id made of a name, or two or more names separated by dots.

        `id_suffix` will be :py:attr:`None`, if `this_id` is the first part of the id, or the
        result of productions of the parts of the id previous to `this_id`.

        """
        return None

    def echo_stmt(self, parser, expr):
        """An echo statement. `expr` is the object to be echoed, or :py:attr:`None`."""
        return None

    def else_stmt(self, parser, statement_list):
        """An else clause."""
        return None

    def elseif_stmts(self, parser, elseif_stmt, elseif_stmts=None):
        """A production for elseif statements (can also be written 'else if')"""
        return None

    def elseif_stmt(self, parser, expr, statement_list=None):
        """An elseif clause, with a `statement_list` to be executed if `expr` is
        :py:attr:`True`.

        """
        return None

    def eostmt(self, parser, marker_text):
        """End statement marker. Unlikely to be useful, but if you need it, it's here."""
        return None

    def expr(self, parser, first, second=None, third=None):
        """An expression production.

        :param [str, ASTNode] first: not|!|expr|literal|ID|LBRACKET|LPAREN|array_ref

        :param [str, ASTNode] second: expr|PLUS|MINUS|TIMES|DIV|MODULUS|FILTER|DOUBLEBAR|RANGE|
            NEQ|LTE|OR|LT|EQ|IS|GT|AND|GTE|DOUBLEAMP|DOT|ASSIGN|ASSIGNOP|COMMA|COLON

        :param [str, ASTNode] third: expr|RBRACKET|RPAREN

        """
        return None

    def for_stmt(self, parser, expr, as_clause=None, eostmt=None, statement_list=None):
        """A for statement, which executes `statement_list` once for each item in the value of
        `expr` (assumed to be a collection). If `as_clause` has one or two children, the current
        item is assigned to a variable of that name (or the current key, value are assigned to
        variables of those names) for each loop.

        """
        return None

    def if_stmt(self, parser, expr, eostmt=None, statement_list=None, elseif_stmts=None,
                else_stmt=None):
        """An if statement.

        :param expr: the test expression. `statement_list` is executed only if this resolves to
            :py:attr:`True`.

        :param eostmt: The end-of-statement value separating expr from statement_list

        :param statement_list: The statements to execute if the test is true.

        :param elseif_stmts: 0 to many elseif statements giving alternate conditions.

        :param else_stmt: The statements to execute if all tests return :py:attr:`False`.

        """
        return None

    def include_stmt(self, parser, filename):
        """An include statement to insert the contents of file `filename`.

        :param filename: The result of an expression production, which may or may not be a
            simple string.

        """
        return None

    def literal(self, parser, literal):
        """A literal value: either a string, a number, or an array literal."""
        return None

    def macro_call(self, parser, macro_expr, arg_list=None):
        """A macro procedure call.

        :param ASTNode macro_expr: An expression, either an ID with the macro name or some
            expression that resolves to a macro reference.

        :param ASTNode arg_list: The list of arguments, if any.

        """
        return None

    def macro_decl(self, parser, macro_name, param_list=None):
        """A macro definition. `macro_name` is the name of the macro, `param_list` is the list
        of formal parameters, or :py:attr:`None`.

        """
        return None

    def macro_defn(self, parser, macro_decl, eostmt, statement_list=None):
        """A macro definition with declaration `macro_decl` containing statements
        `statement_list`. `statement_list` can also be :py:attr:`None`, indicating an empty
        macro (which is legal but useless).

        """
        return None

    def number_literal(self, parser, literal):
        """A numeric literal."""
        return None

    def param_decl(self, parser, param_id, default_value=None):
        """A parameter declaration.

        :param str param_id: The parameter name.

        :param default_value: An expression giving the value to use for the parameter if it is
            omitted from the method call.

        """
        return None

    def param_list(self, parser, param_decl, param_list=None):
        '''A list of parameters for a macro definition.

        :param param_decl: A parameter declaration.

        :param param_list: The parameter list of which `param_decl` is a part, if this is not
            the first production in the list.

        '''
        return None

    def paren_expr(self, parser, expr):
        '''An expr enclosed in parentheses.'''
        return None

    def return_stmt(self, parser, expr=None):
        """A return statement. If `expr` is not :py:attr:`None`, it is the return value."""
        return None

    def string_literal(self, parser, literal):
        """A literal string, enclosed in quotation marks."""
        return None

    def while_stmt(self, parser, expr, statement_list=None):
        """A while statement, where `expr` is the test and `statement_list` is the body."""
        return None
