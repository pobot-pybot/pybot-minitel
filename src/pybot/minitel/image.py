# -*- coding: utf-8 -*-

""" This modules provides tools for loading and converting images to Videotex format.

Based on phooky's Minitel code (https://github.com/phooky/Minitel)

Warning:
    It depends on the availability of PIL. If not installed, the class will be
    replaced by a fake one.
"""
__author__ = 'Eric Pascual'

import logging

log = logging.getLogger('minitel').getChild('image')

try:
    import PIL.Image as Image
    import PIL.ImageOps as ImageOps

except ImportError:
    log.error('PIL is not available. VideotexImage class replaced by a dummy.')
    Image = ImageOps = None

# ordering of sub-pixels (x,y) in a block
_sub_pixels = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]

class VideotexImage(object):
    """ Image converter class.
    """
    def __init__(self, image):
        """
        Parameters:
            image (:py:class:`PIL.image`): the image to be converted
        """
        if not Image:
            return

        if not image:
            raise ValueError('image parameter is mandatory and must be a PIL image')

        self._image = image
        self.last_dark = self.last_light = None

    def to_videotex(self, w=80, h=72):
        """ Returns a list of strings, one for each line of characters
        in the converted image.

        The width and height are specified in sub-pixels, and are always rounded
        up to an even number (for x) or a multiple of 3 (for y).

        Parameters:
            w (int): target image width (in sub-pixels)
            h (int): target image height (in sub-pixels)

        Returns:
            list[str]: the Videotex sequence reproducing the image
        """
        if not Image:
            return []

        # tweak w and h to proper values
        w = ((w + 1) / 2) * 2
        h = ((h + 2) / 3) * 3

        # convert image to gray scale and resize
        im = self._image.convert("L")
        im = im.resize((w, h), Image.ANTIALIAS)

        # normalize contrast
        im = ImageOps.autocontrast(im)

        # down to 3-bit
        im = ImageOps.posterize(im, 3)

        # color hack each 6-cell
        for i in range(w / 2):
            for j in range(h / 3):
                self._color_hack(im, i * 2, j * 3)

        # generate codes for videotex
        self.last_dark = self.last_light = -255
        codes = []
        for j in range(h / 3):
            code_line = ''
            for i in range(w / 2):
                code_line += self._generate_code(im, i * 2, j * 3)
            codes.append(code_line)
        return codes

    def _generate_code(self, image, x, y):
        """ Generates display codes for 2x3 block corresponding to a given
        image pixel.
        """
        dark, light = self._find_dark_light(image, x, y)
        v = 0
        for i, j in _sub_pixels:
            v = (v >> 1)
            if image.getpixel((x + i, y + j)) == light:
                v |= (1 << 5)
        c = ''
        if light != self.last_light:
            c += '\x1b' + chr(0x40 + self._convert_color(light))
        if dark != self.last_dark:
            c += '\x1b' + chr(0x50 + self._convert_color(dark))
        c += chr(32 + v)
        self.last_light, self.last_dark = light, dark
        return c

    @staticmethod
    def _find_dark_light(image, x, y):
        """Finds the darkest and lightest values for a 2x3 block"""
        c = []
        for i, j in _sub_pixels:
            c.append(image.getpixel((x + i, y + j)))
        # select the lightest and darkest pixels
        c.sort()
        return c[0], c[-1]

    @staticmethod
    def _color_hack(image, x, y):
        """ Quantizes a 2x3 block to two colors.
        """
        dark, light = VideotexImage._find_dark_light(image, x, y)
        for i, j in _sub_pixels:
            v = image.getpixel((x + i, y + j))
            if v - dark < light - v:
                v = dark
            else:
                v = light
            image.putpixel((x + i, y + j), v)

    @staticmethod
    def _convert_color(value):
        """ Converts a 256-level gray tone to a 3b minitel 1 tone.
        """
        # take the high three bits, and move the lsb to msb
        return (value >> 6) | ((value >> 3) & (1 << 2))
