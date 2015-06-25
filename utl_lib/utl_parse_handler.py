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

    def utldoc(self, child):
        '''The top-level node for a UTL document. `child` could be a DOCUMENT but is normally a
        statement_list.

        '''
        return None

    def statement_list(self, statement, statement_list=None):
        '''A statement_list production. `statement_list`, if not :py:attr:`None`, is the
        statement list seen so far; `statement` is the result of the current statement parse.

        '''
        return None

    def statement(self, child_or_text, is_document=False):
        """A single statement, usually terminated with a ';' or a '%]'.

        If `is_document` is :py:attr:`True`, then `child_or_text` is the contents of a DOCUMENT.

        Otherwise, `child_or_text` will be the text of a token, or the result of a production.

        Tokens that may be provided include 'continue', 'break', and 'exit'.

        """
        # NOTE: above not satisfactory from library user's perspective. FIXME
        return None

    def end_stmt(self, marker_text):
        """End statement marker. Unlikely to be useful, but if you need it, it's here."""
        return None

    def echo_stmt(self, expr):
        """An echo statement. `expr` is the object to be echoed, or :py:attr:`None`."""
        return None

    def expr(self, expr, term, op):  # pylint: disable=C0103
        """Any of various types of expression. Parameters may be present, or None, based on the expression type.

        :param expr: result of another expr or method_call production.

        :param term: The right-hand side of some productions

        :param op: The operator, for those which don't generate a specialized production.

        """
        return None

    def param_list(self, param_decl, param_list):
        '''A list of parameters for a macro definition.

        :param param_decl: A parameter declaration.

        :param param_list: The parameter list of which `param_decl` is a part, if this is not
            the first production in the list.

        '''
        return None

    def param_decl(self, param_id, param_assign):
        """A parameter declaration. One parameter should have a value, the other should be
        :py:attr:`None`.

        :param str param_id: The parameter name.

        :param param_assign: The result of an assignment production, representing a parameter
        with a default value.

        """
        return None

    def arg_list(self, arg, arg_list):
        '''An argument list, as in a macro call. `arg` is an argument (see :py:meth:`arg`).
        `arg_list`, if not None, is the output of previous processing of this argument list.

        '''
        return None

    def arg(self, argument_or_key, value):
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

    def method_call(self, method_name, arglist):
        """A method call. `arglist` (the list of arguments) is optional."""
        return None

    def full_id(self, this_id, suffix):
        """An ID, possibly part of a dotted ID. `suffix`, if present, is the part of the ID
        which came before the current value (or after it in the original source code.).

        Input of 'cms.this.block' would thus trigger:
            full_id('block')
            full_id('this', ASTNode('id', {'symbol': 'block'}))
            full_id('cms', ASTNode('id', {'symbol': 'this.block'})

        """
        return None

    def term(self, factor, op, term):   # pylint: disable=C0103
        """A term from an expression, with operator '*', '/', '%', or just a factor.

        :param factor: a result from a :py:meth:`factor` production.

        :param str op: The operator, if applicable.

        :param term: The output from any part of the term already processed.

        """
        return None

    def factor(self, node, keyword, paren_expr):
        """Any one of several 'atomic' elements in an expr. Generally only one of the parameters
        will have a value, depending on which production was followed.

        :param node: if present, the result of a sub-production like literal or full_id.

        :param str keyword: a keyword ('false', 'true', 'null') or :py:attr:`None`

        :param paren_expr: the result of an expr production, which was enclosed by parentheses.

        """
        return None

    def literal(self, value):
        """A literal number or string occurring in the source, like '3.0' or 'fred'. Use
        ``isinstance(value, str)`` to determine type if that is relevant to your app.

        """
        return None

    def array_ref(self, name, expr):
        """An array reference to array `name` with index the value of `expr`."""
        return None

    def if_stmt(self, expr, statement_list, elseif_stmts, else_stmt):
        """An if statement. `expr` and `statment_list` are required.

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
        macro (which is legal).

        """
        return None

    def macro_decl(self, macro_id, param_list):
        """A macro definition. `macro_id` is the name of the macro, `param_list` is the list of
        formal parameters, or :py:attr:`None`.

        """
        return None

    def for_stmt(self, expr, for_var, statement_list):
        """A for statement, which executes `statement_list` once for each item in the value of
        `expr` (assumed to be a collection). If for_var is not :py:attr:`None`, the current item
        is assigned to a variable of that name for each loop.

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
