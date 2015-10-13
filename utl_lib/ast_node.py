#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module of classes used to implement an Abstract Syntax Tree structure. Actually, theyre used
to implement parse tree as well, name is historical accident.


| © 2015 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from utl_lib.utl_parse_handler import FrozenDict


class ASTNodeError(Exception):
    '''Exceptions raised by misuse of an ASTNode object.'''
    pass


class ASTNode(object):
    """A node in the AST.

    :param str symbol_name: A name for the node, usually related to the rule that produced it.

    :param dict attrs: key-value pairs attaching arbitrary attributes to this node. For
        attributes that are not common to all nodes.

    :param list children: iterator of nodes, which will be attached as children.

    """

    def __init__(self, symbol_name, attrs, children):
        if not symbol_name:
            raise ASTNodeError('ASTNode must have a valid name')
        if attrs is not None:
            assert hasattr(attrs, 'keys')
        self.children = []
        if children:
            for child in children:
                self.add_child(child)
        self.parent = None  # set by parent in add_child
        self.symbol = symbol_name
        self._attributes = None
        self.attributes = attrs

    @property
    def attributes(self):
        """A :py:class:`~utl_lib.utl_parse_handler.FrozenDict` containing arbitrary key-value
        pairs from the node's creator.

        """
        return self._attributes

    @attributes.setter
    def attributes(self, new_attrs):  # pylint: disable=C0111
        if new_attrs is None:
            self._attributes = FrozenDict()
        elif not isinstance(new_attrs, FrozenDict):
            self._attributes = FrozenDict(new_attrs)
        else:
            self._attributes = new_attrs

    def __eq__(self, other):
        '''Deep equality test, useful for testing.'''
        # note this is optimized for debugging, *not* performance
        # pylint: disable=W0212,R0911
        if self is other:  # optimization
            return True
        if not isinstance(other, ASTNode):
            return False
        if (self.symbol != other.symbol or
                set(self._attributes.keys()) != set(other._attributes.keys())):
            return False
        for key in self._attributes:
            if self._attributes[key] != other._attributes[key]:
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
        if child is self:
            raise ASTNodeError('A node cannot be a child of itself.')
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
        return ASTNode(self.symbol, self._attributes,
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
        """Add each item in iterator to the list of children. Items should be nodes. Note that
        the nodes will be inserted into the beginning of the list, and end up in reverse order
        of the iterator.

        :param list iterator: Iterator producing :py:class:`utl_lib.ast_node.ASTNode` objects.

        """
        # we might have passed a generator to __init__(), or even a set
        self.children = list(self.children)
        for child in iterator:
            if child:
                self.add_child(child)

    def __str__(self):
        result = '{}: '.format(self.symbol)
        if self.symbol == 'literal':
            value = self._attributes['value']
            if isinstance(value, ASTNode) and value.symbol == "array_literal":
                result = "literal (array):"
                for child in value.children:
                    result += " {}".format(child.symbol)
            else:
                result += repr(self._attributes['value'])
        elif self.symbol in ('operator', 'id'):
            result += self._attributes['symbol']
        elif self.symbol == 'unary-op':
            result += self._attributes['operator']
        elif self.symbol == 'document':
            result += repr(self._attributes['text'])
        elif self._attributes:
            attrs = ', '.join(["{}: {}".format(key, repr(value))
                               for key, value in self._attributes.items()])
            result += " {%s}" % attrs
        return result

    def __repr__(self):
        child_list = ""
        for child in self.children:
            if child_list:
                child_list += ", {}".format(child.symbol)
            else:
                child_list = child.symbol
        return 'ASTNode("{}", ..., [{}])'.format(self.symbol, child_list)

    def format(self):
        """Walks the tree from this node, printing it out in a format which, if not pretty, is
        at least comprehensible.

        :returns: str

        """
        result = str(self)
        for child in self.children:
            lines = child.format().split('\n')
            for line in lines:
                result += '\n    ' + line
        return result

    @staticmethod
    def _json_safe(text):
        """Safely convert a python string to a format suitable for JSON"""
        if isinstance(text, int) or isinstance(text, float):
            if isinstance(text, bool):
                # yes, bool is a subclass of int. Sigh
                return "true" if text else "false"
            # these types are fine as is
            return text
        my_repr = repr(text)  # it's quoted
        if my_repr.startswith("'"):
            # escape double quotes
            my_repr = my_repr.replace('"', '\\"')
            # replace single quotes
            my_repr = '"' + my_repr[1:-1] + '"'
        return my_repr

    def json_format(self):
        """Walks the tree whose root is this node and returns a JSON representation of the tree.

        :returns: str

        """
        result = '{"name": "' + str(self.symbol) + '"'
        if self._attributes:
            result += ',\n"attributes": {'
            for key in self._attributes:
                value = self._attributes[key]
                if self.symbol == 'document':
                    # special handling of HTML content
                    if hasattr(value, 'replace'):  # don't try replace() on ints, etc
                        value = value.replace('"', '&quot;')
                if isinstance(value, ASTNode):
                    result += '"{}": {},\n'.format(key, value.json_format())
                else:
                    result += '"{}": {},\n'.format(key, self._json_safe(value))
            result = result[:-2]  # remove final ,\n
            result += '}'
        if self.children:
            result += ',\n"children": [\n'
            for child in self.children:
                result += child.json_format() + ',\n'
            result = result[:-2] + ']'
        result += '}'
        return result

    @property
    def context(self):
        """The context mapping required by :py:class:`~utl_lib.utl_yacc.UTLParser`."""
        # attributes has more information than context, but since it does include context, we
        # can just use it
        return self.attributes

    def find_first(self, symbol):
        """Conducts a depth-first search through the tree for a node with symbol `symbol`.

        This is useful if you don't care which match you get, or you know there's only one.

        Returns none if no matching node was found.
        """
        if self.symbol == symbol:
            return self
        for kid in self.children:
            value = kid.find_first(symbol)
            if value is not None:
                return value

    def find_all(self, symbol):
        """Conducts a depth-first search through the tree for nodes with symbol `symbol`.

        Returns a (possibly empty) list of all nodes found.

        """
        matches = []
        if self.symbol == symbol:
            matches.append(self)
        for kid in self.children:
            matches += kid.find_all(symbol)
        return matches

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
