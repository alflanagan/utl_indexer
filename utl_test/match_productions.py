#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""Given the output of UTL file parse, and the UTL file, attempts to match the productions to
the UTL text. Makes visual debugging/verification easier.

"""

import json


def walk_dicts(top_node, action, extra_data):
    """Calls action with params top_node and extra data, then does walk_dict() for each dict in
    'children' list.

    """
    action(top_node, extra_data)
    # empty "children" lists get dropped from JSON
    if "children" in top_node:
        for node in top_node['children']:
            walk_dicts(node, action, extra_data)


def print_name(node, _):
    """Simple action to just print 'name' field."""
    print(node["name"])

def print_text(node, data):
    print(node["name"], end='')
    attrs = node["attributes"] if "attributes" in node else {}
    if node["name"] == 'expr' and "operator" in node["attributes"]:
        print('[{}] '.format(node["attributes"]["operator"]), end='')
    print(":  ", end='')
    if "start" in attrs and "end" in attrs:
        print(data['text'][attrs["start"]:attrs["end"]])
    else:
        print()

def match_prods(utl_file, json_file):
    """Reads the JSON and UTL files, pulls parts of utl_file according to values in JSON file."""
    with open(json_file, 'r') as jin:
        productions = json.load(jin)

    with open(utl_file, 'r') as utlin:
        utl_text = utlin.read()

    if productions["name"] == "utldoc":
        productions = productions["children"][0]
    assert productions["name"] == "statement_list"
    # # don't want to print out whole statement_list, so cheat
    # productions["attributes"]["start"] = 0
    # productions["attributes"]["end"] = 0

    walk_dicts(productions, print_text, {"text": utl_text})

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        sys.stderr.write("Expecting two file names, a UTL file, then a JSON file.\n")
        sys.exit(1)

    match_prods(sys.argv[1], sys.argv[2])
