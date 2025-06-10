LIGHT_RED = '#fc5c65'
DARK_RED = "#eb3b5a"
LIGHT_ORANGE = "#fd9644"
DARK_ORANGE = "#fa8231"
LIGHT_YELLOW = "#fed330"
DARK_YELLOW = "#f7b731"
LIGHT_GREEN = "#26de81"
DARK_GREEN = "#20bf6b"
LIGHT_TURQUOISE = "#2bcbba"
DARK_TURQUOISE = "#0fb9b1"
SOFT_LIGHT_BLUE = "#45aaf2"
SOFT_DARK_BLUE = "#2d98da"
LIGHT_BLUE = "#4b7bec"
DARK_BLUE = "#3867d6"
LIGHT_PURPLE = "#a55eea"
DARK_PURPLE = "#8854d0"
LIGHT_SILVER = "#d1d8e0"
DARK_SILVER = "#a5b1c2"
LIGHT_LIVID = "#778ca3"
DARK_LIVID = "#4b6584"
LIGHT_GRAY = "#d9d9d9"
DARK_GRAY = "#454545"

COLORS = {
    'light-red': LIGHT_RED,
    'dark-red': DARK_RED,
    'light-orange': LIGHT_ORANGE,
    'dark-orange': DARK_ORANGE,
    'light-yellow': LIGHT_YELLOW,
    'dark-yellow': DARK_YELLOW,
    'light-green': LIGHT_GREEN,
    'dark-green': DARK_GREEN,
    'light-turquoise': LIGHT_TURQUOISE,
    'dark-turquoise': DARK_TURQUOISE,
    'soft-light_blue': SOFT_LIGHT_BLUE,
    'soft-dark_blue': SOFT_DARK_BLUE,
    'light-blue': LIGHT_BLUE,
    'dark-blue': DARK_BLUE,
    'light-purple': LIGHT_PURPLE,
    'dark-purple': DARK_PURPLE,
    'light-silver': LIGHT_SILVER,
    'dark-silver': DARK_SILVER,
    'light-livid': LIGHT_LIVID,
    'dark-livid': DARK_LIVID,
    'light-gray': LIGHT_GRAY,
    'dark-gray': DARK_GRAY,
}

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple):
    """Convert RGB tuple to hex color"""
    return '#' + ''.join(f'{c:02x}' for c in rgb_tuple)