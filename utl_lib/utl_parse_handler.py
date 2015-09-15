#!/usr/bin/env python3
"""A base class to handle parsing operations for a UTL file."""
import sys


# problem with throwing exception on errors is that it halts parsing process
# no good way to resume (?) So error handling is coupled to parser, not user
# of parser
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

    def error(self, p, the_parser):
        """Method called when a syntax error occurs. `p` is a production object with the state
        of the parser at the point where the error was detected.

        The default method raises UTLParseError with context information.
        """
        if p is None:
            if self.exception_on_error:
                raise UTLParseError("Syntax error at end of document! Symbol stack is {}"
                                    "".format(the_parser.symstack))
            else:
                sys.stderr.write("Syntax error at end of document! Symbol stack is {}\n"
                                 "".format(the_parser.symstack))
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
    def utldoc(self, statement_list):
        '''The top-level node for a UTL document.'''
        return None

    def statement_list(self, statement=None, statement_list=None):
        '''A statement_list production. `statement_list`, if not :py:attr:`None`, is the
        statement list seen so far; `statement` is the result of the current statement parse.

        '''
        return None

    def statement(self, statement):
        """A single statement, usually terminated with a ';' or a '%]'.

        `statement` will be the text of a token, or the result of a production.

        Tokens that may be provided include 'continue', 'break', and 'exit'.

        """
        return None

    # -------------------------------------------------------------------------------------------
    # regular productions
    # -------------------------------------------------------------------------------------------
    def abbrev_if_stmt(self, expr, statement):
        """A shortcut if statement, which executes the single statement `statement` if `expr`
        evaluates as true.

        """
        return None

    def arg(self, expr, name=None):
        """An argument, as in a macro call. Arguments can be in two formats, either a plain
        expression or a key-value pair (separated by ':')

        :param expr: the result of an expression production for the argument

        :param name: the name if the argument is named.

        """
        return None

    def arg_list(self, arg, arg_list=None):
        '''An argument list, as in a macro call. `arg` is an argument (see :py:meth:`arg`), or
        None for a call with no arguments.

        `arg_list`, if not None, is the output of previous processing of this argument list.

        '''
        return None

    def array_elems(self, expr, array_elems=None):
        """Elements for a simple array (not key/value pairs).

        :param expr: An expression production for the current element value.

        :param array_elems: The result of a previous array_elems production for this array.

        """
        return None

    def array_literal(self, elements=None):
        """An array literal, like [1, 2, 3] or [1:2, 3:4, 5:6]. `elements`, if present, is the
        result of the expansion of the elements inside the [].

        """
        return None

    def array_ref(self, variable, index):
        """An array reference of the form variable[index]."""
        return None

    def as_clause(self, var1, var2=None):
        """The AS clause of a FOR statement, providing one or two variable names to hold
        successive values from the collection being iterated.

        """
        return None

    def call_stmt(self, macro_call):
        """A call statement, with the keyword call preceding a method call.

        :param macro_call: An expression production, which should resolve to a macro call.

        """
        return None

    def default_assignment(self, assignment):
        """Assignment with a preceding DEFAULT keyword.

        :param assignment: The result of an assignment production (as expression).

        """
        return None

    def dotted_id(self, this_id, id_suffix=None):
        """An id made of a name, or two or more names separated by dots.

        `id_suffix` will be :py:attr:`None`, if `this_id` is the first part of the id, or the
        result of productions of the parts of the id previous to `this_id`.

        """
        return None

    def echo_stmt(self, expr):
        """An echo statement. `expr` is the object to be echoed, or :py:attr:`None`."""
        return None

    def else_stmt(self, statement_list):
        """An else clause."""
        return None

    def elseif_stmts(self, elseif_stmt, elseif_stmts=None):
        """A production for elseif statements (can also be written 'else if')"""
        return None

    def elseif_stmt(self, expr, statement_list):
        """An elseif clause, with a `statement_list` to be executed if `expr` is
        :py:attr:`True`.

        """
        return None

    def eostmt(self, marker_text):
        """End statement marker. Unlikely to be useful, but if you need it, it's here."""
        return None

    def expr(self, first, second=None, third=None):
        """An expression production.
        first is: not|!|expr|literal|ID|LBRACKET|LPAREN|array_ref
        second is: expr|PLUS|MINUS|TIMES|DIV|MODULUS|FILTER|DOUBLEBAR|RANGE|NEQ|LTE|OR|LT|EQ|IS|
                   GT|AND|GTE|DOUBLEAMP|DOT|ASSIGN|ASSIGNOP|COMMA|COLON
        third is: expr|RBRACKET|RPAREN
        """
        return None

    def for_stmt(self, expr, as_clause=None, statement_list=None):
        """A for statement, which executes `statement_list` once for each item in the value of
        `expr` (assumed to be a collection). If `as_clause` has one or two children, the current
        item is assigned to a variable of that name (or the current key, value are assigned to
        variables of those names) for each loop.

        """
        return None

    def if_stmt(self, expr, statement_list=None, elseif_stmts=None, else_stmt=None):
        """An if statement.

        :param expr: the test expression. `statement_list` is executed only if this resolves to
            :py:attr:`True`.

        :param statement_list: The statements to execute if the test is true.

        :param elseif_stmts: 0 to many elseif statements giving alternate conditions.

        :param else_stmt: The statements to execute if all tests return :py:attr:`False`.

        """
        return None

    def include_stmt(self, filename):
        """An include statement to insert the contents of file `filename`.

        :param filename: The result of an expression production, which may or may not be a
            simple string.

        """
        return None

    def literal(self, literal):
        """A literal value: either a string, a number, or an array literal."""
        return None

    def macro_call(self, macro_expr, arg_list=None):
        """A macro procedure call.

        :param ASTNode macro_expr: An expression, either an ID with the macro name or some
            expression that resolves to a macro reference.

        :param ASTNode arg_list: The list of arguments, if any.

        """
        return None

    def macro_decl(self, macro_name, param_list=None):
        """A macro definition. `macro_name` is the name of the macro, `param_list` is the list
        of formal parameters, or :py:attr:`None`.

        """
        return None

    def macro_defn(self, macro_decl, statement_list=None):
        """A macro definition with declaration `macro_decl` containing statements
        `statement_list`. `statement_list` can also be :py:attr:`None`, indicating an empty
        macro (which is legal but useless).

        """
        return None

    def param_decl(self, param_id, default_value=None):
        """A parameter declaration.

        :param str param_id: The parameter name.

        :param default_value: An expression giving the value to use for the parameter if it is
        omitted from the method call.

        """
        return None

    def param_list(self, param_decl, param_list=None):
        '''A list of parameters for a macro definition.

        :param param_decl: A parameter declaration.

        :param param_list: The parameter list of which `param_decl` is a part, if this is not
            the first production in the list.

        '''
        return None

    def paren_expr(self, expr):
        '''An expr enclosed in parentheses.'''
        return None

    def return_stmt(self, expr=None):
        """A return statement. If `expr` is not :py:attr:`None`, it is the return value."""
        return None

    def while_stmt(self, expr, statement_list):
        """A while statement, where `expr` is the test and `statement_list` is the body."""
        return None
