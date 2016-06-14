#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module of classes used to implement an Abstract Syntax Tree structure. Actually, theyre used
to implement parse tree as well, name is historical accident.


| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>


"""
from typing import Mapping, Any, Iterable, MutableMapping, Sequence, Optional, Iterator
from utl_lib.utl_parse_handler import FrozenDict


class ASTNodeError(Exception):
    '''Exceptions raised by misuse of an ASTNode object.'''
    pass


class ASTNode(object):
    """A node in the AST.

    :param str symbol_name: A name for the node, usually related to the rule
        that produced it.

    :param dict attrs: key-value pairs attaching arbitrary attributes to this
        node. For attributes that are not common to all nodes.

    :param list children: Nodes to be attached as children of this node.

    :raises ASTNodeError: if any member of `children` is not an ASTNode

    """

    def __init__(self, symbol_name: str, attrs: Mapping[str, Any],
                 children: Iterable["ASTNode"]) -> None:
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
    def attributes(self) -> MutableMapping[str, Any]:
        """A :py:class:`~utl_lib.utl_parse_handler.FrozenDict` containing arbitrary key-value
        pairs from the node's creator.

        """
        return self._attributes

    @attributes.setter
    def attributes(self, new_attrs: Mapping[str, Any]) -> None:  # pylint: disable=C0111
        if new_attrs is None:
            self._attributes = FrozenDict()
        elif not isinstance(new_attrs, FrozenDict):
            # self._attributes = FrozenDict(new_attrs)
            attr_copy = {}
            for key in new_attrs:
                if isinstance(new_attrs[key], ASTNode):
                    attr_copy[key] = FrozenASTNode(new_attrs[key])
                else:
                    attr_copy[key] = new_attrs[key]
            self._attributes = FrozenDict(attr_copy)
        else:
            self._attributes = new_attrs

    # pylint: disable=R0911
    def __eq__(self, other: Any) -> bool:
        '''Deep equality test, useful for testing.

        :param Any other: The object compared.

        '''
        # note this is optimized for debugging, *not* performance
        # pylint: disable=W0212
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

    def add_child(self, child: "ASTNode") -> None:
        '''Add child to the list of children of this node. `child` will become the last child,
        making this appropriate for right-expanding rules like: a : a b

        Note: If child has no parent node, it is added directly to our children. If child
        already has a parent node, a copy is made, then added. This prevents cases where a node
        would have a child whose parent is not that node.

        :param ASTNode child: A child node.

        :raises ASTNodeError: if child is not an ASTNode, or `child` == `self`

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

    def copy(self) -> "ASTNode":
        """Returns a new instance of :py:class:`utl_lib.ast_node.ASTNode` whose attributes have
        the same values as this.
        """
        return ASTNode(self.symbol, self._attributes,
                       [kid.copy() for kid in self.children])

    def add_first_child(self, child: "ASTNode") -> None:
        '''Add child to the list of children of this node. `child` will become the first child,
        making this appropriate for left-expanding rules like: a : b a

        :param ASTNode child: A child node.
        '''
        # we might have passed a generator to __init__(), or even a set
        self.children = list(self.children)
        child.parent = self
        self.children.insert(0, child)

    def add_children(self, iterator: Iterable["ASTNode"]) -> None:
        """Add each item in iterator to the list of children. Items should be nodes. Note that
        the nodes will be inserted into the beginning of the list, and end up in reverse order
        of the iterator.

        :param list iterator: :py:class:`utl_lib.ast_node.ASTNode` objects to be added.

        """
        # we might have passed a generator to __init__(), or even a set
        self.children = list(self.children)
        for child in iterator:
            if child:
                self.add_child(child)

    def __str__(self) -> str:
        result = '{}: '.format(self.symbol)
        if self.symbol == 'literal':
            value = self._attributes['value']
            if isinstance(value, (ASTNode, FrozenASTNode, )) and value.symbol == "array_literal":
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

    def __repr__(self) -> str:
        child_list = ""
        for child in self.children:
            if child_list:
                child_list += ", {}".format(child.symbol)
            else:
                child_list = child.symbol
        return 'ASTNode("{}", ..., [{}])'.format(self.symbol, child_list)

    def format(self) -> str:
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

    def walk(self) -> Iterator["ASTNode"]:
        """Walk the tree rooted at this node, yielding each node in turn.

        Order is parent-first, depth-first.

            node1
             |
            child1      child2   child3
             |           |
            grandchild1 grandchild2

            node1.walk() ==> (node1, child1, grandchild1, child2, grandchild2, child3)

        """
        yield self
        for child in self.children:
            yield from child.walk()


    # pylint: disable=W9003,W9004
    # appears to be no way to make pylint accept docstring
    @staticmethod
    def _json_safe(value: Any) -> Any:
        """Safely convert a python value to a type suitable for JSON.

        :parm Any value: A python value of some sort.

        """
        if isinstance(value, int) or isinstance(value, float):
            if isinstance(value, bool):
                # yes, bool is a subclass of int. Sigh
                return "true" if value else "false"
            # these types are fine as is
            return value
        my_repr = repr(value)  # it's quoted
        # repr() returns value in "" usually
        # but uses '' if there are embedded '"'
        # but single quotes are invalid in JSON
        if my_repr.startswith("'"):
            # escape double quotes
            my_repr = my_repr.replace('"', '\\"')
            # replace single quotes
            my_repr = '"' + my_repr[1:-1] + '"'
        return my_repr

    # TODO: Fix cases where we have to check for FrozenASTNode. I don't think
    # ASTNode should have to care that FrozenASTNode exists.
    def json_format(self) -> str:
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
                if isinstance(value, (ASTNode, FrozenASTNode, )):
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
    def context(self) -> MutableMapping[str, Any]:
        """The context mapping required by :py:class:`~utl_lib.utl_yacc.UTLParser`."""
        # attributes has more information than context, but since it does include context, we
        # can just use it
        return self.attributes

    def find_first(self, symbol: str) -> Optional["ASTNode"]:
        """Conducts a depth-first search through the tree for a node.

        This is useful if you don't care which match you get, or you know there's only one.

        :param str symbol: The symbol of the node to be found.

        :returns ASTNode, None: The found node, or ``None``.

        """
        if self.symbol == symbol:
            return self
        for kid in self.children:
            value = kid.find_first(symbol)
            if value is not None:
                return value

    def find_all(self, symbol: str) -> Sequence["ASTNode"]:
        """Conducts a depth-first search through the tree for nodes with symbol `symbol`.

        :param str symbol: the node symbol to be matched.

        :returns list: The found nodes

        """
        matches = []
        if self.symbol == symbol:
            matches.append(self)
        for kid in self.children:
            matches += kid.find_all(symbol)
        return matches


class FrozenASTNode(object):
    """An immutable version of ASTNode, for use with dictionaries, sets, etc.

    Note equality is defined by children, attributes, and symbol -- but does
    not check parent.

    :param ASTNode ast_node: A node whose data will be
        copied to this.

    """

    def __init__(self, ast_node: ASTNode) -> None:
        if not isinstance(ast_node, ASTNode):
            raise ValueError("FrozenASTNode() requires an ASTNode as input.")

        self._children = []
        for child in ast_node.children:
            self._children.append(FrozenASTNode(child))
        self._children = tuple(self._children)  # pylint: disable=R0204
        self._symbol = ast_node.symbol
        # pylint: disable=protected-access
        self._attributes = ast_node._attributes   # a FrozenDict

    def unfreeze(self) -> ASTNode:
        """Creates an :py:class:`utl_lib.ast_node.ASTNode` instance from the
        frozen node.

        NOTE: attributes whose values are data structures may not get a copy
        of the value, thus modifying the returned node risks altering this
        node. Be careful.

        """
        return ASTNode(self._symbol, self._attributes,
                       [child.unfreeze() if isinstance(child, FrozenASTNode) else child
                        for child in self.children])

    @property
    def attributes(self) -> Mapping[str, Any]:
        """A :py:class:`~utl_lib.utl_parse_handler.FrozenDict` immutable mapping."""
        return self._attributes

    @property
    def symbol(self) -> str:
        """A string with a symbol for the production this node represents."""
        return self._symbol

    @property
    def children(self) -> Sequence[ASTNode]:
        """A tuple of :py:class:`FrozenASTNode` objects that are children to this node."""
        return self._children

    def __hash__(self) -> int:
        value = hash(self.symbol)
        value ^= hash(self.attributes)
        for child in self.children:
            value ^= hash(child)
        return value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FrozenASTNode):
            return hash(self) == hash(other)
        return False

    def __str__(self):
        result = '{}: '.format(self.symbol)
        if self.symbol == 'literal':
            value = self._attributes['value']
            result += repr(self._attributes['value'])
        elif self.symbol in ('operator', 'id'):
            result += self._attributes['symbol']
        elif self.symbol == 'document':
            result += repr(self._attributes['text'])
        elif self._attributes:
            attrs = ', '.join(["{}: {}".format(key, repr(value))
                               for key, value in self._attributes.items()])
            result += " {%s}" % attrs
        return result

    def __repr__(self) -> str:
        child_list = ""
        for child in self.children:
            if child_list:
                child_list += ", {}".format(child.symbol)
            else:
                child_list = child.symbol
        return 'FrozenASTNode("{}", ..., [{}])'.format(self.symbol, child_list)

    def json_format(self) -> str:
        """Walks the tree whose root is this node and returns a JSON representation of the tree.

        :returns: str

        """
        return self.unfreeze().json_format()

# Local Variables:
# python-indent-offset: 4
# fill-column: 100
# indent-tabs-mode: nil
# End:
