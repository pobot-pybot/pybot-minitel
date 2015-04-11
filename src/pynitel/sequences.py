# -*- coding: utf-8 -*-

""" Minitel command sequences.
"""

__author__ = 'Eric Pascual'

from .constants import ESC, CSI


class Protocol(object):
    """ The commands provided by the protocol module of the Minitel.
    """
    PRO1 = ESC + '\x39'
    PRO2 = ESC + '\x3a'
    PRO3 = ESC + '\x3b'

    PRO1_LEN = 3
    PRO2_LEN = 4
    PRO3_LEN = 5

    DISCONNECT = PRO1 + '\x67'
    CONNECT = PRO1 + '\x68'
    RET1 = PRO1 + '\x6c'
    RET2 = PRO1 + '\x6d'
    OPPOSITION = PRO1 + '\x6f'
    STATUS_TERMINAL = PRO1 + '\x70'
    STATUS = PRO1 + '\x72'
    STATUS_KEYBOARD = PRO1 + '\x72'
    STATUS_SPEED = PRO1 + '\x74'
    STATUS_PROTOCOL = PRO1 + '\x76'
    ENQROM = PRO1 + '\x7b'
    ROM_SIZE = 5
    RESET = PRO1 + '\x7f'

    START = PRO3 + '\x69'
    STOP = PRO3 + '\x6a'
    PROG = PRO2 + '\x6b'

    START_STOP_ROLL = '\x43'
    START_STOP_ERROR_CORRECTION = '\x44'
    START_STOP_CAPS_LOCK = '\x45'

    START_STOP_KEYB_EXT = '\x41'
    START_STOP_KEYB_CURS_CODES = '\x43'

    MODULE_SCREEN = '\x58'
    MODULE_KEYB = '\x59'
    MODULE_MODEM = '\x5a'
    MODULE_PERIINFO = '\x5b'

    OFF = '\x60'
    ON = '\x61'

    TELINFO = PRO2 + '\x31\x7d'
    MIXED1 = PRO2 + '\x32\x7d'  # Videotex to Mixed
    MIXED2 = PRO2 + '\x32\x7e'  # Mixed to Videotex

    @staticmethod
    def is_protocol_command(command):
        return command[:2] in (Protocol.PRO1, Protocol.PRO2, Protocol.PRO3)


class TeleinfoCommand(object):
    CUU = CSI + "%dA"
    CUD = CSI + "%dB"
    CUF = CSI + "%dC"
    CUB = CSI + "%dD"
    CUP = CSI + "%d;%dH"
    ED = CSI + "%dJ"
    EL = CSI + "%dK"
    ICH = CSI + "%d@"
    SM4 = CSI + "4h"
    RM4 = CSI + "4l"
    IL = CSI + "%dL"
    DL = CSI + "%dM"
    DCH = CSI + "%dP"

    ATTR = CSI + "%dm"
    TO_VIDEOTEX = CSI + '\x3f\x7b'


class TextAttribute(object):
    BLINK = 'blink'
    INVERSE = 'inverse'
    UNDERSCORE = 'underscore'
    BRIGHT = 'bright'

    TELEINFO = {
        BLINK: (
            TeleinfoCommand.ATTR % 25,
            TeleinfoCommand.ATTR % 5
        ),
        INVERSE: (
            TeleinfoCommand.ATTR % 27,
            TeleinfoCommand.ATTR % 7
        ),
        UNDERSCORE: (
            TeleinfoCommand.ATTR % 24,
            TeleinfoCommand.ATTR % 4
        ),
        BRIGHT: (
            TeleinfoCommand.ATTR % 22,
            TeleinfoCommand.ATTR % 1
        )
    }
    VIDEOTEX = {
        BLINK: (ESC + '\x49', ESC + '\x48'),
        INVERSE: (ESC + '\x5c', ESC + '\x5d'),
        UNDERSCORE: (ESC + '\x59', ESC + '\x5a')
    }


GET_POS = ESC + '\x61'


class VideotexMode(object):
    """ Rendering modes for Videotex
    """
    GRAPHICS = '\x0e'
    TEXT = '\x0f'
