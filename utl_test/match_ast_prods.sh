#!/usr/bin/env dash

if [ $# -lt 1 ]; then
    echo "Required param: a UTL file name (sans extension)"
    exit 1
fi
../parse_file.py $1.utl --ast --json > $1_ast.json
./match_productions.py $1.utl $1_ast.json 
