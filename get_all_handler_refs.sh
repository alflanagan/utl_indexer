#!/usr/bin/env dash

TMP1=$(mktemp)
TMP2=$(mktemp)

grep handler utl_lib/utl_yacc.py | grep -v self.handler | grep 'handler.[a-z_]\+(' | cut -d'(' -f1 | sed -e 's/^\s\+//' | grep -v 'handler.error' | sed -e 's/value = handler.//' | sort -u > ${TMP1}

grep 'def ' utl_lib/utl_parse_handler.py | cut -d'(' -f1 | sed -e s'/    def //' | grep -v -e __init__ -e error | sort -u > ${TMP2}

echo "< is from utl_yacc, > is from utl_parse_handler"
diff ${TMP1} ${TMP2}

rm ${TMP1} ${TMP2}
