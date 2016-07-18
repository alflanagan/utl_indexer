<style type="text/css">
table {
  border-collapse: collapse;
}

thead tr td {
  border-width: 2px;
  border-style: solid;
  border-color: darkblue;
  padding: 5px;
  }

tbody tr td {
    border-width: 1px;
    border-style: solid;
    border-color: darkblue;
    padding: 6px;
    }

pre {
  font-size: 120%;
  margin-left: 3em;
  margin-right: 3em;
  font-weight: 600;
  background: #F5F5F5;
}

.code {
  font-family: monospace;
  font-weight: 600;
  background: #F5F5F5;
  padding-right: 3px;
  padding-left: 3px;
}

</style>
# A Grammar for UTL

The following is a summary of a grammar for the UTL template language,
reverse-engineered from a combination of the
[Townnews documentation](http://docs.townnews.com/kbpublisher/155/)
and examination of working code.

## operator precedence

Operator precedence isn't documented well. I started with the precedence for [PHP](https://secure.php.net/manual/en/language.operators.precedence.php) and modified it until it parsed actual expressions correctly.

<table>
<thead>
<tr><td>operator</td><td>associativity</td></tr>
</thead>
<tbody>
<tr><td> .      </td><td> right </td></tr>
<tr><td> ) ]    </td><td> left  </td></tr>
<tr><td> ( [    </td><td> right </td></tr>
<tr><td> unary -</td><td> right </td></tr>
<tr><td> ,      </td><td> left  </td></tr>
<tr><td> |      </td><td> left  </td></tr>
<tr><td> ... :  </td><td> none  </td></tr>
<tr><td> !      </td><td> right </td><tr>
<tr><td> * / %  </td><td> left  </td></tr>
<tr><td> + -    </td><td> left  </td></tr>
<tr><td> < > <= >= </td><td> none  </td></tr>
<tr><td> is not eq neq </td><td> none  </td></tr>
<tr><td> =      </td><td> right </td></tr>
<tr><td> += -= *= /= %= </td><td> none  </td></tr>
<tr><td> &&     </td><td> left  </td></tr>
<tr><td> and    </td><td> left  </td></tr>
<tr><td> ||     </td><td> left  </td></tr>
<tr><td> or     </td><td> left  </td></tr>
</tbody>
</table>


Associativity:
* right: a op b op c ==> a op (b op c)
* left: a op b op c ==> (a op b) op c
* none: a op b op c is not valid

unary operators are "right" since (op op) a is not valid.

## Grammar Productions

The notation used below is BNF, with the following additions:

* _[ term ]_ indicates that _term_ is optional.

* _'['_ and _']'_ are used to indicate the actual characters without that special meaning.

* _'|'_ and _'||'_ indicate one or two vertical bar characters, respectively.

* */*_regex_*/* indicates a regular expression, and characters within the '/'s have the usual meaning for a regular expression.

```
<utldoc> ::= [ <DOCUMENT> ] [ '[%' <statement_list> ]

<statement_list> ::= [ <statement> [ <statement_list> ]]

<statement> ::= <eostmt>
          | <echo_stmt> <eostmt>
          | <for_stmt> <eostmt>
          | <abbrev_if_stmt>
          | <if_stmt> <eostmt>
          | '%]' <DOCUMENT> '[%'
          | '%]' <DOCUMENT> EOF
          | <expr> <eostmt>
          | <default_assignment> <eostmt>
          | <return_stmt> <eostmt>
          | <include_stmt> <eostmt>
          | <call_stmt> <eostmt>
          | <macro_defn> <eostmt>
          | <while_stmt> <eostmt>
          | break <eostmt>
          | continue <eostmt>
          | exit <eostmt>

<abbrev_if_stmt> ::= if <expr> then <statement>

<arg> ::= [ <string>|<id> : ] <expr>

<arg_list> ::= [ <arg> [ , <arg_list> ]]

<array_elems> ::= <expr> [ , <array_elems> ]

<array_literal> ::= '[' [ <array_elems> [,] ']'

<array_ref> ::= <expr> '[' <expr> ']'

<as_clause> ::= [ as <id> [ , <id> ]]

<call_stmt> ::= call <macro_call>

<default_assignment> ::= default <expr>

<dotted_id> ::= <id> [ <id> . <dotted_id> ]

<echo_stmt> ::= [ echo [ <expr> ]]

<else_stmt> ::= [ else <statement_list> ]

<elseif_stmts> ::= [ <elseif_stmt> [ <elseif_stmts> ]]

<elseif_stmt> ::= else[ ]if <expr> <statement_list>

<eostmt> ::= ; | EOF | %']'

<unary-op> ::= not | ! | + | -

<binary-op> ::= + | - | * | / | % | '|' | '||' | .. | != | <= | or | < 
     | == | is | > | and | >= | && | . | = | :

<assign-op> ::= += | -= | *= | /= | %=

<expr> ::= <unary-op> <expr> | <expr> <binary-op> <expr> | <expr> <assign-op> <expr>
     | <literal> | <id> | <array_ref> | <macro_call> | <paren_expr>

<for_stmt> ::= for [ each ] <expr> <as_clause> <eostmt> <statement_list> end

<if_stmt> ::= if <expr> <eostmt> <statement_list> <elseif_stmts> <else_stmt> end

<include_stmt> ::= include <expr>

<literal> ::= <string_literal> | <number_literal> | <array_literal> | false | true | null

<macro_call> ::= <expr> ( <arg_list> )

<macro_decl> ::= macro <dotted_id> [ ( <param_list> ) ]

<macro_defn> ::= <macro_decl> <eostmt> <statement_list> end

<number_literal> ::= /[0-9]+(.[0-9]+)?/

<param_decl> ::= <id> [ = <expr> ]

<param_list> ::= <param_decl> [ , <param_list> ]

<paren_expr> ::= ( <expr> )

<return_stmt> ::= return [ <expr> ]

<string_literal> ::= /"((\\"|[^"])*)"|\'((\\\'|[^\'])*)\'/

<while_stmt> ::= while <expr> <statement_list> end

<id> ::= /[a-zA-Z_][a-zA-Z_0-9]*/

<DOCUMENT> is the longest sequence of characters that does not contain the string "[%"

```

### Notes On The Grammar

* <span class="code">else if</span> is parsed the same as the word
  <span class="code">elseif</span>. This means this is correct:

<pre>
if a == b;
  do_something;
else if c == d;
  do_something_else;
end;
</pre>

<p style="margin-left: 2.5em;" >and <em>not</em>:</p>

<pre>
if a==b;
  do_something;
else 
  if c == d;
    do_something_else;
  end;
end;
</pre>

<p style="margin-left: 2.5em;" >But, if you put a semicolon between the <span class="code">else</span> and the <span class="code">if</span>, it will act as two separate <span class="code">if</span> statements, and require the extra <span class="code">end</span>.</p>

* The regex for <string\_literal> is rather confusing. It just means "a
  string literal is a sequence of characters enclosed by either single
  or double quotes. Quotes _of the same kind_ within the string must
  be escaped with a backslash."

    * But, if you do escape it with a backslash, the backslash is kept in 
      the final string: <span class="code">echo "he said, \\"hello\\"";</span>
      is legal, but the output is <span class="code">he said \\"hello\\"</span>.
