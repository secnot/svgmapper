from numbers import Number
from .transform import (SVGFigure, SVGElement, GroupElement, 
        RectElement, DEFAULT_SVG_DPI)
from .utils import svg_dimensions

DEFAULT_MARGIN_WIDTH = 10
DEFAULT_BORDER_WIDTH = 0.1
DEFAULT_BORDER_COLOR = "blue" #"rgb(255, 0, 0)"



class SVGPart(object):

   
    def __init__(self, svg, width=None, height=None, 
            scaled_width=None, scaled_height=None,
            rotate=False, dpi=DEFAULT_SVG_DPI):
        """
        Uses viewbox to scale original image

        Arguments:
            svg (bytes): svg file content
            width (Number|None): svg image width, or None to extract
                from svg.
            height (Number|None): svg image height, or None to extract
                from svg.
            scaled_width (Number|None): width svg will be scaled
                into, or None to use original width.
            scaled_height (Number|None): height svg will be scaled
                into or None to use original height.
            dpi (Number): dpi used to extract svg dimmensions
        """
        assert(isinstance(dpi, Number))
        assert(isinstance(svg, bytes))

        # Extract svg dimmensions when not provided
        if not width or not height:
            width, height = svg_dimensions(svg, dpi)
        
        self.width, self.height = width, height

        # If no scaled dimensions were provided use original size
        self.scaled_width = scaled_width or self.width
        self.scaled_height = scaled_height or self.height

        self.rotate = rotate

        figure = SVGFigure.fromstring(svg)
        svg = SVGElement([figure], self.scaled_width, self.scaled_height)
        svg.viewbox(0, 0, self.width, self.height)
        self._svg = svg

    @classmethod
    def fromstring(cls, string, **kwargs):
        """
        Create SVGPart from a string

        Arguments:
            svg (bytes): svg content
            width (number|None): svg image new width, None to use original
            height (number|None): svg image new height, None to use original
        """
        return cls(string, **kwargs)

    @classmethod
    def fromfile(cls, filepath, **kwargs):   
        """
        Create SVGPart from a svg file

        Arguments:
            filepath (str): path to svg file
            width (number|None): svg image new width, None to use original
            height (number|None): svg image new height, None to use original
        """
        with open(filepath, 'br') as f:
            string = f.read()

        return cls(string, **kwargs)
    
    def get_size(self):
        return self.width, self.height

    def generate_group(self, margin_width=0, border_width=0, 
            border_color=DEFAULT_BORDER_COLOR):
        """
        Generate svg group ready for placing into surface

        Argumens:
        """
        part_group = GroupElement([self._svg])
        
        # Rotate part when enabled
        if self.rotate:
            part_group.rotate(90.0, x=margin_width, y=margin_width)
            rotation_compensation = self.scaled_height
        else:
            rotation_compensation = 0

        # Move svg to leave space for margins, and to compensate rotation
        if margin_width>0:
            part_group.moveto(margin_width, margin_width-rotation_compensation)
    
        # Add borders to the group when enabled  
        elements = [part_group]
        if border_width > 0:
            rect_width = self.scaled_width+2*margin_width-border_width
            rect_height= self.scaled_height+2*margin_width-border_width
            border_compensation = float(border_width)/2

            if self.rotate:
                rect_width, rect_height = rect_height, rect_width

            elements.append(RectElement(
                border_compensation, border_compensation, 
                rect_width, rect_height, 
                border_width, border_color))

        return GroupElement(elements)



class SVGMapper(object):

    def __init__(self, width, height, dpi=DEFAULT_SVG_DPI):
        """
        Arguments:
            - Width (Number): Surface width in px
            - Height (Number): Surface height in px
            - dpi (Number): dpi used to extract svg dimmensions if
                needed
        """
        self.parts = []
        self.width = width
        self.height = height

        # Border width or 0 for no border
        self.border_width = DEFAULT_BORDER_WIDTH

        # Border color string (e.g. rgb(240, 30, 100) | #6495ED | blue)
        self.border_color = DEFAULT_BORDER_COLOR

        # Margin width
        self.margin_width = DEFAULT_MARGIN_WIDTH
  
        # 
        self.dpi = dpi

    def _fits_inside(self, x, y, width, height, rotate):
        """Returns true if svg fits inside mapping surface for a given
        position.
        
        Arguments:
            x (Number): placement x coordinate
            y (Number): placement y coordinate
            width (Number): SVG width in pixels
            height (Number): SVG height in pixels
            rotate (Bool): True if the SVG has to be rotated 90 degrees

        Returns:
            Bool: True if it fits, false otherwise
        """ 
        if rotate:
            return self._fits_inside(x, y, height, width, False)

        full_width = width+2*self.margin_width
        full_height= height+2*self.margin_width

        return (x+full_width <= self.width and y+full_height <= self.height)
        
    def add_svg_fromstring(self, svg, x, y, width=None, height=None, 
            rotate=False, uid=None):
        """
        Add svg to surface, from a string

        Arguments:
            svg (bytes): File content binary format
            x (positive number): Part x position
            y (positive number): Part y position
            width  (number | None): SVG width (not including margins) or None
                to extract from svg. If the width is different from the
                svg's real width, it will be scaled.
            height (number | None): SVG height (not including margins) or None
                to extract from svg. If the height is different from the
                svg's real height, it will be scaled.
            rotate (bool): Rotate svg 90 degrees in-place
            uid (string|None): User assigned id for the part, or None. It will
                be added to the group containing the svg and its border.
        """
        assert(x>=0 and y>=0)

        svg_width, svg_height = svg_dimensions(svg, self.dpi)
        width = width or svg_width
        height = height or svg_height
        
        assert(width>0 and height>0)

        # Check svg (margins included) fits into the surface.
        if not self._fits_inside(x, y, width, height, rotate):
            raise ValueError("Placement out of bounds")

        # Create part and store
        part = SVGPart.fromstring(svg, width=svg_width, height=svg_height,
                scaled_width=width, scaled_height=height, rotate=rotate,
                dpi=self.dpi)
        self.parts.append((part, x, y, uid))

    def add_svg_fromfile(self, path, x, y, width=None, height=None, 
            rotate=False, uid=None):
        """
        Add svg from local file
        """
        with open(path, 'rb') as thefile:
            content = thefile.read()
        
        return self.add_svg_fromstring(content, x, y, height, width, rotate, uid)
 
    def _place_parts(self, surf):
        """Generate each part group and place them in the surface

        Arguments:
            surf (SVGFigure): Figure where the parts will be placed
        """
        parts = []

        for p in self.parts:
            part, x, y, uid = p
            group = part.generate_group(self.margin_width, self.border_width,
                        self.border_color)

            # Asign part id to the group
            #g = GroupElement(group)
            part_group = group
            if uid:
                part_group.id(str(uid))

            # Move whole group to its final positions
            part_group.moveto(x, y)
            parts.append(part_group)

        surf.append(parts)

    def to_svg(self, path=None):
        """
        Save to svg file

        Arguments:
            path (string|None): Path to output file or None to return
            svg as string.
        """
        width = "{}".format(self.width)
        height = "{}".format(self.height)
        surf = SVGFigure(width, height)
      
        self._place_parts(surf)
       
        if path is not None:
            surf.save(path)
        else:
            return surf.to_str()
