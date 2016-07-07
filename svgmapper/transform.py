from lxml import etree
from copy import deepcopy
import re

from .utils import to_num

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SVG = "{%s}" % SVG_NAMESPACE
NSMAP = {None : SVG_NAMESPACE}
DEFAULT_SVG_DPI = 90.0

class FigureElement(object):

    def __init__(self, xml_element, defs=None):
        self.root = xml_element

    def moveto(self, x, y):
        self.root.set("transform", "%s translate(%s, %s)" %
                (self.root.get("transform") or '', x,y))

    def rotate(self, angle, x=0, y=0):
        self.root.set("transform", "%s rotate(%f %f %f)" %
                (self.root.get("transform") or '', angle,x, y))

    def scale(self, swidth, sheight=None):
        if sheight is None:
            self.root.set("transform", "%s scale(%s)" %
                (self.root.get("transform") or '', swidth))
        else:
            self.root.set("transform", "%s scale(%s %s)" %
                (self.root.get("transform") or '', swidth, sheight))

    def viewbox(self, min_x, min_y, width, height):
        self.root.set("viewBox", "%s %s %s %s" %
                (min_x, min_y, width, height))

    def id(self, id_str):
        self.root.set("id", id_str)

    def __getitem__(self, i):
        return FigureElement(self.root.getchildren()[i])

    def copy(self):
        return deepcopy(self.root)

    def tostr(self):
        return etree.tostring(self.root, pretty_print=True)


class TextElement(FigureElement):
    def __init__(self, x, y, text, size=8, font="Verdana",
            weight="normal", letterspacing=0, anchor='start'):
        txt = etree.Element(SVG+"text", {"x": str(x), "y": str(y),
            "font-size":str(size), "font-family": font,
            "font-weight": weight, "letter-spacing": str(letterspacing),
            "text-anchor": str(anchor)})
        txt.text = text
        FigureElement.__init__(self, txt)

class LineElement(FigureElement):
    def __init__(self, points, width=1, color='black'):
        linedata = "M{} {} ".format(*points[0])
        linedata += " ".join(map(lambda x: "L{} {}".format(*x), points[1:]))
        line = etree.Element(SVG+"path", 
                {"d": linedata, 
                 "stroke-width":str(width),
                 "stroke" : color}) 
        FigureElement.__init__(self, line)

class RectElement(FigureElement):
    def __init__(self, x, y, width, height, stroke_width=1, color='red'):
        style = "stroke:{};stroke-width:{};fill-opacity:0.0;stroke-opacity:1.0"
        style = style.format(color, str(stroke_width))
        rect = etree.Element(SVG+"rect", {"x": str(x), "y": str(y),
            "width": str(width), "height": str(height),
            "style": style,
            })
        FigureElement.__init__(self, rect)

class SVGElement(FigureElement):
    def __init__(self, element_list, width, height):
        svg = etree.Element(SVG+"svg", {"width": str(width), 
            "height": str(height)})
        for e in element_list:
            if isinstance(e, FigureElement):
                svg.append(e.root)
            elif isinstance(e, SVGFigure):
                svg.append(e.root)
            else:
                svg.append(e)
        self.root = svg

class GroupElement(FigureElement):
    def __init__(self, element_list, attrib=None):
        new_group = etree.Element(SVG+"g", attrib=attrib)
        for e in element_list:
            if isinstance(e, FigureElement):
                new_group.append(e.root)
            else:
                new_group.append(e)
        self.root = new_group


class SVGFigure(object):
    def __init__(self, width=None, height=None):
        self.root = etree.Element(SVG+"svg",nsmap=NSMAP)
        self.root.set("version", "1.1")
        if width:
            self.width = width
        if height:
            self.height = height

    @classmethod
    def fromstring(cls, svg, width=None, height=None):
        figure = cls(width=width, height=height)
        figure.root = etree.fromstring(svg)
        return figure

    @classmethod
    def fromfile(cls, filepath, width=None, height=None):
        with open(filepath, 'br') as f:
            content = f.read()
        return cls.fromstring(content, width=width, height=height)

    @property
    def width(self):
        return self.root.get("width")

    @width.setter
    def width(self, value):
        self.root.set('width', value)
        self.root.set("viewbox", "0 0 %s %s" % (self.width, self.height))

    @property
    def height(self):
        return self.root.get("height")

    @height.setter
    def height(self, value):
        self.root.set('height', value)
        self.root.set("viewbox", "0 0 %s %s" % (self.width, self.height))
    
    def append(self, element):
        try:
            self.root.append(element.root)
        except AttributeError:
            self.root.append(GroupElement(element).root)

    def getroot(self):
        if 'class' in self.root.attrib:
            attrib = {'class' : self.root.attrib['class']}
        else:
            attrib = None
        return GroupElement(self.root.getchildren(), attrib=attrib)

    def to_str(self):
        """
        Returns a string of the svg image
        """
        return etree.tostring(self.root, xml_declaration=True,
                standalone=True,pretty_print=True)

    def save(self, fname):
        out=etree.tostring(self.root, xml_declaration=True,
                standalone=True,pretty_print=True)
        fid = open(fname, 'wb')
        fid.write(out)
        fid.close()

    def find_id(self, element_id):
        find = etree.XPath("//*[@id=$id]")
        return FigureElement(find(self.root, id=element_id)[0])

    def get_size(self):
        """Extract svg dimensions using native library

        Returns:
            Tuple (number, number): width, height
        """
        #TODO: Also extract cm, in, em,  etc.....
        try:
            width_str  = self.root.get('width')
            height_str = self.root.get('height')
            width  = re.search("[-+]?\d+[\.]?\d*", width_str)
            height = re.search("[-+]?\d+[\.]?\d*", height_str)
        except Exception:
            raise ValueError('Unable to extract svg dimensions')

        if width is None or height is None:
            raise ValueError('Unable to extract svg dimensions')

        return to_num(width.group(0)), to_num(height.group(0))

    def set_size(self, size):
        w, h = size
        self.root.set('width', w)
        self.root.set('height', h)

