#!/usr/bin/env dash

if [ $# -lt 1 ]; then
  echo "Required argument: the name of a handler file."
  exit 1
fi

TMPFIL=$(mktemp)
TMPFIL2=$(mktemp)
TMPFIL3=$(mktemp)
trap "{ rm -f ${TMPFIL} ${TMPFIL2} ${TMPFIL3}; }" EXIT INT KILL

grep -v '^#' utl_lib/utl_yacc.py | grep -oh -e 'def p_[^(]*' | sed -e 's/def p_//' | sort > ${TMPFIL}
grep -v '^#' $1 | grep -oh -e 'def [^_][^(]*' | sed -e 's/def //' | sort > ${TMPFIL2}

diff ${TMPFIL} ${TMPFIL2} > ${TMPFIL3}

echo "methods in yacc not found in $1:"
grep '^<' ${TMPFIL3} | cut -c 2-
echo "\nmethods in $1 not found in yacc:"
grep '^>' ${TMPFIL3} | cut -c 2-
