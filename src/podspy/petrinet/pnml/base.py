#!/usr/bin/env python

"""This is the PNML base module.

This module contains base pnml classes.
"""


from abc import ABC, abstractmethod
from lxml import etree

__all__ = [
    'PnmlBaseFactory',
    'PnmlElement',
    'PnmlText'
]


class PnmlBaseFactory:
    @staticmethod
    def create_pnml_text(text=''):
        return PnmlText(text)


class PnmlElement(ABC):
    @abstractmethod
    def __init__(self, tag):
        self.tag = tag

    def add_attrib(self, attrib):
        """Add attributes to pnml element

        :param attrib: attributes to add
        :return: whether if the attributes have been processed
        """
        return False

    def add_text(self, text):
        """Add text to pnml element

        :param text: text to add
        :return: whether if the text has been processed
        """
        return False

    def add_child(self, child):
        """Add child object to pnml element

        :param child: object to be added into this pnml
        :return: whether if the child is processed
        :rtype: bool
        """
        return False

    def protect_special_chars(self, str):
        """Converts special characters in string to protected characters

        :param str: string to protect
        :return: protected string
        """
        if str is None:
            return None
        control_char = lambda c: ord(c) < 32
        not_ascii = lambda c: ord(c) > 126
        is_special = lambda c: c == '<' or c == '&' or c == '>'
        conditions = lambda c: control_char(c) or not_ascii(c) or is_special(c)
        processed = list(map(conditions, str))

        # return original string if string does not have any special characters
        if not any(processed):
            return str

        to_change = zip(processed, str)
        change = lambda pair: '&#' + pair[1] if pair[0] else pair[1]
        protected = map(change, to_change)
        protected = ''.join(protected)

        return protected

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.tag)


class PnmlText(PnmlElement):
    TAG = 'text'

    def __init__(self, text=''):
        super().__init__(PnmlText.TAG)
        self.text = text

    def add_text(self, text):
        """Add text to PnmlText

        :param text: text to add
        :return: whether if text has been added
        """
        super().add_text(text)
        self.text = text
        return True

    def to_lxml(self):
        ele = etree.Element(PnmlText.TAG)
        ele.text = self.text
        return ele

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               self.text)


