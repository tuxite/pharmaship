# -*- coding: utf-8 -*-
import matplotlib.colors as mcolors

def fg_color(color):
    """Return the color name to use according to background color.

    Inspired from https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color
    """
    r, g, b = mcolors.to_rgb(color)
    if (r*255*0.299 + g*255*0.587 + b*255*0.114) > 150:
        return "black"
    return "white"

    # # W3C compliant
    # colors = [r, g, b]
    # for c in colors:
    #     # c = c/255.0
    #     if c <= 0.03928:
    #         c = c/12.92
    #     else:
    #         c = ((c + 0.055)/1.055) ** 2.4
    #
    # L = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # if L > 0.179:
    #     return "black"
    # return "white"
