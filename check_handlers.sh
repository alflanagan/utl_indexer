#!/usr/bin/env dash

TMP1=$(mktemp)
TMP2=$(mktemp)

echo "---------------------------------------------------------------"
grep 'def ' utl_lib/utl_parse_handler.py | cut -d'(' -f1 | sed -e s'/    def //' | grep -v -e __init__ | sort -u > ${TMP1}

grep 'def p_' utl_lib/utl_yacc.py | cut -d'(' -f1 | sed -e s'/    def p_//' | sort -u > ${TMP2}

echo "< is from utl_parse_handler.py, > is from utl_yacc.py"
diff ${TMP1} ${TMP2} | grep '^[<>]'

rm ${TMP1} ${TMP2}

if [ ! -z $1 ]; then
    if [ ! -r $1 ]; then
        echo $1 not found >&2
        exit 1
    fi

    echo "---------------------------------------------------------------"
    grep 'def ' utl_lib/utl_parse_handler.py | cut -d'(' -f1 | sed -e s'/    def //' | grep -v -e __init__ -e error | sort -u > ${TMP1}

    grep 'def ' $1 | cut -d'(' -f1 | sed -e s'/    def //' | grep -v __init__ | sort -u > ${TMP2}

    echo "< is from utl_parse_handler.py, > is from $1"
    diff ${TMP1} ${TMP2} | grep '^[<>]'

    rm ${TMP1} ${TMP2}
fi
