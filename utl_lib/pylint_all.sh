#!/usr/bin/env dash

# specify file list -- several we don't want to scan
for FILE in ast_node.py handler_ast.py handler_parse_tree.py handler_print_productions.py \
            utl_lex.py utl_parse_handler.py utl_yacc.py
do
  echo ${FILE}
  pylint ${FILE}
done
