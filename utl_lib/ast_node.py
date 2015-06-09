#!/usr/bin/env python3


class ASTNode(object):
    """A node in the AST tree. """

    def __init__(self, symbol_name):
        self.children = []
        self.symbol = symbol_name
        self.terminal = True
        self.attributes = {}

    def add_child(self, a_child):
        self.children.append(a_child)

    def add_children(self, iterator):
        self.children.extend(iterator)

    def __str__(self):
        result = 'Node({})'.format(self.symbol)
        if self.attributes:
            attrs = ''
            for key in self.attributes:
                if attrs:
                    attrs += ', {}: "{}"'.format(key, self.attributes[key])
                else:
                    attrs = '{}: "{}"'.format(key, self.attributes[key])
            result += " [{}]".format(attrs)

        for child in self.children:
            result += ' -> {}'.format(child)
        return result
