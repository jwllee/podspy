#!/usr/bin/env python


import podspy.conformance
import podspy.petrinet as petri
import podspy.log

from podspy.conformance import alignment


import pytest
import pandas as pd
import numpy as np
import collections as cols


@pytest.fixture(
    scope='function'
)
def trace_l3():
    event_df = pd.DataFrame({
        podspy.log.CASEID: ['1', '1', '1'],
        podspy.log.ACTIVITY: ['a', 'b', 'c']
    })
    return event_df


@pytest.fixture(
    scope='function'
)
def trace_net_l3():
    net = petri.PetrinetFactory.new_petrinet('1')

    t_a = net.add_transition('a')
    t_b = net.add_transition('b')
    t_c = net.add_transition('c')
    src = net.add_place('p0')
    sink = net.add_place('p3')
    p0 = net.add_place('p1')
    p1 = net.add_place('p2')
    net.add_arc(src, t_a)
    net.add_arc(p0, t_b)
    net.add_arc(p1, t_c)
    net.add_arc(t_a, p0)
    net.add_arc(t_b, p1)
    net.add_arc(t_c, sink)

    init_marking = petri.Marking([src])
    final_markings = [petri.Marking([sink])]

    return petri.PetrinetFactory.new_accepting_petrinet(net, init_marking, final_markings)


@pytest.fixture(
    scope='function'
)
def model_cc_book():
    """Petri net model from conformance checking book Figure 7.1

    :return: accepting petri net
    """
    net = petri.PetrinetFactory.new_petrinet('n7.1')

    As = net.add_transition('As')
    Aa = net.add_transition('Aa')
    Fa = net.add_transition('Fa')
    Sso = net.add_transition('Sso')
    Co = net.add_transition('Co')
    Ro = net.add_transition('Ro')
    Da1 = net.add_transition('Da1')
    tau = net.add_transition('tau', is_invisible=True)
    Ao = net.add_transition('Ao')
    Do = net.add_transition('Do')
    Aaa = net.add_transition('Aaa')
    Da2 = net.add_transition('Da2')
    Af = net.add_transition('Af')

    p0 = net.add_place('p0')
    p1 = net.add_place('p1')
    p2 = net.add_place('p2')
    p3 = net.add_place('p3')
    p4 = net.add_place('p4')
    p5 = net.add_place('p5')
    p6 = net.add_place('p6')
    p7 = net.add_place('p7')
    p8 = net.add_place('p8')
    p9 = net.add_place('p9')
    p10 = net.add_place('p10')
    p11 = net.add_place('p11')

    p0_As = net.add_arc(p0, As)
    p1_Da1 = net.add_arc(p1, Da1)
    p1_Aa = net.add_arc(p1, Aa)
    p2_Fa = net.add_arc(p2, Fa)
    p3_tau = net.add_arc(p3, tau)
    p4_Sso = net.add_arc(p4, Sso)
    p5_Ro = net.add_arc(p5, Ro)
    p6_Co = net.add_arc(p6, Co)
    p6_tau = net.add_arc(p6, tau)
    p7_Ao = net.add_arc(p7, Ao)
    p7_Do = net.add_arc(p7, Do)
    p8_Da2 = net.add_arc(p8, Da2)
    p9_Aaa = net.add_arc(p9, Aaa)
    p10_Af = net.add_arc(p10, Af)

    As_p1 = net.add_arc(As, p1)
    Aa_p2 = net.add_arc(Aa, p2)
    Aa_p4 = net.add_arc(Aa, p4)
    Fa_p3 = net.add_arc(Fa, p3)
    Sso_p5 = net.add_arc(Sso, p5)
    Co_p4 = net.add_arc(Co, p4)
    Ro_p6 = net.add_arc(Ro, p6)
    Da1_p10 = net.add_arc(Da1, p10)
    tau_p7 = net.add_arc(tau, p7)
    Do_p8 = net.add_arc(Do, p8)
    Ao_p9 = net.add_arc(Ao, p9)
    Aaa_p10 = net.add_arc(Aaa, p10)
    Da2_p10 = net.add_arc(Da2, p10)
    Af_p11 = net.add_arc(Af, p11)

    init_marking = petri.Marking([p0])
    final_marking = petri.Marking([p11])
    apn = petri.PetrinetFactory.new_accepting_petrinet(net, init_marking, {final_marking})

    return apn


@pytest.fixture(
    scope='function'
)
def trace_cc_book():
    """Example trace taken from Figure 7.2 of the conformance checking book

    :return: trace
    """
    event_df = pd.DataFrame({
        podspy.log.CASEID: ['0' for _ in range(7)],
        podspy.log.ACTIVITY: ['As', 'Aa', 'Sso', 'Ro', 'Ao', 'Aaa', 'Aaa']
    })
    return event_df


@pytest.fixture(
    scope='function'
)
def tran_ev_mapping_cc_book(model_cc_book):
    """Mapping from transition to event activity of Figure 7.3 of the conformance checking book

    :return: mapping
    """
    label_to_trans = {t.label:t for t in model_cc_book.net.transitions}
    mapping = {t:t.label for t in model_cc_book.net.transitions}
    del mapping[label_to_trans['Da1']]
    del mapping[label_to_trans['Da2']]
    mapping[label_to_trans['Da1']] = 'Da'
    mapping[label_to_trans['Da2']] = 'Da'

    return mapping


@pytest.fixture(
    scope='function'
)
def snp_cc_book(model_cc_book, trace_cc_book):
    """Example synchronous net product taken from Figure 7.3 of the conformance checking book

    :return: synchronous net product
    """
    net = petri.PetrinetFactory.new_petrinet('snp')

    m_As = net.add_transition('(As,>>)')
    m_Aa = net.add_transition('(Aa,>>)')
    m_Fa = net.add_transition('(Fa,>>)')
    m_Sso = net.add_transition('(Sso,>>)')
    m_Co = net.add_transition('(Co,>>)')
    m_Ro = net.add_transition('(Ro,>>)')
    m_Da1 = net.add_transition('(Da1,>>)')
    m_tau = net.add_transition('(tau,>>)', is_invisible=True)
    m_Ao = net.add_transition('(Ao,>>)')
    m_Do = net.add_transition('(Do,>>)')
    m_Aaa = net.add_transition('(Aaa,>>)')
    m_Da2 = net.add_transition('(Da2,>>)')
    m_Af = net.add_transition('(Af,>>)')

    p0 = net.add_place('p0')
    p1 = net.add_place('p1')
    p2 = net.add_place('p2')
    p3 = net.add_place('p3')
    p4 = net.add_place('p4')
    p5 = net.add_place('p5')
    p6 = net.add_place('p6')
    p7 = net.add_place('p7')
    p8 = net.add_place('p8')
    p9 = net.add_place('p9')
    p10 = net.add_place('p10')
    p11 = net.add_place('p11')

    p0_As = net.add_arc(p0, m_As)
    p1_Da1 = net.add_arc(p1, m_Da1)
    p1_Aa = net.add_arc(p1, m_Aa)
    p2_Fa = net.add_arc(p2, m_Fa)
    p3_tau = net.add_arc(p3, m_tau)
    p4_Sso = net.add_arc(p4, m_Sso)
    p5_Ro = net.add_arc(p5, m_Ro)
    p6_Co = net.add_arc(p6, m_Co)
    p6_tau = net.add_arc(p6, m_tau)
    p7_Ao = net.add_arc(p7, m_Ao)
    p7_Do = net.add_arc(p7, m_Do)
    p8_Da2 = net.add_arc(p8, m_Da2)
    p9_Aaa = net.add_arc(p9, m_Aaa)
    p10_Af = net.add_arc(p10, m_Af)

    As_p1 = net.add_arc(m_As, p1)
    Aa_p2 = net.add_arc(m_Aa, p2)
    Aa_p4 = net.add_arc(m_Aa, p4)
    Fa_p3 = net.add_arc(m_Fa, p3)
    Sso_p5 = net.add_arc(m_Sso, p5)
    Co_p4 = net.add_arc(m_Co, p4)
    Ro_p6 = net.add_arc(m_Ro, p6)
    Da1_p10 = net.add_arc(m_Da1, p10)
    tau_p7 = net.add_arc(m_tau, p7)
    Do_p8 = net.add_arc(m_Do, p8)
    Ao_p9 = net.add_arc(m_Ao, p9)
    Aaa_p10 = net.add_arc(m_Aaa, p10)
    Da2_p10 = net.add_arc(m_Da2, p10)
    Af_p11 = net.add_arc(m_Af, p11)

    l_As = net.add_transition('(>>,As)')
    l_Aa = net.add_transition('(>>,Aa)')
    l_Sso = net.add_transition('(>>,Sso)')
    l_Ro = net.add_transition('(>>,Ro)')
    l_Ao = net.add_transition('(>>,Ao)')
    l_Aaa1 = net.add_transition('(>>,Aaa)')
    l_Aaa2 = net.add_transition('(>>,Aaa)')

    p12 = net.add_place('p12')
    p13 = net.add_place('p13')
    p14 = net.add_place('p14')
    p15 = net.add_place('p15')
    p16 = net.add_place('p16')
    p17 = net.add_place('p17')
    p18 = net.add_place('p18')
    p19 = net.add_place('p19')

    p12_l_As = net.add_arc(p12, l_As)
    p13_l_Aa = net.add_arc(p13, l_Aa)
    p14_l_Sso = net.add_arc(p14, l_Sso)
    p15_l_Ro = net.add_arc(p15, l_Ro)
    p16_l_Ao = net.add_arc(p16, l_Ao)
    p17_l_Aaa1 = net.add_arc(p17, l_Aaa1)
    p18_l_Aaa2 = net.add_arc(p18, l_Aaa2)

    l_As_p13 = net.add_arc(l_As, p13)
    l_Aa_p14 = net.add_arc(l_Aa, p14)
    l_Sso_p15 = net.add_arc(l_Sso, p15)
    l_Ro_p16 = net.add_arc(l_Ro, p16)
    l_Ao_p17 = net.add_arc(l_Ao, p17)
    l_Aaa1_p18 = net.add_arc(l_Aaa1, p18)
    l_Aaa2_p19 = net.add_arc(l_Aaa2, p19)

    # synchronous moves
    s_As = net.add_transition('(As,As)')
    s_Aa = net.add_transition('(Aa,Aa)')
    s_Sso = net.add_transition('(Sso,Sso)')
    s_Ro = net.add_transition('(Ro,Ro)')
    s_Ao = net.add_transition('(Ao,Ao)')
    s_Aaa1 = net.add_transition('(Aaa,Aaa)')
    s_Aaa2 = net.add_transition('(Aaa,Aaa)')

    # net arcs to sync move
    net.add_arc(p0, s_As)
    net.add_arc(p1, s_Aa)
    net.add_arc(p4, s_Sso)
    net.add_arc(p5, s_Ro)
    net.add_arc(p7, s_Ao)
    net.add_arc(p9, s_Aaa1)
    net.add_arc(p9, s_Aaa2)

    net.add_arc(s_As, p1)
    net.add_arc(s_Aa, p2)
    net.add_arc(s_Aa, p4)
    net.add_arc(s_Sso, p5)
    net.add_arc(s_Ro, p6)
    net.add_arc(s_Ao, p9)
    net.add_arc(s_Aaa1, p10)
    net.add_arc(s_Aaa2, p10)

    net.add_arc(p12, s_As)
    net.add_arc(p13, s_Aa)
    net.add_arc(p14, s_Sso)
    net.add_arc(p15, s_Ro)
    net.add_arc(p16, s_Ao)
    net.add_arc(p17, s_Aaa1)
    net.add_arc(p18, s_Aaa2)

    net.add_arc(s_As, p13)
    net.add_arc(s_Aa, p14)
    net.add_arc(s_Sso, p15)
    net.add_arc(s_Ro, p16)
    net.add_arc(s_Ao, p17)
    net.add_arc(s_Aaa1, p18)
    net.add_arc(s_Aaa2, p19)

    # initial marking
    init_marking = petri.Marking([p0, p12])
    final_marking = petri.Marking([p11, p19])

    apn = petri.AcceptingPetrinet(net, init_marking, {final_marking})

    return apn

def test_trace_to_trace_net(trace_l3, trace_net_l3):
    caseid = trace_l3[podspy.log.CASEID].values[0]
    apn = alignment.to_trace_net(caseid, trace_l3[podspy.log.ACTIVITY])

    try:
        petri.testing.assert_petrinet_equal(apn.net, trace_net_l3.net, check_label=True,
                                            check_id=False, check_local_id=False,
                                            check_graph=False, check_attr=False)
    except AssertionError:
        pytest.fail('Petrinets should be equal')

    # verify markings
    assert len(apn.init_marking) == len(trace_net_l3.init_marking)
    assert len(apn.final_markings) == len(trace_net_l3.final_markings)


def test_to_sync_net_prod(model_cc_book, trace_cc_book, tran_ev_mapping_cc_book, snp_cc_book):
    caseid = trace_cc_book[podspy.log.CASEID].values[0]
    events = trace_cc_book[podspy.log.ACTIVITY]
    place_labeller = alignment.utils.label_generator(start_index=12)
    trace_apn = alignment.to_trace_net(caseid, events, place_labeller)

    snp = podspy.conformance.alignment.to_sync_net_product(caseid, trace_apn,
                                               model_cc_book, tran_ev_mapping_cc_book)

    try:
        petri.testing.assert_petrinet_equal(snp.net, snp_cc_book.net, check_label=False,
                                            check_id=False, check_local_id=False,
                                            check_graph=False, check_attr=False)
    except AssertionError:
        pytest.fail('Petrinets should be equal')

    assert len(snp.init_marking) == len(snp_cc_book.init_marking)
    assert len(snp.final_markings) == len(snp_cc_book.final_markings)

    snp_init_marking_place_labels = list(map(lambda p: p.label, snp.init_marking))
    expected_init_marking_place_labels = list(map(lambda p: p.label, snp_cc_book.init_marking))

    snp_final_marking_place_labels = list(map(lambda p: p.label, list(snp.final_markings)[0]))
    expected_final_marking_place_labels = list(map(lambda p: p.label, list(snp_cc_book.final_markings)[0]))

    assert sorted(snp_init_marking_place_labels) == sorted(expected_init_marking_place_labels)
    assert sorted(snp_final_marking_place_labels) == sorted(expected_final_marking_place_labels)
