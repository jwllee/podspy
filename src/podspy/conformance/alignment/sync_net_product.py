#!/usr/bin/env python


import podspy.petrinet as petri
import collections as cols


from podspy.conformance.alignment import utils


__all__ = [
    'to_trace_net',
    'to_sync_net_product'
]


def to_trace_net(name, trace, place_labeller=None):
    """Converts a trace into a trace net

    :param name: name of trace
    :param trace: events of trace
    :param place_labeller: generator function to generate place labels
    :return: trace net
    """
    if place_labeller is None:
        place_labeller = utils.label_generator('p', 0)

    net = petri.PetrinetFactory.new_petrinet(name)

    trans = []
    for activity in trace:
        trans.append(net.add_transition(activity))

    # add places and arcs
    # for a trace of length n, there are n + 1 places and 2n arcs
    src = net.add_place(next(place_labeller))
    from_place = src
    to_place = None
    for i in range(len(trans)):
        to_place = net.add_place(next(place_labeller))
        net.add_arc(from_place, trans[i])
        net.add_arc(trans[i], to_place)
        from_place = to_place

    init_marking = petri.Marking([src])
    final_marking = petri.Marking([to_place])

    return net, init_marking, final_marking


def to_sync_net_product(trace_net, trace_init, trace_final,
                        net, init, final, mapping,
                        label=None, namer=utils.default_snp_transition_namer):
    """Joins a trace net and model net to a synchronous net product

    :param trace_net: trace net
    :param trace_init: initial marking of trace net
    :param trace_final: final marking of trace net
    :param net: model net
    :param init: initial marking of trace net
    :param final: final marking of trace net
    :param mapping: mapping from net transitions to activity names
    :param label: synchronous net product label
    :param namer: function that names different move transitions
    :return: synchronous net product
    """
    assert isinstance(trace_net, petri.Petrinet)
    assert isinstance(net, petri.Petrinet)

    snp_label = label if label else 'snp-{}-{}'.format(trace_net.label, net.label)
    snp = petri.PetrinetFactory.new_petrinet(snp_label)

    tran_map = dict()
    place_map = dict()

    for t in net.transitions:
        tran_map[t] = snp.add_transition(namer(t, None), is_invisible=t.is_invisible)

    for p in net.places:
        place_map[p] = snp.add_place(p.label)

    for a in net.arcs:
        new_src = tran_map[a.src] if isinstance(a.src, petri.Transition) else place_map[a.src]
        new_target = tran_map[a.target] if isinstance(a.target, petri.Transition) else place_map[a.target]
        snp.add_arc(new_src, new_target, a.weight)

    trace_tran_map = cols.defaultdict(list)

    for t in trace_net.transitions:
        tran_map[t] = snp.add_transition(namer(None, t))
        trace_tran_map[t.label].append(t)

    for p in trace_net.places:
        place_map[p] = snp.add_place(p.label)

    for a in trace_net.arcs:
        new_src = tran_map[a.src] if isinstance(a.src, petri.Transition) else place_map[a.src]
        new_target = tran_map[a.target] if isinstance(a.target, petri.Transition) else place_map[a.target]
        snp.add_arc(new_src, new_target, a.weight)

    # create synchronous move transitions
    net_sm_map = cols.defaultdict(list)     # a transition can be mapped to multiple synchronous move transitions
    trace_sm_map = dict()                   # 1 to 1 mapping from event to transition

    for t in net.transitions:
        mapped_val = mapping[t]

        if mapped_val not in trace_tran_map:
            continue

        for tt in trace_tran_map[mapped_val]:
            sm = snp.add_transition(namer(t, tt))
            net_sm_map[t].append(sm)
            trace_sm_map[tt] = sm

    # adding arcs from net
    for a in net.arcs:
        if isinstance(a.src, petri.Transition) and a.src not in net_sm_map:     # no related synchronous move
            continue
        elif isinstance(a.target, petri.Transition) and a.target not in net_sm_map: # same as above
            continue

        if isinstance(a.src, petri.Transition):     # t->p arc
            new_target = place_map[a.target]
            for new_src in net_sm_map[a.src]:       # can be multiple synchronous move transitions
                snp.add_arc(new_src, new_target, a.weight)

        elif isinstance(a.src, petri.Place):
            new_src = place_map[a.src]
            for new_target in net_sm_map[a.target]:
                snp.add_arc(new_src, new_target, a.weight)

    # adding arcs from trace net
    for a in trace_net.arcs:
        if isinstance(a.src, petri.Transition):
            new_src = trace_sm_map[a.src]
            new_target = place_map[a.target]
            snp.add_arc(new_src, new_target, a.weight)

        elif isinstance(a.src, petri.Place):
            new_src = place_map[a.src]
            new_target = trace_sm_map[a.target]
            snp.add_arc(new_src, new_target, a.weight)

    # initial and final markings
    init_marking_list = []
    final_marking_list = []

    for p in trace_init:
        init_marking_list.append(place_map[p])
    for p in init:
        init_marking_list.append(place_map[p])

    for p in trace_final:
        final_marking_list.append(place_map[p])
    for p in final:
        final_marking_list.append(place_map[p])

    init_marking = petri.Marking(init_marking_list)
    final_marking = petri.Marking(final_marking_list)

    return snp, init_marking, final_marking
