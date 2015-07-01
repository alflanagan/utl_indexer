#!/usr/bin/env dash

TMP1=$(mktemp)
TMP2=$(mktemp)

grep 'def ' utl_lib/utl_parse_handler.py | cut -d'(' -f1 | sed -e s'/    def //' | grep -v -e __init__ -e error | sort -u > ${TMP1}

grep 'def ' $1  | cut -d'(' -f1 | sed -e s'/    def //' | grep -v -e __init__ -e error | sort -u > ${TMP2}

echo "< is from the parent, > is from $1"
diff ${TMP1} ${TMP2}

rm ${TMP1} ${TMP2}
