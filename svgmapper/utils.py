from gi.repository import Rsvg
import re


DIMENSIONS_ERROR_MSG = 'Invalid svg unable to extract svg dimensions'

def svg_dimensions(svg, dpi=90.0):
    """
    extract svg dimensions using rsvg library

    See librsvg documentation
        https://wiki.gnome.org/action/show/Projects/LibRsvg
        https://developer.gnome.org/rsvg/stable/
        https://lazka.github.io/pgi-docs/Rsvg-2.0/classes/Handle.html

    Arguments:
        svg(string|bytes): String containig svg file
        dpi(float): dpi used for unit conversion to px

    Returns:
        (int, int): svg width and height in px
    """
    try:
        handle = Rsvg.Handle()
        if isinstance(svg, str):
            svg = svg.encode('utf8')
        svg = handle.new_from_data(svg)
        svg.set_dpi(float(dpi))
        dim = svg.get_dimensions()
        return dim.width, dim.height
    except Exception:
        raise ValueError(DIMENSIONS_ERROR_MSG)


def to_num(s):
    """
    Convert number string to int or float as needed

    Arguments:
        s (string): string containing number

    Returns:
        int|float
    """
    try:
        return int(s)
    except ValueError:
        return float(s)


