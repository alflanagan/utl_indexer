A Grammar for UTL
=================

The following is a summary of a grammar for the UTL template language,
reverse-engineered from a combination of the
`Townnews documentation <http://docs.townnews.com/kbpublisher/155/>`_
and examination of working code.

Operator Precedence
-------------------

Operator precedence isn't documented well. I started with the precedence for `PHP <https://secure.php.net/manual/en/language.operators.precedence.php>`_ and modified it until it parsed actual expressions correctly.

==================== ==================================
operator             associativity
==================== ==================================
.                    right
) ]                  left
( [                  right
*unary* -            right
,                    left
\|                   left
\... :               none
!                    right
\* / %               left
\+ -                 left
< > <= >=            none
is not eq neq == !=  none
=                    right
+= -= \*= /= %=      none
&&                   left
and                  left
||                   left
or                   left
==================== ==================================

Associativity:

* right: a **op** b **op** c ==> a **op** (b **op** c)
* left: a **op** b **op** c ==> (a **op** b) **op** c
* none: a **op** b **op** c is not valid

unary operators are "right" since (**op** **op**) a is not valid.

Grammar Productions
-------------------

The notation used below is BNF, with the following additions:

* [ *term* ] indicates that *term* is optional.

* characters in double quotes "like this" are literal strings.

* */regex/* indicates a regular expression, and characters within the '/'s have the usual meaning for a regular expression.

.. productionlist::
   utldoc : [ DOCUMENT ] [ "[%" statement_list ]
   statement_list : [ statement [ statement_list ]]
   statement : eostmt
             : echo_stmt eostmt
             : for_stmt eostmt
             : abbrev_if_stmt
             : if_stmt eostmt
             : "%]" DOCUMENT "[%"
             : "%]" DOCUMENT EOF
             : expr eostmt
             : default_assignment eostmt
             : return_stmt eostmt
             : include_stmt eostmt
             : call_stmt eostmt
             : macro_defn eostmt
             : while_stmt eostmt
             : "break" eostmt
             : "continue" eostmt
             : "exit" eostmt
   abbrev_if_stmt : "if" expr "then" statement
   arg : [ string|id ":" ] expr
   arg_list : [ arg [ "," arg_list ]]
   array_elems : expr "," array_elems
               : expr
   array_literal : "[" array_elems "]"
   array_ref : expr "[" expr "]"
   as_clause : [ "as" id [ "," id ]]
   call_stmt : "call" macro_call
   default_assignment : "default" expr
   dotted_id : id [ id "." dotted_id ]
   echo_stmt : [ "echo" ] expr
   else_stmt : [ "else" statement_list ]
   elseif_stmts : [ elseif_stmt [ elseif_stmts ]]
   elseif_stmt : "else" "if" expr statement_list
               : "elseif" expr statement_list
   eostmt : ";"
          : EOF
          : "%]"
   unary-op : "not"
            : "!"
            : "+"
            : "-"
   binary-op : "+"
             : "-"
             : "*"
             : "/"
             : "%"
             : "|"
             : "||"
             : ".."
             : "!="
             : "<="
             : "or"
             : "<"
             : "=="
             : "is"
             : ">"
             : "and"
             : ">="
             : "&&"
             : "."
             : "="
             : ":"
   assign-op : "+="
             : "-="
             : "\*="
             : "/="
             : "%="
   expr : unary-op expr
        : expr binary-op expr
        : expr assign-op expr
        : literal
        : id
        : array_ref
        : macro_call
        : paren_expr
   for_stmt : "for" [ "each" ] expr as_clause eostmt statement_list "end"
   if_stmt : "if" expr eostmt statement_list elseif_stmts else_stmt "end"
   include_stmt : "include" expr
   literal : string_literal
           : number_literal
           : array_literal
           : "false"
           : "true"
           : "null"
   macro_call : expr "(" arg_list ")"
   macro_decl : "macro" dotted_id [ "(" param_list ")" ]
   macro_defn : macro_decl eostmt statement_list "end"
   number_literal : /[0-9]+(.[0-9]+)?/
   param_decl : id [ "=" expr ]
   param_list : param_decl [ "," param_list ]
   paren_expr : "(" expr ")"
   return_stmt : "return" [ expr ]
   string_literal : /"((\"|[^"])*)"|'((\'|[^'])*)'/
   while_stmt : "while" expr statement_list "end"
   id : /[a-zA-Z_][a-zA-Z_0-9]*/

*DOCUMENT* is the longest sequence of characters that does not contain the string "[%"

Notes On The Grammar
++++++++++++++++++++

* ``else if`` is parsed the same as the word ``elseif``. This means
  this is correct:

.. code-block:: php

    if a == b;
      do_something;
    else if c == d;
      do_something_else;
    end;

and **not**:

.. code-block:: php

    if a==b;
      do_something;
    else
      if c == d;
        do_something_else;
      end;
    end;

But, if you put a semicolon between the ``else`` and the ``if``, it
will act as two separate ``if`` statements, and require the extra
``end``.

* The regex for *string\_literal* is rather confusing. It just means "a
  string literal is a sequence of characters enclosed by either single
  or double quotes. Quotes *of the same kind* within the string must
  be escaped with a backslash."

    * But, if you do escape it with a backslash, the backslash is kept in
      the final string: ``echo "he said, \"hello\"";``
      is legal, but the output is ``he said \"hello\"``.
