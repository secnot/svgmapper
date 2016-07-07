from unittest import TestCase, skip
import os

from svgmapper.transform import *



def test_file_path(filename=""):
    basepath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basepath, 'data/', filename)

def load_svg(filename=''):
    svg_path = test_file_path(filename)
    
    with open(svg_path, 'br') as f :
        svg = f.read()
    
    return svg



class SVGFigureTest(TestCase):

    def test_fromstring(self):
        """Test SVGPart creation froms a string"""
        part = SVGFigure.fromstring(load_svg('dimension.svg'))
        self.assertEqual((800, 600), part.get_size())

    def test_fromfile(self):
        part = SVGFigure.fromfile(test_file_path('dimension.svg'))
        self.assertEqual((800, 600), part.get_size())



