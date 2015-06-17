#!/usr/bin/env python3
"""Module of classes used to implement an Abstract Syntax Tree structure."""


class ASTNodeError(Exception):
    '''Exceptions raised by misuse of an ASTNode object.'''
    pass


class ASTNode(object):
    """A node in the AST tree.

    :param str symbol_name: A name for the node, usually related to the rule that produced it.

    :param Boolean is_term: :py:attr:`True` if this is a terminal node (never has children).

    :param dict attrs: key-value pairs attaching arbitrary attributes to this node. For
        attributes that are not common to all nodes.

    :param list children: iterator of nodes, which will be attached as children.

    """

    def __init__(self, symbol_name, is_term, attrs=None, children=None):
        if not symbol_name:
            raise ASTNodeError('ASTNode must have a valid name')
        self.children = []
        if children:
            for child in children:
                self.add_child(child)
        self.parent = None  # set by parent in add_child
        self.symbol = symbol_name
        self.terminal = is_term
        self.attributes = {} if attrs is None else attrs

    def __eq__(self, other):
        '''Deep equality test, useful for testing.'''
        if not isinstance(other, ASTNode):
            return False
        if (self.symbol != other.symbol
                or self.terminal != other.terminal
                or set(self.attributes.keys()) != set(other.attributes.keys())):
            return False
        for key in self.attributes:
            if self.attributes[key] != other.attributes[key]:
                return False
        if len(self.children) != len(other.children):
            return False
        for i in range(len(self.children)):
            if self.children[i] != other.children[i]:
                return False
        return True

    def add_child(self, child):
        '''Add child to the list of children of this node. `child` will become the last child,
        making this appropriate for right-expanding rules like: a : a b

        Note: If child has no parent node, it is added directly to our children. If child
        already has a parent node, a copy is made, then added. This prevents cases where a node
        would have a child whose parent is not that node.

        :param ASTNode child: A child node.

        :raises ASTNodeError: if child is not an ASTNode
        '''
        if not isinstance(child, ASTNode):
            raise ASTNodeError('Invalid child for AST Node: {}'.format(child))
        # we might have passed a generator to __init__(), or even a set
        self.children = list(self.children)
        if child.parent:
            child = child.copy()
        child.parent = self
        self.children.append(child)

    def copy(self):
        """Returns a new instance of :py:class:`utl_lib.ast_node.ASTNode` whose attributes have
        the same values as this.
        """
        return ASTNode(self.symbol, self.terminal, self.attributes.copy(),
                       [kid.copy() for kid in self.children])

    def add_first_child(self, child):
        '''Add child to the list of children of this node. `child` will become the first child,
        making this appropriate for left-expanding rules like: a : b a

        :param ASTNode child: A child node.
        '''
        # we might have passed a generator to __init__(), or even a set
        self.children = list(self.children)
        child.parent = self
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
                    attrs += ', {}: {}'.format(key, repr(self.attributes[key]))
                else:
                    attrs = '{}: {}'.format(key, repr(self.attributes[key]))
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
