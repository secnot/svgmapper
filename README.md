## Introduction

SVGMapper is a library for composing SVG graphics by mixing several SVG, 
it allows setting placement points, rotations, scaling, and addition of 
margins and borders around them.

## Usage

```python
from svgmapper import SVGMapper

#1 Create a new mapper by suplying its dimmension in pixels
width, height = 1000, 1000
mapper = SVGMapper(width, height)

#2 Modify margin and border options before adding any svg, note
# that the border is placed inside the margin, if it is enabled
# and no margin is set, it will overlap the svg. Than can be 
# importat with thick borders
# (to disable border and margin just set their values to 0)
mapper.margin_width = 10 # in pixels
mapper.border_width = 10 # in pixels
mapper.border_color = 'rgb(255, 0, 0)'

#3 Add all svg into the desired position, from a file or a string
mapper.add_svg_fromfile('path/to/file', 0, 2) # x=0, y=2

svg_str=b'<svg>....</svg>'
mapper.add_svg_fromstring(svg_str, 100, 130) # x=100, y=130

#4 You can also scale the svg by providing a width or height different
# than the indicated in the svg file
mapper.add_svg_fromfile('/another/file', 400, 400, width=300, height=450)

#5 To rotate a svg 90 degrees (only angle supported sorry), use rotate
# parameter
mapper.add_svg_fromfile('/file/to/rotate', 200, 200, rotate=True)

#6 Optionally provide an identification with the svg that will be 
# added to the group containg the svg it in the result as an 'id'
# attribute
mapper.add_svg_fromfile('/path/to/last/file', 800, 100, uid='svgid')

#7 Output the constructed svg
svg = mapper.to_svg()

# Or directly to a file
mapper.to_svg('path/to/output/file')
```

