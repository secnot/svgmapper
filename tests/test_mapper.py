from unittest import TestCase, skip
import os
from svgmapper.mapper import SVGMapper, SVGPart
import svgmapper.transform as tf 



def test_file_path(filename=""):
    basepath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basepath, 'data/', filename)



class SVGPartTest(TestCase):

    def load_svg(self, filename):
        svg_path = test_file_path(filename)
        
        with open(svg_path, 'br') as f :
            svg = f.read()
       
        return svg


    def test_fromstring(self):
        """Test SVGPart creation froms a string"""
        part = SVGPart.fromstring(self.load_svg('dimension.svg'))
        self.assertEqual((800, 600), part.get_size())

    def test_fromfile(self):
        part = SVGPart.fromfile(test_file_path('dimension.svg'))

    def test_rotation(self):
        #TODO: Do some rotations testing
        pass

    def test_scaling(self):
        #TODO: Do some scaling testing
        pass

    def test_margin(self):
        #TODO: Do some margin testing
        pass

    def test_border(self):
        #TODO: Do some border testing
        pass



class SVGMapperTest(TestCase):

    def setUp(self):
        self.mapper = SVGMapper(1000, 1000) 

    def test_add_svg_fromfile(self):
        """Test adding svg to mapper from a file"""
        self.mapper.add_svg_fromfile(test_file_path('map1.svg'), 
                0, 0, uid='shakespeare')
        self.mapper.add_svg_fromfile(test_file_path('map2.svg'),
                500, 500, uid='cervantes')
    
        svg = self.mapper.to_svg()
        self.assertIsInstance(svg, bytes)
        # check circle tag from the files are present in the result
        self.assertTrue(b'circle' in svg)
        # check rect tag used by borders is present
        self.assertTrue(b'rect' in svg)

    def test_add_svg_uid(self):
        """Test uids assigned to a part are added to its group 
        in the resultins svg"""
        self.mapper.add_svg_fromfile(test_file_path('map1.svg'), 
                0, 0, uid='shakespeare')
        self.mapper.add_svg_fromfile(test_file_path('map2.svg'),
                500, 500, uid='cervantes')

        svg = self.mapper.to_svg()
        self.assertTrue(b'cervantes' in svg)
        self.assertTrue(b'shakespeare' in svg)

    def test_disabled_borders(self):
        """Test border can be disabled, and width can"""
        self.mapper.border_width = 0
        self.mapper.border_color = 'violet'
        self.mapper.add_svg_fromfile(test_file_path('map1.svg'), 
                0, 0)
        self.mapper.add_svg_fromfile(test_file_path('map2.svg'),
                500, 500)

        svg = self.mapper.to_svg()
        self.assertFalse(b'rect' in svg)
        self.assertFalse(b'violet' in svg)

    def test_borders_thickness_color(self):
        """Test borders thicknes and color are modified"""
        self.mapper.border_width = 3.569
        self.mapper.border_color = 'darkorange'
        self.mapper.add_svg_fromfile(test_file_path('map1.svg'), 
                0, 0)
        self.mapper.add_svg_fromfile(test_file_path('map2.svg'),
                500, 500)

        svg = self.mapper.to_svg()
        self.assertTrue(b'3.569' in svg)
        self.assertTrue(b'darkorange' in svg)

    def test_margin_width(self):
        """Test margins are used"""
        self.mapper.border_width=0
        self.mapper.margin_width=35.81

        self.mapper.add_svg_fromfile(test_file_path('map1.svg'), 
                0, 0)
        self.mapper.add_svg_fromfile(test_file_path('map2.svg'),
                500, 500)

        svg = self.mapper.to_svg()
        self.assertTrue(b'35.81' in svg)

    def test_invalid_placements(self):
        """Test adding a svg out of surface or too big to be placed"""
        self.mapper.margin_width = 200

        with self.assertRaises(Exception):
            self.mapper.add_svg_fromfile(test_file_path('map1.svg'),
                    0, 0, width=3000, height=100)
        
        with self.assertRaises(Exception):
            self.mapper.add_svg_fromfile(test_file_path('map1.svg'),
                    width=3000, height=100)

    def test_valid_placements(self):
        """Test placements with the same exact dimmensions of the output
        surface can be placed"""
        self.mapper.margin_width = 0

        self.mapper.add_svg_fromfile(test_file_path('map1.svg'), 
                0, 0, width=1000, height=1000)
        svg = self.mapper.to_svg()


    def test_result_svg_dimmensions(self):
        """Test resulting svg has correct dimmensions"""
        mapper = SVGMapper(1222, 4455)
        mapper.add_svg_fromfile(test_file_path('map1.svg'), 
                0, 0)

        svg = mapper.to_svg()
        self.assertTrue(b'width="1222"' in svg)
        self.assertTrue(b'height="4455"' in svg)

    def test_svg_rotation(self):
        """Test svg are rotated when enabled"""
        self.mapper.add_svg_fromfile(test_file_path('map4_rect.svg'), 
                100, 100, rotate=True)
        svg_rotated = self.mapper.to_svg()

        mapper = SVGMapper(1000, 1000) 
        mapper.add_svg_fromfile(test_file_path('map4_rect.svg'), 
                100, 100)
        svg_normal = mapper.to_svg()

        self.assertNotEqual(svg_rotated, svg_normal)

    def test_dpi_conversion(self):
        """Test dpi is used to convert svg dimmensions from in and cm to
        pixels"""
        self.mapper.dpi=110
        self.mapper.add_svg_fromfile(test_file_path('map3_cm.svg'), 0, 0)
        svg = self.mapper.to_svg()
    
        self.assertTrue(b'130' in svg) # 3cm -> 110dpi -> 129.9px
        self.assertTrue(b'260' in svg) # 6cm -> 110dpi -> 259.8px

    def test_save_to_file(self):
        """Test resulting svg are correctly saved to files"""
        filepath = test_file_path('output_test_file_232344.svg')
        
        self.mapper.add_svg_fromfile(test_file_path('map1.svg'), 
                0, 0)

        self.mapper.to_svg(filepath) 
        self.assertTrue(os.path.exists(filepath))

        # Cleanup
        os.remove(filepath)
        self.assertFalse(os.path.exists(filepath))

