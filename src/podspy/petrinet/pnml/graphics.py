#!/usr/bin/env python

"""This is the pnml graphic module.

This module contains PNML graphic classes.
"""
from podspy.petrinet.pnml.base import PnmlElement
from podspy.utils import attributes as atr
from podspy.utils import layout as lot
from podspy.petrinet.elements import *
from enum import Enum
from lxml import etree


__all__ = [
    'PnmlAnnotationGraphics',
    'PnmlArcGraphics',
    'PnmlDimension',
    'PnmlFill',
    'PnmlFont',
    'PnmlLine',
    'PnmlNodeGraphics',
    'PnmlOffset',
    'PnmlPosition',
    'PnmlGraphicFactory'
]


class PnmlGraphicFactory:
    @staticmethod
    def create_annot_graphics():
        return PnmlAnnotationGraphics()

    @staticmethod
    def ele2annot_graphics(element, layout=None):
        graphics = PnmlAnnotationGraphics()
        graphics.fill = PnmlGraphicFactory.ele2fill(element, layout)
        graphics.line = PnmlGraphicFactory.ele2line(element, layout)
        if graphics.fill or graphics.line:
            graphics.offset = PnmlGraphicFactory.create_offset(0., 0.)
        return graphics

    @staticmethod
    def create_arc_graphics():
        return PnmlArcGraphics()

    @staticmethod
    def ele2arc_graphics(element, layout=None):
        graphic = PnmlArcGraphics()

        position_list = lot.get_edge_points(element, layout)
        for pos in position_list:
            pnml_pos = PnmlGraphicFactory.create_position()
            pnml_pos.x, pnml_pos.y = pos
            graphic.position_list.append(pnml_pos)

        graphic.line = PnmlGraphicFactory.ele2line(element, layout)
        if len(graphic.position_list) > 0 and graphic.line:
            # only give non-empty arc graphics
            return graphic
        return None

    @staticmethod
    def create_dimension():
        return PnmlDimension()

    @staticmethod
    def ele2dimension(element, layout=None):
        dim = PnmlDimension()
        # dimension can be either in node.attribs (from ProM)
        # or node.attr (from pygraphviz), we use ProM if possible
        if atr.SIZE in element.attribs:
            size = element.attribs[atr.SIZE]
        else:
            width = lot.get_width(element, layout, atr.DEF_NODE_WIDTH)
            height = lot.get_width(element, layout, atr.DEF_NODE_HEIGHT)
            size = (width, height)

        dim.x, dim.y = size
        return dim

    @staticmethod
    def create_fill():
        return PnmlFill()

    @staticmethod
    def ele2fill(element, layout=None):
        if atr.FILLCOLOR in element.attribs:
            color = element.attribs[atr.FILLCOLOR]
            if color != '#000000': # no point adding color if it's just black
                fill = PnmlFill()
                fill.color = color
                return fill
        return None

    @staticmethod
    def create_font():
        return PnmlFont()

    @staticmethod
    def create_line():
        return PnmlLine()

    @staticmethod
    def ele2line(element=None, layout=None):
        # todo: implement getting line style from graph element
        return None

    @staticmethod
    def create_node_graphics():
        return PnmlNodeGraphics()

    @staticmethod
    def ele2node_graphics(element, layout=None):
        n_gc = PnmlNodeGraphics()
        n_gc.position = PnmlGraphicFactory.ele2position(element, layout)
        n_gc.fill = PnmlGraphicFactory.ele2fill(element, layout)
        n_gc.line = PnmlGraphicFactory.ele2line(element, layout)
        n_gc.dimension = PnmlGraphicFactory.ele2dimension(element, layout)
        return n_gc

    @staticmethod
    def create_offset(x=None, y=None):
        return PnmlOffset(x, y)

    @staticmethod
    def create_position():
        return PnmlPosition()

    @staticmethod
    def ele2position(element=None, layout=None):
        pnml_pos = PnmlPosition()
        # should be in node.attr (from pygraphviz)
        pos = lot.get_node_pos(element, layout, default=(atr.DEF_NODE_POS_X, atr.DEF_NODE_POS_Y))

        # dimension can be either in node.attribs (from ProM)
        # or node.attr (from pygraphviz), we use ProM if possible
        if atr.SIZE in element.attribs:
            size = element.attribs[atr.SIZE]
        else:
            width = lot.get_width(element, layout, default=atr.DEF_NODE_WIDTH)
            height = lot.get_height(element, layout, default=atr.DEF_NODE_HEIGHT)
            size = (width, height)

        pnml_pos.x = pos[0] + size[0] / 2
        pnml_pos.y = pos[1] + size[1] / 2
        return pnml_pos


class PnmlAnnotationGraphics(PnmlElement):
    TAG = 'graphics'

    def __init__(self):
        super().__init__(PnmlAnnotationGraphics.TAG)
        self.offset = None
        self.font = None
        self.fill = None
        self.line = None

    def add_child(self, child):
        if isinstance(child, PnmlOffset):
            self.offset = child
            added = True
        elif isinstance(child, PnmlFont):
            self.font = child
            added = True
        elif isinstance(child, PnmlFill):
            self.fill = child
            added = True
        elif isinstance(child, PnmlLine):
            self.line = child
            added = True
        else:
            added = super().add_child(child)
        return added

    def to_lxml(self):
        ele = etree.Element(PnmlAnnotationGraphics.TAG)

        if self.offset is not None:
            ele.append(self.offset.to_lxml())

        if self.font is not None:
            ele.append(self.font.to_lxml())

        if self.fill is not None:
            ele.append(self.fill.to_lxml())

        if self.line is not None:
            ele.append(self.line.to_lxml())

        return ele

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__,
                                           self.offset, self.font,
                                           self.fill, self.line)


class PnmlArcGraphics(PnmlElement):
    TAG = 'graphics'

    def __init__(self):
        super().__init__(PnmlArcGraphics.TAG)
        self.position_list = list()
        self.line = None

    def add_child(self, child):
        if isinstance(child, PnmlPosition):
            self.position_list.append(child)
            added = True
        elif isinstance(child, PnmlLine):
            self.line = child
            added = True
        else:
            added = super().add_child(child)
        return added

    def to_lxml(self):
        ele = etree.Element(PnmlArcGraphics.TAG)

        for pnml_pos in self.position_list:
            ele.append(pnml_pos.to_lxml())

        if self.line is not None:
            ele.append(self.line.to_lxml())

        return ele

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.position_list,
                                   self.line)


class PnmlDimension(PnmlElement):
    TAG = 'dimension'

    def __init__(self, x=atr.DEF_NODE_WIDTH, y=atr.DEF_NODE_HEIGHT):
        super().__init__(PnmlDimension.TAG)
        self.x = x
        self.y = y

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        if 'x' in attrib:
            try:
                self.x = PnmlPosition.SCALE * float(attrib['x'])
            except:
                self.x = atr.DEF_NODE_WIDTH
        if 'y' in attrib:
            try:
                self.y = PnmlPosition.SCALE * float(attrib['x'])
            except:
                self.y = atr.DEF_NODE_HEIGHT
        return True

    def convert_to_net(self, element, box):
        if self.x and self.y:
            luc, rbc = box
            # dimension in x and y
            dim = (rbc[0] - luc[0], rbc[1] - luc[1])
            element.attribs[atr.SIZE] = dim

    def to_lxml(self):
        ele = etree.Element(PnmlDimension.TAG)
        ele.attrib['x'] = str(self.x)
        ele.attrib['y'] = str(self.y)
        return ele

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.x, self.y)


class GradientRotation(Enum):
    GRADIENT_ROTATION_DEFAULT = 1
    GRADIENT_ROTATION_VERTICAL = 2
    GRADIENT_ROTATION_HORIZONTAL = 3
    GRADIENT_ROTATION_DIAGONAL = 4


class PnmlFill(PnmlElement):
    TAG = 'fill'

    def __init__(self):
        super().__init__(PnmlFill.TAG)
        self.color = None
        self.gradient_color = None
        self.gradient_rotation = GradientRotation.GRADIENT_ROTATION_DEFAULT
        self.image = None

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        self.color = attrib['color'] if 'color' in attrib else None
        self.gradient_color = attrib['gradient-color'] if 'gradient-color' in attrib else None
        if 'gradient-rotation' in attrib:

            tmp = {
                'vertical': GradientRotation.GRADIENT_ROTATION_VERTICAL,
                'horizontal': GradientRotation.GRADIENT_ROTATION_HORIZONTAL,
                'diagonal': GradientRotation.GRADIENT_ROTATION_DIAGONAL
            }

            rot_type = attrib['gradient-rotation']
            self.gradient_rotation = tmp[rot_type]
        self.image = attrib['image'] if 'image' in attrib else None
        return True

    def convert_to_net(self, element):
        if self.color:
            element.attribs[atr.FILLCOLOR] = self.color

    def to_lxml(self):
        ele = etree.Element(PnmlFill.TAG)
        ele.attrib['color'] = self.color
        return ele

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__,
                                           self.color, self.gradient_color,
                                           self.gradient_rotation, self.image)


class Decoration(Enum):
    DECORATION_DEFAULT = 1
    DECORATION_UNDERLINE = 2
    DECORATION_OVERLINE = 3
    DECORATION_LINETHROUGH = 4


class Align(Enum):
    ALIGN_DEFAULT = 1
    ALIGN_LEFT = 2
    ALIGN_CENTER = 3
    ALIGN_RIGHT = 4


class PnmlFont(PnmlElement):
    TAG = 'font'

    def __init__(self):
        super().__init__(PnmlFont.TAG)
        self.family = None
        self.style = None
        self.weight = None
        self.size = None
        self.decoration = Decoration.DECORATION_DEFAULT
        self.align = Align.ALIGN_DEFAULT
        self.rotation = 0.0

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        self.family = attrib['family'] if 'family' in attrib else None
        self.style = attrib['style'] if 'style' in attrib else None
        self.weight = attrib['weight'] if 'weight' in attrib else None
        self.size = attrib['size'] if 'size' in attrib else None
        if 'decoration' in attrib:
            tmp = {
                'underline': Decoration.DECORATION_UNDERLINE,
                'overline': Decoration.DECORATION_OVERLINE,
                'line-through': Decoration.DECORATION_LINETHROUGH
            }
            deco_type = attrib['decoration']
            self.decoration = tmp[deco_type]
        if 'align' in attrib:
            tmp = {
                'left': Align.ALIGN_LEFT,
                'center': Align.ALIGN_CENTER,
                'right': Align.ALIGN_RIGHT
            }
            align_type = attrib['align']
            self.align = tmp[align_type]
        if 'rotation' in attrib:
            try:
                self.rotation = float(attrib['rotation'])
            except:
                self.rotation = 0.0
        return True

    def __repr__(self):
        return '{}({}, {}, {}, {}, {}, {}, {})'.format(
            self.__class__.__name__,
            self.family, self.style, self.weight, self.size,
            self.decoration, self.align, self.rotation
        )


class Shape(Enum):
    SHAPE_DEFAULT = 1
    SHAPE_LINE = 2
    SHAPE_CURVE = 3


class Style(Enum):
    STYLE_DEFAULT = 1
    STYLE_SOLID = 2
    STYLE_DASH = 3
    STYLE_DOT = 4


class PnmlLine(PnmlElement):
    TAG = 'line'

    def __init__(self):
        super().__init__(PnmlLine.TAG)
        self.shape = Shape.SHAPE_DEFAULT
        self.color = None
        self.width = 1.
        self.style = Style.STYLE_DEFAULT

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        if 'shape' in attrib:
            tmp = {
                'line': Shape.SHAPE_LINE,
                'curve': Shape.SHAPE_CURVE
            }
            shape = attrib['shape']
            self.shape = tmp[shape]
        self.color = attrib['color'] if 'color' in attrib else None
        if 'width' in attrib:
            try:
                self.width = float(attrib['width'])
            except:
                self.width = 1.
        if 'style' in attrib:
            tmp = {
                'solid': Style.STYLE_SOLID,
                'dash': Style.STYLE_DASH,
                'dot': Style.STYLE_DOT
            }
            style = attrib['style']
            self.style = tmp[style]
        return True

    def convert_to_net(self, element):
        if self.shape == Shape.SHAPE_LINE:
            element.attribs[atr.STYLE] = 'orthogonal'
        else:
            element.attribs[atr.STYLE] = 'spline'

        if self.color:
            if isinstance(element, Arc):
                element.attribs[atr.EDGECOLOR] = self.color
            else:
                element.attribs[atr.STROKECOLOR] = self.color

        if self.width:
            element.attribs[atr.LINEWIDTH] = self.width

        if self.style == Style.STYLE_DASH:
            element.attribs[atr.DASHPATTERN] = (3., 3.)
        elif self.style == Style.STYLE_DOT:
            element.attribs[atr.DASHPATTERN] = (1., 3.)
        elif self.style != Style.STYLE_DEFAULT:
            element.attribs[atr.DASHPATTERN] = (1., 0.)

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__,
                                           self.shape, self.color,
                                           self.width, self.style)


class PnmlNodeGraphics(PnmlElement):
    TAG = 'graphics'

    def __init__(self):
        super().__init__(PnmlNodeGraphics.TAG)
        self.position = None
        self.fill = None
        self.line = None
        self.dimension = None

    def add_child(self, child):
        if isinstance(child, PnmlPosition):
            self.position = child
            added = True
        elif isinstance(child, PnmlDimension):
            self.dimension = child
            added = True
        elif isinstance(child, PnmlFill):
            self.fill = child
            added = True
        elif isinstance(child, PnmlLine):
            self.line = child
            added = True
        else:
            added = super().add_child(child)
        return added

    def get_box(self):
        position_x = self.position.x if self.position else atr.DEF_NODE_POS_X
        position_y = self.position.y if self.position else atr.DEF_NODE_POS_Y
        dimension_x = self.dimension.x if self.dimension else atr.DEF_NODE_WIDTH
        dimension_y = self.dimension.y if self.dimension else atr.DEF_NODE_HEIGHT

        luc_x = (position_x - dimension_x) / 2
        luc_y = (position_y - dimension_y) / 2
        rbc_x = (position_x + dimension_x) / 2
        rbc_y = (position_y + dimension_y) / 2

        luc = (luc_x, luc_y)
        rbc = (rbc_x, rbc_y)

        return luc, rbc

    def convert_to_net(self, element):
        box = self.get_box()
        if self.position:
            self.position.convert_to_net(element)
        if self.fill:
            self.fill.convert_to_net(element)
        if self.line:
            self.line.convert_to_net(element)
        if self.dimension:
            self.dimension.convert_to_net(element, box)

    def to_lxml(self):
        ele = etree.Element(PnmlNodeGraphics.TAG)

        if self.position is not None:
            ele.append(self.position.to_lxml())

        if self.fill is not None:
            ele.append(self.fill.to_lxml())

        if self.dimension is not None:
            ele.append(self.dimension.to_lxml())

        return ele

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__,
                                           self.position, self.fill,
                                           self.line, self.dimension)


class PnmlOffset(PnmlElement):
    TAG = 'offset'

    def __init__(self, x=None, y=None):
        super().__init__(PnmlOffset.TAG)
        self.x = x
        self.y = y

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        if 'x' in attrib:
            try:
                self.x = PnmlPosition.SCALE * float(attrib['x'])
            except:
                self.x = None
        if 'y' in attrib:
            try:
                self.y = PnmlPosition.SCALE * float(attrib['y'])
            except:
                self.y = None
        return True

    def to_lxml(self):
        ele = etree.Element(PnmlOffset.TAG)
        ele.attrib['x'] = str(self.x)
        ele.attrib['y'] = str(self.y)
        return ele

    def __repr__(self):
        return '{}({}, {}'.format(self.__class__.__name__,
                                           self.x, self.y)


class PnmlPosition(PnmlElement):
    TAG = 'position'
    SCALE = 2.0

    def __init__(self, x=0., y=0.):
        super().__init__(PnmlPosition.TAG)
        self.x = x
        self.y = y

    def add_attrib(self, attrib):
        super().add_attrib(attrib)
        if 'x' in attrib:
            try:
                self.x = PnmlPosition.SCALE * float(attrib['x'])
            except:
                self.x = 0.
        if 'y' in attrib:
            try:
                self.y = PnmlPosition.SCALE * float(attrib['y'])
            except:
                self.y = 0.
        return True

    def convert_to_net(self, element):
        # TO REMOVE:
        # Since graphviz is used for layout, no need to set layout position of
        # the element.
        pass

    def to_lxml(self):
        ele = etree.Element(PnmlPosition.TAG)
        ele.attrib['x'] = str(self.x)
        ele.attrib['y'] = str(self.y)
        return ele

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__,
                                   self.x, self.y)


