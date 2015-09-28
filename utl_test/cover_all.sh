#!/usr/bin/env dash

for MODULE in utl_parse_test ast_node utl_lex utl_yacc handler_ast macro_xref
do
  echo "************************************** ${MODULE} **************************************"
  ./cover_test.sh ${MODULE}
done
