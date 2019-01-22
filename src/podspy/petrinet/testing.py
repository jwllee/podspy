#!/usr/bin/env python


import podspy.petrinet
import numpy as np
from collections import Iterable
from pandas.core.dtypes.common import (
    is_number, is_bool,
    is_list_like
)


__all__ = [
    'assert_arc_equal',
    'assert_place_equal',
    'assert_transition_equal',
    'assert_petrinet_equal'
]


def _check_isinstance(left, right, cls):
    """
    Copied from https://github.com/pandas-dev/pandas/blob/v0.23.4/pandas/util/testing.py#L1257-L1365

    Helper method for assert_* methods to ensure that the two objects being compared have
    the right type before proceeding with the comparison.

    :param left: the first object being compared
    :param right: the second object being compared
    :param cls: the class type to check against
    :raises: AssertionError: Either `left` or `right` is not an instance of `cls`
    """
    err_msg = '{name} Expected type {exp_type}, found {act_type} instead'
    cls_name = cls.__name__

    if not isinstance(left, cls):
        raise AssertionError(err_msg.format(name=cls_name, exp_type=cls,
                                            act_type=type(left)))
    if not isinstance(right, cls):
        raise AssertionError(err_msg.format(name=cls_name, exp_type=cls,
                                            act_type=type(right)))



def assert_attr_equal(attr, left, right, obj='Attributes'):
    """
    Copied from https://github.com/pandas-dev/pandas/blob/v0.23.4/pandas/util/testing.py

    Checks attributes are equal. Both objects must have attributes

    :param attr: attribute name being compared
    :param left: the first object being compared
    :param right: the second object being compared
    :param obj: specify object name being compared, internally used to show appropriate
                assertion message
    :raises: AssertionError: `left` and `right` have different attribute value
    """
    left_attr = getattr(left, attr)
    right_attr = getattr(right, attr)

    if left_attr is right_attr:
        return True
    elif (is_number(left_attr) and np.nan(left_attr) and
          is_number(right_attr) and np.nan(right_attr)):
        return True

    try:
        result = left_attr == right_attr
    except TypeError:
        result = False
    if not isinstance(result, bool) and isinstance(result, Iterable):
        result = all(result)

    if result:
        return True
    else:
        msg = 'Attribute "{attr}" are different'.format(attr=attr)
        raise_assert_detail(obj, msg, left_attr, right_attr)


def raise_assert_detail(obj, message, left, right, diff=None):
    """
    Copied from https://github.com/pandas-dev/pandas/blob/v0.23.4/pandas/util/testing.py

    """
    msg = """{obj} are different
    
    {message}
    [left]: {left}
    [right]: {right}
    """.format(obj=obj, message=message, left=left, right=right)

    if diff is not None:
        msg += '\n[diff]: {diff}'.format(diff=diff)

    raise AssertionError(msg)


def _assert_petrinet_node_equal(left, right,
                                check_id=True,
                                check_local_id=True,
                                check_graph=True,
                                check_attr=True,
                                obj='PetrinetNode'):
    _check_isinstance(left, right, podspy.petrinet.elements.PetrinetNode)

    if check_local_id:
        assert_attr_equal('local_id', left, right, obj)

    assert_attr_equal('label', left, right, obj)


def _assert_petrinet_edge_equal(left, right,
                                check_id=True,
                                check_local_id=True,
                                check_graph=True,
                                check_attr=True,
                                obj='PetrinetEdge'):
    _check_isinstance(left, right, podspy.petrinet.elements.PetrinetEdge)

    if check_local_id:
        assert_attr_equal('local_id', left, right, obj)

    assert_attr_equal('label', left, right, obj)

    _check_isinstance(left.src, right.src, type(left.src))
    _check_isinstance(left.target, right.target, type(left.target))

    if isinstance(left.src, podspy.petrinet.Transition):
        assert_transition_equal(left.src, right.src, check_id, check_local_id,
                                check_graph, check_attr, '{obj}.src'.format(obj=obj))

        # target must be a place
        assert_place_equal(left.target, right.target, check_id, check_local_id,
                           check_graph, check_attr, '{obj}.target'.format(obj=obj))
    else:
        assert_place_equal(left.src, right.src, check_id, check_local_id,
                           check_graph, check_attr, '{obj}.src'.format(obj=obj))

        # target must be a transition
        assert_transition_equal(left.target, right.target, check_id, check_local_id,
                                check_graph, check_attr, '{obj}.target'.format(obj=obj))


def assert_transition_equal(left, right,
                            check_id=True,
                            check_local_id=True,
                            check_graph=True,
                            check_attr=True,
                            obj='Transition'):
    """Check that the left and right Transition are equal

    :param left: the first Transition
    :param right: the second Transition
    :param check_id: whether to check if the Transition id are equal
    :param check_local_id: whether to check if the Transition local id are equal
    :param check_graph: whether to check if the Transition graph are equal
    :param check_attr: whether to check if the Transition attributes are equal
    :param obj: specify object name being compared, internally used to show
                appropriate assertion message
    """
    _check_isinstance(left, right, podspy.petrinet.Transition)

    _assert_petrinet_node_equal(left, right,
                                check_id, check_local_id,
                                check_graph, check_attr, obj)

    assert_attr_equal('is_invisible', left, right, obj)


def assert_place_equal(left, right,
                       check_id=True,
                       check_local_id=True,
                       check_graph=True,
                       check_attr=True,
                       obj='Place'):
    """Check that the left and right Place are equal

    :param left: the first Place
    :param right: the second Place
    :param check_id: whether to check if the Place id are equal
    :param check_local_id: whether to check if the Place local id are equal
    :param check_graph: whether to check if the Place graph are equal
    :param check_attr: whether to check if the Place attributes are equal
    :param obj: specify object name being compared, internally used to show
                appropriate assertion message
    """
    _check_isinstance(left, right, podspy.petrinet.elements.Place)

    _assert_petrinet_node_equal(left, right,
                                check_id, check_local_id,
                                check_graph, check_attr, obj)


def assert_arc_equal(left, right,
                     check_id=True,
                     check_local_id=True,
                     check_graph=True,
                     check_attr=True,
                     obj='Arc'):
    """Check that the left and right Arc are equal

    :param left: the first Arc
    :param right: the second Arc
    :param check_id: whether to check if the Arc id are equal
    :param check_local_id: whether to check if the Arc local id are equal
    :param check_graph: whether to check if the Arc graph are equal
    :param check_attr: whether to check if the Arc attributes are equal
    :param obj: specify object name being compared, internally used to show
                appropriate assertion message
    """
    _check_isinstance(left, right, podspy.petrinet.elements.Arc)

    _assert_petrinet_edge_equal(left, right,
                                check_id, check_local_id,
                                check_graph, check_attr, obj)

    assert_attr_equal('weight', left, right, obj)


def _assert_abstract_reset_inhibitor_net_equal(left, right, check_label=True,
                                              check_id=True,
                                              check_local_id=True,
                                              check_graph=True,
                                              check_attr=True,
                                              obj='AbstractResetInhibitorNet'):
    _check_isinstance(left, right, podspy.petrinet.nets.AbstractResetInhibitorNet)

    def assert_collection_len_equal(attr, left, right, id_attr, obj):
        left_attr = getattr(left, attr)
        right_attr = getattr(right, attr)

        left_id = getattr(left, id_attr)
        right_id = getattr(right, id_attr)

        if len(left_attr) != len(right_attr):
            msg1 = 'Number of {attr} are different'.format(attr=attr)
            msg2 = '{len}, {left}'.format(len=len(left_attr), left=left_id)
            msg3 = '{len}, {right}'.format(len=len(right_attr), right=right_id)
            raise_assert_detail(obj, msg1, msg2, msg3)

    if check_label:
        assert_attr_equal('label', left, right, obj)

    assert_collection_len_equal('transitions', left, right, 'label', obj)
    assert_collection_len_equal('places', left, right, 'label', obj)
    assert_collection_len_equal('arcs', left, right, 'label', obj)
    assert_collection_len_equal('reset_arcs', left, right, 'label', obj)
    assert_collection_len_equal('inhibitor_arcs', left, right, 'label', obj)

    left_trans = sorted(left.transitions, key=lambda t: t.label)
    right_trans = sorted(right.transitions, key=lambda t: t.label)

    for t_left, t_right in zip(left_trans, right_trans):
        assert_transition_equal(t_left, t_right,
                                check_id, check_local_id,
                                check_graph, check_attr, '{obj} Transition'.format(obj=obj))

    left_places = sorted(left.places, key=lambda p: p.label)
    right_places = sorted(right.places, key=lambda p: p.label)

    for p_left, p_right in zip(left_places, right_places):
        assert_place_equal(p_left, p_right,
                           check_id, check_local_id,
                           check_graph, check_attr, '{obj} Place'.format(obj=obj))

    left_arcs = sorted(left.arcs, key=lambda a: '{},{}'.format(a.src.label, a.target.label))
    right_arcs = sorted(right.arcs, key=lambda a: '{},{}'.format(a.src.label, a.target.label))

    for a_left, a_right in zip(left_arcs, right_arcs):
        assert_arc_equal(a_left, a_right,
                         check_id, check_local_id,
                         check_graph, check_attr, '{obj} Arc'.format(obj=obj))

    # todo: check reset arcs and etc...


def assert_petrinet_equal(left, right, check_label=True,
                          check_id=True,
                          check_local_id=True,
                          check_graph=True,
                          check_attr=True,
                          obj='Petrinet'):
    """Check that the left and right Petrinet are equal

    :param left: the first Petrinet
    :param right: the second Petrinet
    :param check_label: whether to check if the Petrinet label are equal
    :param check_id: whether to check if the Petrinet elements id are equal
    :param check_local_id: whether to check if the Petrinet elements local id are equal
    :param check_graph: whether to check if the Petrinet elements graph are equal
    :param check_attr: whether to check if the Petrinet elements attributes are equal
    :param obj: specify object name being compared, internally used to show
                appropriate assertion message
    """
    _check_isinstance(left, right, podspy.petrinet.Petrinet)

    _assert_abstract_reset_inhibitor_net_equal(left, right,
                                               check_label, check_id,
                                               check_local_id, check_graph,
                                               check_attr, obj)