#!/usr/bin/env python3


class ASTNode(object):
    """A node in the AST tree. """

    def __init__(self, symbol_name):
        self.children = []
        self.symbol = symbol_name
        self.terminal = True

    def add_child(self, a_child):
        self.children.append(a_child)

    def add_children(self, iterator):
        self.children.extend(iterator)
