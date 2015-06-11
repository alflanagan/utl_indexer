#!/usr/bin/env python3
"""Module of classes used to implement an Abstract Syntax Tree structure."""


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
        '''Add child to the list of children of this node. `child` will become the first child,
        as the parser provides them in reverse order.

        :param ASTNode child: A child node.
        '''
        # we might have passed a generator to __init__(), or even a set
        self.children = list(self.children)
        child.parent = self
        # because we're an LR parser, we see "first" child last
        self.children.insert(0, child)

    def add_children(self, iterator):
        '''Add each item in iterator to the list of children. Items should be nodes. Note that
        the nodes will be inserted into the beginning of the list, and end up in reverse order
        of the iterator.

        :param list iterator: Iterator producing :py:class:`utl_lib.ast_node.ASTNode` objects.
        '''
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


class ASTNodeFormatter(object):  # pylint: disable=too-few-public-methods
    """Helper class that can traverse an AST and pretty-print it.

    :param ASTNode root_node: The root node of the tree to be printed. May be supplied to
        :py:meth:`~utl_lib.ast_node.ASTNodeFormatter.format` instead.
    """
    # TODO: abstract class for "classes that walk an AST"
    def __init__(self, root_node):
        self.root = root_node

    def format(self, from_node=None):
        """Walks the tree with root `from_node`, printing it out in a format which, if not
        pretty, is at least comprehensible. `from_node` defaults to the root node set at object
        init.

        :param ASTNode from_node: Root of an AST to be printed.
        """
        if from_node is None:
            from_node = self.root
        result = str(from_node)
        for child in from_node.children:
            lines = self.format(child).split('\n') if child else ['**error**']
            for line in lines:
                result += '\n    ' + line
        return result
