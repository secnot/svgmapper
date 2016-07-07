from unittest import TestCase
import os

from svgmapper.utils import svg_dimensions


class SVGDimensionsTest(TestCase):

    def load_svg(self, filename):
        base_path = os.path.dirname(os.path.abspath(__file__))
        svg_path = os.path.join(base_path, 
                'data/', filename)
        
        with open(svg_path, 'br') as f :
            svg = f.read()
        
        return svg

    def test_normal(self):
        svg = self.load_svg('dimension.svg')
        width, height = svg_dimensions(svg)
        self.assertEqual((width, height), (800, 600))

    def test_viewport(self):
        """ """
        svg = self.load_svg('dimension_viewport.svg')
        width, height = svg_dimensions(svg)
        self.assertEqual((width, height), (800, 600))

    def test_no_dimension(self):
        """Test when width and height not present returns 0"""
        svg = self.load_svg('dimension_without.svg')
        width, height = svg_dimensions(svg)
        self.assertEqual((width, height), (0, 0))

    def test_in(self):
        """Test inches are converted to pixels using dpi"""
        svg = self.load_svg('dimension_in.svg')

        # with custom 100 dpi
        width, height = svg_dimensions(svg, dpi=100.0)
        self.assertEqual((width, height), (80000, 60000))

        # default 90 dpi
        width, height = svg_dimensions(svg)
        self.assertEqual((width, height), (72000, 54000))

    def test_cm(self):
        """Tesct cetimeters are converted to pixels using dpi"""
        svg = self.load_svg('dimension_cm.svg')

        # with custom 100 dpi
        width, height = svg_dimensions(svg, dpi=100.0)
        self.assertEqual((width, height), (31496,23622))

        # with default 90 dpi (28346.9, 21259.8)
        width, height = svg_dimensions(svg)
        self.assertEqual((width, height), (28346,21260))

    def test_no_svg(self):
        """Test an invalid svg raises an exception"""
        with self.assertRaises(ValueError):
            width, height = svg_dimensions("nothing to see")
