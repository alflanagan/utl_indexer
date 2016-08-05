#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Immutable collections.

| © 2015-2016 BH Media Group, Inc.
| BH Media Group Digital Development

.. codeauthor:: A. Lloyd Flanagan <aflanagan@bhmginc.com>

"""
import collections
import copy


class FrozenDict(collections.Mapping):
    """Immutable dictionary class by Raymond Hettinger himself.

    This allows handlers to return context info in a form that has the goodness of immutability,
    and is hashable.

    :param collections.Mapping somedict: A mapping whose values will be used to initialize the
        FrozenDict. Note this is the only way to add values!

    """

    def __init__(self, somedict=None):
        if somedict is None:
            somedict = {}
        self._dict = dict(somedict)   # make a copy
        # if values of self._dict are not hashable, we're not hashable. Fail now.
        self._hash = hash(frozenset(self._dict.items()))

    def __getitem__(self, key):
        return self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return self._dict == other._dict  # pylint: disable=W0212

    def combine(self, *args, **keys):
        """D.combine([E, ]**F) -> D'.  Create FrozenSet D' from D and dict/iterable E and F.

    D' is initially a copy of D.
    If E is present and has a .keys() method, then does:  for k in E: D'[k] = E[k]
    If E is present and lacks a .keys() method, then does:  for k, v in E: D'[k] = v
    In either case, this is followed by: for k in F:  D'[k] = F[k]

    :param args: one more dictionaries to be combined with this one.

    :param keys: key-value pairs that will be combined with this dictionary.

    :return: A new FrozenDict combining all the keys and values.

    :rtype: FrozenDict

    """
        # yes, above is a direct steal from dict.update() docstring. Don't call this update()
        # because it does not modify-in-place, it returns a new FrozenDict
        newdict = self._dict.copy()
        newdict.update(*args, **keys)
        return FrozenDict(newdict)

    def delkey(self, *args):
        """D.delkey(key [, ...]) -> D' which contains {key:D[key] for key in D if key not in args}.

        :param str args: One or more keys to delete.

        :return: A new dictionary without those keys.
        :rtype: FrozenDict

        """
        newdict = self._dict.copy()
        for arg in args:
            del newdict[arg]
        return FrozenDict(newdict)

    def thaw(self):
        """Returns a dictionary with the same keys and values as this instance.

        Be careful: uses :py:func:`copy.deepcopy`. Safer immutability, but may be a problem on
        large objects.

        """
        newdict = {}
        for key in self._dict:
            # keys are immutable anyway
            newdict[key] = copy.deepcopy(self._dict[key])
        return newdict

    def __str__(self):
        return "frozen: {}".format(self._dict)

    def __repr__(self):
        return "FrozenDict({})".format(repr(self._dict))
