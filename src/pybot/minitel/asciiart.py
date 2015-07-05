# -*- coding: utf-8 -*-

""" Simple helper for managing character based images.
"""

__author__ = 'Eric Pascual'

import constants


class AsciiArtImage(object):
    """ A pseudo image, composed of lines of ASCII characters.
    """
    def __init__(self, lines):
        """
        Parameters:
            lines (list of str): the ASCII chars composing the image, organized
                as a list of strings representing the lines of the image
        """
        if not lines:
            raise ValueError('lines parameter is mandatory')

        h = len(lines)
        w = max((len(line) for line in lines))

        self._h, self._w = h, w
        self._lines = lines

    def display(self, mt, x=0, y=0):
        """ Displays the image on a Minitel, at a given position.

        Parameters:
            mt (:py:class:`core.Minitel`): the Minitel instance
            x, y (int): the coordinates of the target area (default: 0, 0)
        """
        if not mt:
            raise ValueError('mt parameter is mandatory')

        clip = mt.get_screen_width() - x
        for line in self._lines:
            mt.goto_xy(x, y)
            mt.send(line[:clip])
            y += 1
            if y > constants.Y_MAX:
                break
