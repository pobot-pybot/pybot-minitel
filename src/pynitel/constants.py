# -*- coding: utf-8 -*-

""" Shared constants.
"""

__author__ = 'Eric Pascual'

# General control codes
ESC = '\x1b'
SOH = '\x01'
EOT = '\x04'
BEL = '\x07'
BS = '\x08'
CR = '\x0d'
SO = '\x0e'
SI = '\x0f'
CAN = '\x18'
SS2 = '\x19'
US = '\x1f'
SEP = '\x13'

CSI = ESC + '['

Y_MAX = 23


class KeyCode(object):
    """ The codes sent by the special keys in **Videotex mode**.
    """
    SEND = ENVOI = '\x41'
    PREV = RETOUR = '\x42'
    REPEAT = REPETITION = '\x43'
    GUIDE = '\x44'
    CANCEL = ANNULATION = '\x45'
    CONTENT = SOMMAIRE = '\x46'
    CORRECTION = '\x47'
    NEXT = SUITE = '\x48'


class ModuleCode(object):
    """ The identifiers of the Minitel software modules.
    """
    SCREEN_IN = '\x58'
    KEYBOARD_IN = '\x59'
    MODEM_IN = '\x5a'
    PERI_INFO_IN = '\x5b'

    SCREEN_OUT = '\x50'
    KEYBOARD_OUT = '\x51'
    MODEM_OUT = '\x52'
    PERI_INFO_OUT = '\x53'


class LinkSpeed(object):
    """ The speed of the "peri-info" serial link.
    """
    CODES = (1, 2, 4, 6, 7)
    BAUDRATES = (75, 300, 1200, 4800, 9600)

    @classmethod
    def baudrate(cls, value):
        if value in cls.BAUDRATES:
            # if already a valid baudrate, return the passed value
            return value

        try:
            return cls.BAUDRATES[cls.CODES.index(value)]
        except ValueError:
            raise ValueError('invalid speed code (%s)' % value)

    @classmethod
    def code(cls, value):
        if value in cls.CODES:
            # if already a valid speed code, return the passed value
            return value

        try:
            return cls.CODES[cls.BAUDRATES.index(value)]
        except ValueError:
            raise ValueError('invalid baudrate (%s)' % value)


class Part(object):
    """ A screen or line part.
    """
    END, BEGIN, ALL = range(3)

    _all = (END, BEGIN, ALL)

    @staticmethod
    def check(part):
        if part not in Part._all:
            raise ValueError('invalid part code (%d)' % part)
        return part

