#!/usr/bin/env dash
APIDOC_FLAGS="-T -e -o doc/api"

rm doc/api/*
sphinx-apidoc ${APIDOC_FLAGS} utl_lib
sphinx-apidoc ${APIDOC_FLAGS} utl_test
cd doc
make clean
make html
