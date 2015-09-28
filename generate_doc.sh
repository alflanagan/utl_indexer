#!/usr/bin/env dash
rm doc/api/*
sphinx-apidoc -T -o doc/api utl_lib
sphinx-apidoc -T -o doc/api utl_test
cd doc
make clean
make html
