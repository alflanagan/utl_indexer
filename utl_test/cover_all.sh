#!/usr/bin/env dash

# modules that don't have test suites (yet):
# handler_parse_tree handler_print_productions handler_null

for MODULE in utl_parse_test ast_node utl_lex utl_yacc handler_ast macro_xref tn_package
do
  echo "************************************** ${MODULE} **************************************"
  ./cover_test.sh ${MODULE}
done
