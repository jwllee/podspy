#!/usr/bin/env python


import podspy.petrinet as petri
import pytest


def test_assert_transition_equal_only_check_label():
    graph = None

    a0 = petri.Transition(graph, 'a')
    a1 = petri.Transition(graph, 'a')

    try:
        petri.testing.assert_transition_equal(a0, a1, check_id=False, check_local_id=False,
                                              check_graph=False, check_attr=False)
    except AssertionError:
        pytest.fail('Transitions should be equal')

    b0 = petri.Transition(graph, 'b')

    try:
        petri.testing.assert_transition_equal(a0, b0, check_id=False, check_local_id=False,
                                              check_graph=False, check_attr=False)
        pytest.fail('Should have raised assertion error on different transitions')
    except AssertionError:
        pass


def test_assert_place_equal_only_check_label():
    graph = None

    p0 = petri.Place(graph, 'p')
    p1 = petri.Place(graph, 'p')

    try:
        petri.testing.assert_place_equal(p0, p1, check_id=False, check_local_id=False,
                                         check_graph=False, check_attr=False)
    except AssertionError:
        pytest.fail('Places should be equal')

    q0 = petri.Place(graph, 'q')

    try:
        petri.testing.assert_place_equal(p0, q0, check_id=False, check_local_id=False,
                                         check_graph=False, check_attr=False)
        pytest.fail('Should have raised assertion error on different places')
    except AssertionError:
        pass


def test_assert_arc_equal_only_check_label():
    graph = None

    # arc 0
    p0 = petri.Place(graph, 'p')
    a0 = petri.Transition(graph, 'a')
    a0 = petri.Arc(p0, a0, 1)

    # arc 1
    p1 = petri.Place(graph, 'p')
    a1 = petri.Transition(graph, 'a')
    a1 = petri.Arc(p1, a1, 1)

    try:
        petri.testing.assert_arc_equal(a0, a1, check_id=False, check_local_id=False,
                                       check_graph=False, check_attr=False)
    except AssertionError:
        pytest.fail('Arcs should be equal')


def test_assert_petrinet_equal_only_check_element_label():
    net0 = petri.PetrinetFactory.new_petrinet('n0')
    net1 = petri.PetrinetFactory.new_petrinet('n1')

    a0 = net0.add_transition('a')
    b0 = net0.add_transition('b')
    p0 = net0.add_place('p')
    net0.add_arc(a0, p0)
    net0.add_arc(p0, b0)

    b1 = net1.add_transition('b')
    a1 = net1.add_transition('a')
    p1 = net1.add_place('p')
    net1.add_arc(p1, b1)
    net1.add_arc(a1, p1)

    try:
        petri.testing.assert_petrinet_equal(net0, net1, check_label=False,
                                            check_id=False, check_local_id=False,
                                            check_graph=False, check_attr=False)
    except AssertionError:
        pytest.fail('Petrinets should be equal')

    net2 = petri.PetrinetFactory.new_petrinet('n2')

    a2 = net2.add_transition('a')
    p2 = net2.add_place('p')
    net2.add_arc(p2, a2)

    try:
        petri.testing.assert_petrinet_equal(net0, net2, check_label=False,
                                            check_id=False, check_local_id=False,
                                            check_graph=False, check_attr=False)
        pytest.fail('Should have raised assertion error on different petrinets')
    except AssertionError:
        pass
