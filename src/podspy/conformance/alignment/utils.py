#!/usr/bin/env python


def label_generator(prefix='p', start_index=0):
    while True:
        yield '{prefix}{index}'.format(prefix=prefix, index=start_index)
        start_index += 1


def default_snp_transition_namer(model_tran, trace_tran):
    if model_tran is None:
        label = '(>>,{})'.format(trace_tran.label)
    elif trace_tran is None:
        label = '({},>>)'.format(model_tran.label)
    else:
        label = '({},{})'.format(model_tran.label, trace_tran.label)
    return label