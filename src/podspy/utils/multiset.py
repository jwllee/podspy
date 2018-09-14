#!/usr/bin/env python

"""This is the collection module.

This module contains collection classes.
"""


from abc import ABC, abstractmethod
import itertools as its
import functools as fts
from sortedcontainers import SortedDict
import logging


__all__ = [
    'SortedMultiSet',
    'HashMultiSet'
]


logger = logging.getLogger(__file__)


class AbstractMultiSet(ABC):
    @abstractmethod
    def __init__(self):
        self.map = None
        self.size = None
        self.hash_code = None
        self.hash_valid = False

    def __len__(self):
        return self.size

    def __iter__(self):
        return MultiSetIterator(self)

    def __lt__(self, other):
        """Returns true if this multiset is less than the given multiset,
        i.e., all objects in this multiset should be contained in the given set
        and the number of occurrences in this multiset is strictly less than
        the given multiset.

        :param other: other multiset to compare against
        :type other: multiset-like
        :return: whether if this multiset is less than the other one
        :rtype: bool
        """
        all_items = set(self.base_set())
        all_items.update(other.base_set())

        # logger.debug('all_items: {}'.format(all_items))

        for ele in all_items:
            # if for any item, the occurrences in the other multiset is less
            # than or equal this multiset, then this multiset cannot be less
            # than the other multiset
            if other.occurrences(ele) <= self.occurrences(ele):
                return False
        return True

    def __le__(self, other):
        """Returns true if this multiset is less or equal to the given multiset,
        i.e., all objects in this multiset should be contained in the given set
        and the number of occurrences in the given set is at least the number of
        occurrences in this multiset.

        :param other: other multiset to compare against
        :type other: multiset-like
        :return: whether if this multiset is less than or equal to the other one
        :rtype: bool
        """
        all_items = set(self.base_set())
        all_items.update(other.base_set())

        # logger.debug('all_items: {}'.format(all_items))

        for ele in all_items:
            if not self.occurrences(ele) <= other.occurrences(ele):
                return False
        return True

    def __eq__(self, other):
        """Returns true if this multiset is equal to the given multiset, i.e., all
        objects in this multiset should be contained in the given set and the number
        of occurrences in this multiset is equal to the given one.

        :param other: other multiset to compare against
        :type other: multiset-like
        :return: whether if this multiset is equal to the other one
        :rtype: bool
        """
        if not isinstance(other, AbstractMultiSet):
            return False
        return self.map == other.map

    def __ge__(self, other):
        """Returns true if this multiset is greater than or equal to the given multiset,
        i.e., all objects in the given multiset are contained in this multiset and the
        number of occurrences in this multiset is greater than or equal to the given one.

        :param other: other multiset to compare against
        :type other: multiset-like
        :return: whether if this multiset is greater than or equal to the other one
        :rtype: bool
        """
        all_items = set(self.base_set())
        all_items.update(other.base_set())

        for ele in all_items:
            if not self.occurrences(ele) >= other.occurrences(ele):
                return False
        return True

    def __gt__(self, other):
        """Returns true if this multiset is greater than to the given multiset, i.e., all
        objects in the given multiset are contained in this multiset and the number of
        occurrences in this multiset is greater than the given one.

        :param other:
        :return:
        """
        all_items = set(self.base_set())
        all_items.update(other.base_set())

        # logger.debug('all_items: {}'.format(all_items))

        for ele in all_items:
            # if for any item, the occurrences in the other multiset is more
            # than or equal this multiset, then this multiset cannot be more
            # than the other multiset
            if other.occurrences(ele) >= self.occurrences(ele):
                return False
        return True

    def __contains__(self, item):
        return item in self.map

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__,
                                           self.hash_code, self.hash_valid,
                                           self.size, self.map)

    def __str__(self):
        format = lambda kv: '({}, {})'.format(kv[0], kv[1])
        formatted = map(format, self.map.items())
        return '[' + ' '.join(formatted) + ']'

    def __hash__(self):
        if not self.hash_valid:
            self.hash_code = hash(frozenset(self.map.items()))
            self.hash_valid = True
        return self.hash_code

    def occurrences(self, key):
        return self.map[key] if key in self.map else 0

    def base_set(self):
        return self.map.keys()

    def items(self):
        return self.map.items()

    def retain_all(self, c):
        """Keeps all elements of the given collection in this multiset
        where multiplicities are taken into account.

        :param c: AbstractMultiSet
        :type c: multiset-like
        :return: true if the multiset changed from calling this method.
        :rtype: bool

        >> ms0 = HashMultiSet(['a', 'c'])
        >> ms1 = HashMultiSet(['a', 'a', 'b', 'b'])
        >> ms0.retain_all(ms1)

        The occurrences of 'a' doesn't change because `ms1` contains two 'a'
        >> assert ms0.occurrences('a') == 1
        The occurrences of 'c' goes to zero because `ms1` does not contain 'c'
        >> assert ms0.occurrences('c') == 0
        The occurrences of 'b' goes to zero because `ms0` does not contain 'b'
        >> assert ms0.occurrences('b') == 0
        """
        changed = False
        to_remove = set()
        for key in self.map:
            occ_to_retain = c.occurrences(key)
            occ_in_this = self.occurrences(key)
            if occ_in_this >= occ_to_retain:
                # keep occ_to_retain
                diff = occ_in_this - occ_to_retain
                self.size -= diff
                if occ_to_retain == 0:
                    to_remove.add(key)
                else:
                    self.map[key] = occ_to_retain
                changed = True
                self.hash_valid = False
        # necessary removal
        for key in to_remove:
            del self.map[key]
        return changed

    def add(self, key, weight=1):
        if weight == 0:
            raise ValueError('Cannot add 0 weight of an item!')
        self.hash_valid = False
        # note that in Python 3, int should be unbounded
        self.size = self.size + weight
        if key not in self.map:
            assert weight > 0, 'Trying to add {} weight for new key'.format(weight)
            self.map[key] = weight
            return weight
        else:
            new_val = self.map[key] + weight
            if new_val == 0:
                del self.map[key]
            else:
                assert new_val > 0, 'Cannot have {} weight for existing key'.format(new_val)
                self.map[key] = new_val
            return new_val

    def add_all(self, *cols):
        """Adds the given collections to this multiset. If the given collection is not
        a multiset, then the implementation is diverted to an iterable.


        :param c: iterable
        :return: bool
                 whether if the multiset is modified
        """
        changed = False
        for c in cols:
            changed = self.__add_all(c) or changed
        return changed

    def __add_all(self, c):
        changed = False
        if len(c) == 0:
            return changed
        changed = True
        self.hash_valid = False
        try:
            # treating c as a multiset
            for key in c.base_set():
                self.add(key, c.occurrences(key))
        except:
            # c cannot be treated as a multiset
            for key in c:
                self.add(key)
        return changed

    def __add__(self, other):
        _sum = self.__class__()
        _sum.add_all(self)
        _sum.add_all(other)
        return _sum

    def combine(self, *others):
        return fts.reduce(lambda x, y: x + y, others, self)

    def __sub__(self, other):
        diff = self.__class__()
        diff.add_all(self)
        diff.remove_all(other)
        return diff

    def difference(self, *others):
        return fts.reduce(lambda x, y: x - y, others, self)

    def to_list(self):
        """Converts this multiset to a list, such that each element occurs as
        often as returned by the iterator of the multiset (its number of occurrences).

        :return: list
        """
        return list(self)

    def contains_at_least(self, item, occ):
        return self.occurrences(item) >= occ

    def remove_all(self, items):
        logger.debug('Removing all {}'.format(items))
        removed = False

        if isinstance(items, AbstractMultiSet):
            for item in items.base_set():
                removed = self.remove(item, items.occurrences(item))
        else:
            for item in items:
                removed = self.remove(item) or removed

        return removed

    def remove(self, item, count=1):
        if self.occurrences(item) == 0:
            return False
        else:
            self.hash_valid = False
            # remove count occurrences
            occ = self.map[item]
            if occ >= count:
                self.size -= count
                self.map[item] = self.map[item] - count
            else:
                self.size -= occ
                del self.map[item]
            return True

    def empty(self):
        return self.size == 0


class MultiSetIterator:
    def __init__(self, multiset):
        self.multiset = multiset
        iterables = []
        for key in self.multiset.map:
            repeated = its.repeat(key, times=self.multiset.occurrences(key))
            iterables.append(repeated)
        self.iterator = its.chain(*iterables)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.iterator)


class HashMultiSet(AbstractMultiSet):
    def __init__(self, *iterable):
        super().__init__()
        self.map = dict()
        self.size = 0
        self.add_all(*iterable)


class SortedMultiSet(AbstractMultiSet):
    """Sorted multiset is a sorted mutable multiset.

    Using the sorted dict implementation from sortedcollections,
    the design of sorted multiset uses a sorted dict to manage the
    multiplicities of items, and maintains the order of the items
    as dict keys.
    """
    def __init__(self, *iterable):
        super().__init__()
        self.map = SortedDict()
        self.size = 0
        self.add_all(*iterable)
