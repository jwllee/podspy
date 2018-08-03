#!/usr/bin/env python

"""This is the unit test module.

This module tests the log io module.
"""


from podspy.log import io
import pytest
from lxml import etree


__author__ = "Wai Lam Jonathan Lee"
__email__ = "walee@uc.cl"



@pytest.fixture(ids=lambda s: s[1], params=[
    ('<classifier name="Operation" keys="Operation"/>', 'Operation', ['Operation'], dict()),
    ('<classifier name="Service Type" keys="Service Type"/>', 'Service Type', ['Service Type'], dict()),
    ('<classifier name="activity classifier" keys="Operation Service Type"/>',
     'activity classifier', ['Operation', 'Service Type'],
     {'Operation': ['Operation'], 'Service Type': ['Service Type']})
])
def classifier_elem(request):
    # need to convert it as etree element
    return etree.fromstring(request.param[0]), request.param[1], request.param[2], request.param[3]


def test_check_classifier_elem_fixture(classifier_elem):
    assert classifier_elem is not None


def test_parse_classifier_elem(classifier_elem):
    existing_clf_dict = classifier_elem[3]
    d = io.parse_classifier_elem(classifier_elem[0], existing_clf_dict)

    expected_name = classifier_elem[1]
    expected_clf_keys = classifier_elem[2]

    assert expected_name in d
    assert d[expected_name] == expected_clf_keys


