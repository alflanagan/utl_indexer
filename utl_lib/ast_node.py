#!/usr/bin/env python3


class ASTNode(object):
    """A node in the AST tree.

    :param str symbol_name: A name for the node, usually related to the rule that produced it.

    :param Boolean is_term: :py:attr:`True` if this is a terminal node (never has children).

    :param dict attrs: key-value pairs attaching arbitrary attributes to this node. For
        attributes that are not common to all nodes.

    :param list children: iterator of nodes, which will be attached as children.

    """

    def __init__(self, symbol_name, is_term, attrs=None, children=None):
        self.children = [] if children is None else children
        self.parent = None  # set by parent in add_child
        self.symbol = symbol_name
        self.terminal = is_term
        self.attributes = {} if attrs is None else attrs

    def add_child(self, child):
        # we might have passed a generator to __init__(), or even a set
        self.children = list(self.children)
        child.parent = self
        # because we're an LR parser, we see "first" child last
        self.children.insert(0, child)

    def add_children(self, iterator):
        # we might have passed a generator to __init__(), or even a set
        self.children = list(self.children)
        for child in iterator:
            if child:
                self.add_child(child)

    def __str__(self):
        result = 'Node({})'.format(self.symbol)
        if self.attributes:
            attrs = ''
            for key in self.attributes:
                if attrs:
                    attrs += ', {}: "{}"'.format(key, repr(self.attributes[key]))
                else:
                    attrs = '{}: "{}"'.format(key, repr(self.attributes[key]))
            result += " {%s}" % attrs
        return result

    def __repr__(self):
        child_list = ""
        for child in self.children:
            if child_list:
                child_list += ", {}".format(child.symbol)
            else:
                child_list = child.symbol
        return'ASTNode("{}", {}, ..., [{}])'.format(self.symbol,
                                                    "True" if self.terminal else "False",
                                                    child_list)


class ASTNodeFormatter(object):

    def __init__(self, root_node):
        self.root = root_node

    def format(self, from_node=None):
        if from_node is None:
            from_node = self.root
        result = str(from_node)
        for child in from_node.children:
            lines = self.format(child).split('\n') if child else ['**error**']
            for line in lines:
                result += '\n    ' + line
        return result
