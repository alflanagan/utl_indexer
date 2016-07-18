#!/usr/bin/env dash
# check all exported UTL files for errors
find /mnt/extra/Devel/utl_indexer/data/exported/ -name '*.utl' | xargs --max-args=50 ./parse_file.py > /dev/null 2> test_parse_file.out &
