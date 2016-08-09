#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A base class to handle parsing operations for a UTL file.

| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import sys


# problem with throwing exception on errors is that it halts parsing process
# no good way to resume (?) So error handling is coupled to parser, not user
# of parser
class UTLParseError(Exception):
    """Exceptions raised when a parsing error occurs."""
    pass


# pylint: disable=too-many-public-methods,unused-argument,missing-type-doc
# don't document param type because we don't constrain child classes
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

    :param bool exception_on_error: If True, a syntax error will raise a
        :py:class:`UTLParseError`, which will effectively end processing. Usually one
        wants to continue processing and report all syntax errors encountered.

    :note: In the method docstrings, the phrase 'an "xxxx" production' may be considered
        shorthand for 'the returned value from a call to method "xxxx"'. The latter is the
        concrete results of matching the former.

    """
    # -------------------------------------------------------------------------------------------
    # admin stuff
    # -------------------------------------------------------------------------------------------
    def __init__(self, exception_on_error=False):
        """Exists to provide an end point for super() calls."""
        super().__init__()
        self.exception_on_error = exception_on_error

    def error(self, parser, p):
        """Method called when a syntax error occurs. `p` is a production object with the state
        of the parser at the point where the error was detected.

        The default method raises :py:class:`UTLParseError` with context information.

        :param parser: The parser which called this handler.

        :param list p: The pending productions at time of error. Will be :py:attr:`None` if the
            error is detected at the end of the document.

        :raises UTLParseError: If ``self.exception_on_error`` is :py:attr:`True`.

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
        '''The top-level node for a UTL document.

        :param parser: The parser which called this handler.

        :param statement_list: The result of all the productions for this document.

        '''
        return None

    def statement_list(self, parser, statement=None, statement_list=None):
        '''A list of 0 to many statments.

        :param parser: The parser which called this handler.

        :param statement: A "statement" production, or `None` if document is empty.

        :param statement_list: A "statment_list" production, or `None` when called for the first
            statement in the list.

        '''
        return None

    def statement(self, parser, statement, eostmt=None):
        """A single statement, usually terminated with a ';' or a '%]'.

        :param parser: The parser which called this handler.

        :param statement: A production, or one of the strings: 'continue', 'break', 'exit'.

        :param eostmt: The end-of-statement token (``str``), or ``None``.

        """
        return None

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, parser, expr, statement):
        """A shortcut if statement, which executes the single statement `statement` if `expr`
        evaluates as true.

        :param parser: The parser which called this handler.

        :param expr: An "expr" production.

        :param statement: A "statement" production.

        """
        return None

    def arg(self, parser, expr, name=None):
        """An argument, as in a macro call. Arguments can be in two formats, either a plain
        expression or a key-value pair (separated by ':')

        :param parser: The parser which called this handler.

        :param expr: An "expr" production (the value)

        :param name: The name (``str``) if the argument is named, else ``None``.

        """
        return None

    # NOTE: my_macro(,,4,,5,,7,,) is legal, and NOT equivalent to my_macro(4, 5, 7)!!
    def arg_list(self, parser, arg_or_list, arg=None):
        '''An argument list, as in a macro call.

        :param parser: The parser which called this handler.

        :param arg_or_list: An "arg" production, an "arg_list" production, or ",".

        :param arg: An "arg" production, or ",", or `None`.

        '''
        return None

    # NOTE: [,,4,,5,,7,,] is legal, and equivalent to [4, 5, 7]!!
    def array_elems(self, parser, first_part=None, maybe_comma=None, rest=None):
        """Elements for a simple array (not key/value pairs).

        :param parser: The parser that called this method.

        :param first_part: An "expr" production, an "array_elems" production, a comma (","), or
            ``None``.

        :param maybe_comma: A comma (","), or ``None``.

        :param rest: An "expr" production, or ``None``.

        :note: it is an error if both ``first_part`` and ``rest`` are :py:attr:`None`.

        """
        return None

    def array_literal(self, parser, elements=None):
        """An array literal, like [1, 2, 3] or [1:2, 3:4, 5:6].

        :param parser: The parser which called this handler.

        :param elements: An "array_elems" production, or ``None`` (if literal is '[]').

        :note: Currently the grammar does not call anything for trailing commas in the literal
        expression.

        """
        return None

    def array_ref(self, parser, variable, index):
        """An array reference of the form variable[index].

        :param parser: The parser which called this handler.

        :param variable: An "expr" production identifying the array.

        :param index: An "expr" production identifying the member referenced.

        """
        return None

    def as_clause(self, parser, var1, var2=None):
        """The AS clause of a FOR statement, providing one or two variable names to hold
        successive values from the collection being iterated.

        :param parser: The parser which called this handler.

        :param var1: The ID of the first variable specified.

        :param var2: The ID of the second variable specified, or :py:attr:`None`.

        """
        return None

    def call_stmt(self, parser, macro_call):
        """A call statement, with the keyword call preceding a method call.

        :param parser: The parser which called this handler.

        :param macro_call: An expression production, which should resolve to a macro call.

        """
        return None

    def default_assignment(self, parser, assignment):
        """Assignment with a preceding DEFAULT keyword.

        :param parser: The parser which called this handler.

        :param assignment: The result of an assignment production (as expression).

        """
        return None

    def dotted_id(self, parser, this_id, id_suffix=None):
        """An id made of a name, or two or more names separated by dots.

        :param parser: The parser which called this handler.

        :param str this_id: a string which is an ID or part of an ID.

        :param str id_suffix: None (if `this_id` is the first part of the id), or the result of
            previous calls to :py:meth:`dotted_id`.

        """
        return None

    def echo_stmt(self, parser, expr):
        """An echo statement.

        :param parser: The parser which called this handler.

        :param expr: The object to be displayed: :py:attr:`None`, or the result of a previous
            call to :py:meth:`expr`.

        """
        return None

    def else_stmt(self, parser, statement_list):
        """An else clause.

        :param parser: The parser which called this handler.

        :param statement_list: The body of the else clause, the result of a previous call to
            :py:meth:`statement_list`.

        """
        return None

    def elseif_stmts(self, parser, elseif_stmt, elseif_stmts=None):
        """A production for elseif statements (can also be written 'else if')

        :param parser: The parser which called this handler.

        :param elseif_stmt: An "elseif_stmt" production, or `None` if elseif clause is empty
            (which is permitted by the grammar).

        :param elseif_stmts: An "elseif_stmts" production, or `None`.

        """
        return None

    def elseif_stmt(self, parser, expr, statement_list):
        """An elseif clause, with a `statement_list` to be executed if `expr` is :py:attr:`True`.

        :param parser: The parser which called this handler.

        :param expr: An "expr" production.

        :param statement_list: A "statement_list" production.

        """
        return None

    def eostmt(self, parser, marker_text):
        """End statement marker. Needed for context, etc., but not compilation.

        :param parser: The parser which called this handler.

        :param str marker_text: The actual text of the end-of-statement marker. '' (end of file),
            ';', or '%]'.

        """
        return None

    def expr(self, parser, first, second=None, third=None):
        """An expression production.

        :param parser: The parser which called this handler.

        :param first: An "expr", "literal", "id", or "array_ref" production, or one of the
            strings: "not", "!", "[", "(".

        :param second: An "expr" production, `None`, or a binary expression operator (`str`).

        :param third: An "expr" production, `None`, "]", or ")".

        """
        return None

    def for_stmt(self, parser, expr, as_clause, eostmt, statement_list):
        """A for statement, which executes ``statement_list`` once for each item in the value of
        ``expr`` (assumed to be a collection). If ``as_clause`` has one or two children, the current
        item is assigned to a variable of that name (or the current key, value are assigned to
        variables of those names) for each loop.

        :param parser: The parser which called this handler.

        :param expr: An "expr" production.

        :param as_clause: An "as_clause" production, or ``None``.

        :param eostmt: An end-of-statement delimiter (``str``), or ``None``.

        :param statement_list: A "statement_list" production.

        """
        return None

    def if_stmt(self, parser, expr, eostmt=None, statement_list=None, elseif_stmts=None,
                else_stmt=None):
        """An if statement.

        :param parser: The parser which called this handler.

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

        :param parser: The parser which called this handler.

        :param filename: The result of an expression production, which may or may not be a
            simple string.

        """
        return None

    def literal(self, parser, literal):
        """A literal value: either a string, a number, or an array literal.

        :param parser: The parser which called this handler.

        :param literal: A "string_literal", "number-literal", or "array_literal" prodcution, or a
            string ("false", "true", or "null").

        """
        return None

    def macro_call(self, parser, macro_expr, arg_list=None):
        """A macro procedure call.

        :param parser: The parser which called this handler.

        :param ASTNode macro_expr: An expression, either an ID with the macro name or some
            expression that resolves to a macro reference.

        :param ASTNode arg_list: The list of arguments, if any.

        """
        return None

    def macro_decl(self, parser, macro_name, param_list=None):
        """A macro definition.

        :param parser: The parser which called this handler.

        :param macro_name: A "dotted_id" production, the macro name.

        :param param_list: A "param_list" production, the macro's formal parameters. ``None`` if
            no parameters were specified.

        """
        return None

    def macro_defn(self, parser, macro_decl, eostmt, statement_list=None):
        """A macro definition with signature and body.

        :param parser: The parser which called this handler.

        :param macro_decl: A "macro_decl" production, the macro signature declaration.

        :param eostmt: An "eostmt" production.

        :param statement_list: A "statement_list" production, the macro body. May be ``None`` if
            macro has no statements.

        """
        return None

    def number_literal(self, parser, literal):
        """A numeric literal.

        :param parser: The parser which called this handler.

        :param literal: A valid numeric string which should be interpreted as a number.

        """
        return None

    def param_decl(self, parser, param_id, default_value=None):
        """A parameter declaration.

        :param parser: The parser which called this handler.

        :param str param_id: The parameter name.

        :param default_value: An expression giving the value to use for the parameter if it is
            omitted from the method call.

        """
        return None

    def param_list(self, parser, param_decl, param_list=None):
        '''A list of parameters for a macro definition.

        :param parser: The parser which called this handler.

        :param param_decl: A parameter declaration.

        :param param_list: The parameter list of which `param_decl` is a part, if this is not
            the first production in the list.

        '''
        return None

    def paren_expr(self, parser, expr):
        '''An expr enclosed in parentheses.

        :param parser: The parser which called this handler.

        :param expr: An "expr" production, which was enclosed in parentheses.

        '''
        return None

    def return_stmt(self, parser, expr=None):
        """A return statement.

        :param parser: The parser which called this handler.

        :param expr: An "expr" production for the value to be returned, or ``None`` if no value
            was given.

        """
        return None

    def string_literal(self, parser, literal):
        """A literal string, enclosed in quotation marks.

        :param parser: The parser which called this handler.

        :param literal: The string value (as ``str``).

        """
        return None

    def while_stmt(self, parser, expr, eostmt, statement_list=None):
        """A while statement.

        :param parser: The parser which called this handler.

        :param expr: An "expr" production, which is to be evaluated to true/false.

        :param eostmt: An "eostmt" production.

        :param statement_list: A "statement_list" production for the body of the loop, or
            ``None`` if no body was given.

        """
        return None
