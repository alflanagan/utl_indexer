#!/usr/bin/env python3
"""A base class to handle parsing operations for a UTL file."""


class UTLParseError(Exception):
    """Exceptions raised when a parsing error occurs."""
    pass


# pylint: disable=unused-argument,too-many-public-methods
class UTLParseHandler(object):
    """A base class defining an interface for classes which take actions on parse reductions for
    a UTL file. Implementors can inherit this class and only override those reductions where
    they want an action taken.

    This separates the actual parsing logic from the code that does something with the parse,
    enabling the parser to be reused for multiple applications.

    Each method will take one or more parameters corresponding to the elements in the parse
    production. It should in turn return an object which can be passed on to subsequent
    higher-level methods (except for :py:meth:`~utl_lib.utl_parse_handler.utldoc` which is the
    top level).

    """

    def utldoc(self, statement_list):
        '''The top-level node for a UTL document.'''
        return None

    def statement_list(self, statement, statement_list=None):
        '''A statement_list production. `statement_list`, if not :py:attr:`None`, is the
        statement list seen so far; `statement` is the result of the current statement parse.

        '''
        return None

    def statement(self, statement, is_document=False):
        """A single statement, usually terminated with a ';' or a '%]'.

        If `is_document` is :py:attr:`True`, then `statement` is the contents of a DOCUMENT.

        Otherwise, `statement` will be the text of a token, or the result of a production.

        Tokens that may be provided include 'continue', 'break', and 'exit'.

        """
        return None

    def end_stmt(self, marker_text):
        """End statement marker. Unlikely to be useful, but if you need it, it's here."""
        return None

    def echo_stmt(self, expr):
        """An echo statement. `expr` is the object to be echoed, or :py:attr:`None`."""
        return None

    def expr(self, lhs, rhs, operator, value):
        """An expression production. `lhs` is the left side of the infix operator, `rhs` is the
        right side (or None for unary operators), `operator` is the operator itself. `value` is
        used for expressions with no operators.

        """
        return None

    def param_list(self, param_decl, param_list=None):
        '''A list of parameters for a macro definition.

        :param param_decl: A parameter declaration.

        :param param_list: The parameter list of which `param_decl` is a part, if this is not
            the first production in the list.

        '''
        return None

    def param_decl(self, param_id, default_value=None):
        """A parameter declaration.

        :param str param_id: The parameter name.

        :param default_value: An expression giving the value to use for the parameter if it is
        omitted from the method call.

        """
        return None

    def arg_list(self, arg, arg_list=None):
        '''An argument list, as in a macro call. `arg` is an argument (see :py:meth:`arg`), or None for a call with no arguments.

        `arg_list`, if not None, is the output of previous processing of this argument list.

        '''
        return None

    def arg(self, key_or_value, value=None):
        """An argument, as in a macro call. Arguments can be in two formats, either a plain
        expression or a key-value pair (separated by ':')

        """
        return None

    def assignment(self, target, expr, op, default):   # pylint: disable=C0103
        """An assignment, either through the equal operator (=) or one of the various
        operate-and-assign operators (e.g. +=).

        `target` is the LHS of the assignment (assigned to)
        `expr` is the RHS of the assignement (assigned from)
        `op` is the actual operator used
        `default` is :py:attr:`True` of the 'default' keyword was used.

        """
        return None

    def method_call(self, expr, arg_list=None):
        """A method call. `expr` should resolve to method, `arg_list`, if present, is the result
        of an argument list production."""
        return None

    def array_literal(self, elements=None):
        """An array literal, like [1, 2, 3] or [1:2, 3:4, 5:6]. `elements`, if present, is the
        result of the expansion of the elements inside the [].

        """
        return None

    def array_elems(self, expr, array_elems=None):
        """Elements for a simple array (not key/value pairs)."""
        return None

    def key_value_elems(self, key_expr, value_expr, prior_args=None):
        """Elements for an object-type array, with key/value pairs. `prior_args`, if present, is
        the result of reduction of previous elements in the array expression.

        """
        return None

    def array_ref(self, array_id, array_index):
        """An array reference to array `array_id` with index the value of `array_index`. Either
        param may be an expression rather than a simple value."""
        return None

    def if_stmt(self, expr, statement_list, elseif_stmts=None, else_stmt=None):
        """An if statement.

        :param expr: the test expression. `statement_list` is executed only if this resolves to
            :py:attr:`True`.

        :param statement_list: The statements to execute if the test is true.

        :param elseif_stmts: 0 to many elseif statements giving alternate conditions.

        :param else_stmt: The statements to execute if all tests return :py:attr:`False`.

        """
        return None

    def elseif_stmts(self, elseif_stmt, elseif_stmts=None):
        """A production for elseif statements (can also be written 'else if')"""
        return None

    def elseif_stmt(self, expr, statement_list):
        """An elseif clause, with a `statement_list` to be executed if `expr` is
        :py:attr:`True`.

        """
        return None

    def else_stmt(self, statement_list):
        """An else clause."""
        return None

    def return_stmt(self, expr):
        """A return statement. If `expr` is not :py:attr:`None`, it is the return value."""
        return None

    def macro_defn(self, macro_decl, statement_list):
        """A macro definition with declaration `macro_decl` containing statements
        `statement_list`. `statement_list` can also be :py:attr:`None`, indicating an empty
        macro (which is legal but useless).

        """
        return None

    def macro_decl(self, macro_name, param_list=None):
        """A macro definition. `macro_name` is the name of the macro, `param_list` is the list
        of formal parameters, or :py:attr:`None`.

        """
        return None

    def dotted_id(self, this_id, id_prefix=None):
        """An id made of a name, or two or more names separated by dots.

        `id_prefix` will be :py:attr:`None`, if the name is undotted or the first part of a dotted name."""
        return None

    def for_stmt(self, expr, as_clause, statement_list):
        """A for statement, which executes `statement_list` once for each item in the value of
        `expr` (assumed to be a collection). If `as_clause` has one or two children, the current
        item is assigned to a variable of that name (or the current key, value are assigned to
        variables of those names) for each loop.

        """
        return None

    def as_clause(self, var1, var2):
        """The AS clause of a FOR statement, providing one or two variable names to hold
        successive values from the collection being iterated.

        """
        return None

    def include_stmt(self, filename):
        """An include statement to insert the contents of file `filename`."""
        return None

    def abbrev_if_stmt(self, expr, statement):
        """A shortcut if statement, which executes the single statement `statement` if `expr`
        evaluates as true.

        """
        return None

    def while_stmt(self, expr, statement_list):
        """A while statement, where `expr` is the test and `statement_list` is the body."""
        return None

    def call_stmt(self, method_call):
        """A call statement, with the keyword call preceding a method call."""
        return None

    def error(self, p, the_parser):
        """Method called when a syntax error occurs. `p` is a production object with the state
        of the parser at the point where the error was detected.

        The default method raises UTLParseError with context information.
        """
        if p is None:
            raise UTLParseError("Syntax error at end of document! Symbol stack is {}".format(the_parser.symstack))
        else:
            the_lexer = p.lexer
            badline = the_lexer.lexdata.split('\n')[p.lineno-1]
            lineoffset = the_lexer.lexdata.rfind('\n', 0, the_lexer.lexpos)
            if lineoffset == -1:  # we're on first line
                lineoffset = 0
            lineoffset = the_lexer.lexpos - lineoffset
            raise UTLParseError("Syntax error in input line {}, column {} after '{}'!"
                                "".format(p.lineno, lineoffset, p.value))
