import typing
from typing import Tuple

def hexToRGB(color: str) -> Tuple[int, int, int]:
    """
    color = The hexadecimal representation of the color, # hash optional.

    returns:
    
        A tuple containing the red, green and blue color information.
    """
    color = color.replace("#", "")
    red = int(color[0:2], 16)
    green = int(color[2:4], 16)
    blue = int(color[4:6], 16)

    return (red, green, blue)