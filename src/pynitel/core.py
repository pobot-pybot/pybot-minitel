# -*- coding: UTF-8 -*-

""" Core classes for communicating with a Minitel.
"""

import time
import logging

import serial

from .sequences import Protocol, TeleinfoCommand, TextAttribute, GET_POS, VideotexMode
from .identification import DeviceSpecs
from .constants import *

__all__ = ('Minitel', 'Part')

log = logging.getLogger('minitel')
log.addHandler(logging.NullHandler())
log.setLevel(logging.INFO)

log_rx = log.getChild('rx')
log_tx = log.getChild('tx')


def dump(data):
    return ' '.join(c.encode('hex') for c in data)


class Minitel(object):
    """ Represents a Minitel beast.

    .. warning:: tested only with a Philips Minitel 2
    """
    VIDEOTEX, MIXED, TELEINFO = range(3)

    # transition matrix between modes (line=current, col=target)
    _MODE_TRANSITIONS = (
        (TeleinfoCommand.TO_VIDEOTEX, Protocol.MIXED1, Protocol.TELINFO),
        (Protocol.MIXED2, '', Protocol.TELINFO),
        (TeleinfoCommand.TO_VIDEOTEX, '', '')
    )

    # Videotex sub-modes
    # VT_TEXT = 0
    # VT_GRAPHICS = 1

    mode = None
    _in_vt_mode = None
    _vt_graphics = None

    def __init__(self, port=None, baud=4800, debug=False):
        """ The serial port to be used can be either a string such as ``/dev/ttyUSB0``
        or an instance of :py:class:`serial.Serial`. In this case, the port is automatically
        opened if not yet done.

        .. warning:: When providing a port instance, beware to have it initialized
            with even parity and 7 data bytes.

        :param port: serial port identification or serial port instance
        :type port: str or :py:class:`serial.Serial`
        :param int baud: baud rate (default: 4800)
        :param bool debug: if True, communications are traced
        :raises ValueError: if port is not specified.
        :raises TypeError: if the port type is not one of the expected ones
        """
        if not port:
            raise ValueError('port parameter is mandatory')

        self.debug = debug
        if debug:
            log.setLevel(logging.DEBUG)

        self.baud = baud
        self.vtMode = None
        self.fg = self.bg = None
        if isinstance(port, basestring):
            self.portName = port
            self.ser = serial.Serial(port, baud,
                                     parity=serial.PARITY_EVEN,
                                     bytesize=serial.SEVENBITS,
                                     timeout=1)

        elif isinstance(port, serial.Serial):
            if not port.isOpen():
                port.open()
            self.ser = port

        else:
            raise TypeError('port parameter type mismatch')

        # Since we don't know the current speed setting of the Minitel,
        # we test all possible ones until it works in order to be able to
        # communicate with it

        log.debug('communication speed discovery and setting :')

        init_ok = False
        last_attempt = False
        log.debug('- first attempt, supposing Minitel in Videotex')
        while not init_ok:
            for speed in reversed(LinkSpeed.BAUDRATES):
                log.debug('+ trying with baudrate=%d' % speed)
                self.ser.baudrate = speed
                if self.probe():
                    # we found the current operating speed
                    log.debug('+ current speed is %d' % speed)
                    if speed != baud:
                        log.debug('+ changing it to %d' % baud)
                        self.set_speed(baud)
                    else:
                        log.debug('+ already at the requested speed')
                    init_ok = True
                    break

            if last_attempt:
                break

            # check that it worked
            if not init_ok:
                # maybe we are in Teleinfo mode => try switching to Videotex using all possible speeds
                # and re-attempt
                log.debug('* maybe in Teleinfo => switch to Videotex')
                for speed in reversed(LinkSpeed.BAUDRATES):
                    self.ser.baudrate = speed
                    self.send(TeleinfoCommand.TO_VIDEOTEX)
                    time.sleep(0.1)
                    if self.probe():
                        log.debug('- now in Videotex => last attempt')
                        break

                last_attempt = True

        if not init_ok:
            raise ValueError('speed setting failed')

        self.set_mode(self.VIDEOTEX)

    def close(self):
        """ Closes the communication.

        Should be invoked only when the instance is no more needed.
        """
        self.ser.close()

    def send(self, data):
        """ Sends data to the Minitel.

        :param str data: the data to be sent
        """
        if data:
            log_tx.debug(dump(data))
            self.ser.write(data)

    def receive(self, count=1):
        """ Receives a given count of bytes from the Minitel.

        Does not wait for data, but returns whats is currently available.

        :param int count: the expected count of bytes (default: 1)
        :return: the received bytes
        :rtype: str
        """
        data = self.ser.read(count)
        if data:
            log_rx.debug(dump(data))
        return data

    def request(self, command, reply_size):
        """ Sends a request and returns its reply.

        .. warning:: The serial input link is flushed before issuing the request to be sure
            that the returned value will not contain data remaining from previous
            communications. This means that such data will be lost.

        :param str command: the command to be sent
        :param int reply_size: the size of the expected reply
        :return: the reply
        :rtype: str
        """
        if Protocol.is_protocol_command(command) and not self._in_vt_mode:
            raise RuntimeError('protocol commands available in Videotex mode only')

        self.ser.flushInput()
        self.send(command)
        reply = self.ser.read(reply_size)
        log_rx.debug(dump(reply))
        return reply

    def probe(self):
        """ Reads the content of the identification ROM and returns it in a
        decoded form.

        :return: the decoded identification ROM
        :rtype: :py:class:`DeviceSpecs`
        """
        self.ser.flushInput()
        self.send(Protocol.ENQROM)
        data = self.ser.read(Protocol.ROM_SIZE)
        if len(data) != 5 or data[0] != SOH or data[-1] != EOT:
            return None

        maker, model, version = data[1:4]
        return DeviceSpecs(model, maker, version)

    def in_videotex_mode(self):
        """ Tells if we are presently in Videotex mode.

        Tries to probe the device. If it is not in Videotex, the Protocol
        module is not here, and we will get no reply.

        :return: True if in Videotex mode, False otherwise
        """
        return self.probe() is not None

    def get_speeds(self):
        """ Returns the current teleinfo communication speed settings.

        Teleinfo link speeds are symmetrical, so both values should be the same.

        :return: send/received baudrates
        :rtype: tuple
        """
        data = ord(self.request(Protocol.STATUS_SPEED, Protocol.PRO2_LEN)[-1])
        send_speed = LinkSpeed.baudrate((data >> 3) & 7)
        recv_speed = LinkSpeed.baudrate(data & 7)
        return send_speed, recv_speed

    def set_speed(self, speed):
        """ Sets the communication link communication speed.

        Send and receive speeds are set to the same value, since the teleinfo
        link is symmetrical.

        The provided value is automatically interpreted as a speed code or a baudrate if
        it is a valid value for both cases. See :py:class:`LinkSpeed` for details.

        :param int speed: baudrate or speed code
        :raise ValueError: if an invalid speed is provided
        """
        speed_code = LinkSpeed.code(speed)
        prog_value = 0x40 | (speed_code << 3) | speed_code
        self.send(Protocol.PROG + chr(prog_value))
        # let the beast process the command
        time.sleep(0.05)

        self.ser.baudrate = LinkSpeed.baudrate(speed)

    def set_mode(self, mode, force=False):
        """ Sets the Minitel mode.

        :param int mode: the operating mode, selected among ``VIDEOTEX``, ``MIXED`` and ``TELEINFO``
        :param bool force: if True, the command is issued whatever is the current mode
        :raises ValueError: if a wrong mode is passed
        """
        if mode == self.mode and not force:
            return

        try:
            # special case for initial mode setting
            if self.mode is None:
                self.mode = mode
            sequence = self._MODE_TRANSITIONS[self.mode][mode]
            self.send(sequence)

        except KeyError:
            raise ValueError('invalid display mode')

        else:
            self.mode = mode
            self._in_vt_mode = mode == self.VIDEOTEX
            if self._in_vt_mode:
                self.videotex_graphic_mode(False)
                self.activate_echo(False)

    def videotex_graphic_mode(self, activate=True):
        """ Switches Videotex mode between graphics and text
        :param bool activate: True (default) to activate graphics mode
        """
        if self._in_vt_mode:
            if activate != self._vt_graphics:
                self.send(VideotexMode.GRAPHICS if activate else VideotexMode.TEXT)
                self._vt_graphics = activate

    def get_functional_status(self):
        """ Returns the current settings of the modules.

        :return: caps lock state, roll mode, screen width
        :rtype: tuple
        """
        data = ord(self.request(Protocol.STATUS, Protocol.PRO2_LEN)[-1])
        caps_lock = (data & 0x08) == 0
        roll = (data & 0x02) == 1
        width = (40, 80)[data & 0x01]
        return caps_lock, roll, width

    def is_w80(self):
        """ Tells if the screen is currently in 80 chars width.

        :return: is large screen currently active
        :rtype: bool
        """
        if self.mode == self.TELEINFO:
            return True

        data = ord(self.request(Protocol.STATUS, Protocol.PRO2_LEN)[-1])
        return bool(data & 0x01)

    def set_char_size(self, width=1, height=1):
        """ Defines the size (width and height) of the characters in Videotex mode.

        :param int width: character width (1 or 2)
        :param int height: character height (1 or 2)
        :raise ValueError: if not in Videotex mode or in invalid width or height
        """
        if not self._in_vt_mode:
            raise ValueError('not in Videotex mode')
        if width not in [1, 2]:
            raise ValueError('invalid width')
        if height not in [1, 2]:
            raise ValueError('invalid height')

        self.send('\x1b' + chr(0x4c + (height - 1) + (width - 1) * 2))

    def set_text_style(self, blink=None, inverse=None, underscore=None, bright=None):
        """ Sets the attributes for subsequently displayed text.
        """
        self.send(self.text_style_sequence(blink, inverse, underscore, bright))

    def text_style_sequence(self, blink=None, inverse=None, underscore=None, bright=None):
        # will allow us to access the arguments by their names
        args = locals()
        # selects the text attributes sequence table for the current mode
        mode_attributes = TextAttribute.VIDEOTEX if self._in_vt_mode else TextAttribute.TELEINFO
        # build the sequence corresponding to the attributes specified in the call and send it
        return ''.join(
            mode_attributes[attr][value]
            for attr, value in (
                (a, args[a]) for a in mode_attributes if args[a] is not None
            )
        )

    def set_text_normal(self):
        """ Reverts to normal text.
        """
        self.set_text_style(blink=False, inverse=False, underscore=False, bright=False)

    def set_charset(self, num=0):
        """ Activates the charset (i.e. Gn) to be used for subsequent text display.

        :param int num: the charset num (in range [0, 2])
        :raise ValueError: if passed number is out of range
        """
        try:
            self.send((SI, SO, SS2)[num])
        except (IndexError, TypeError):
            raise ValueError('invalid charset num (%s)' % num)

    def clear_screen(self, part=Part.ALL):
        """ Clears (a part of) the screen.

        :param int part: which part should be cleared (among ``PART_xxx`` constants)
        :raise ValueError: if part code is invalid
        """
        self.send(CSI + '%dJ' % Part.check(part))
        time.sleep(0.1)     # needs some time to complete

    def clear_status(self):
        """ Clears the status line
        """
        self.send(US + '\x40\x41' + CAN + '\x0a')

    def clear_all(self):
        """ Clears the whole screen, including the status line.
        """
        self.clear_status()
        self.clear_screen()

    def clear_end_of_screen(self):
        self.clear_screen(part=Part.END)

    def clear_begin_of_screen(self):
        self.clear_screen(part=Part.BEGIN)

    def clear_line(self, part=Part.ALL):
        """ Clears (a part of) the current line.

        :param int part: which part should be cleared (among :py:class:``Part`` pre-defined constants)
        :raise ValueError: if part code is invalid
        """
        self.send(CSI + '%dK' % Part.check(part))

    def clear_end_of_line(self):
        self.clear_line(part=Part.END)

    def clear_begin_of_line(self):
        self.clear_line(part=Part.BEGIN)

    def newline(self):
        """ Sends a newline/carriage return combo. """
        self.send('\n\r')

    def beep(self):
        self.send(BEL)

    def rlinput(self, max_length=40, marker=' ', start_pos=None, initial_value=None):
        """ User input with basic Gnu's readline features
        :param int max_length: max length of the input
        :param str marker: the char to be used as the input area filler
        :param tuple start_pos: input area start position (default: current one)
        :param str initial_value: the value of the input on entry
        :return: the entered value and the key used to terminate the entry
        :rtype: tuple
        """
        initial_value = initial_value or ''
        chars = list(initial_value)
        self.ser.flushInput()

        # define the field starting position
        if start_pos:
            x0, y0 = start_pos
            self.goto_xy(x0, y0)
        else:
            x0, y0 = self.get_cursor_position()

        # display the initial content (if any) and put the cursor after it
        self.send(initial_value.ljust(max_length, marker))
        self.goto_xy(x0 + len(initial_value), y0)

        # handle user typed keys
        while True:
            c = self.receive()
            if c:
                if c == SEP:
                    c = self.receive()
                    if c in (KeyCode.SEND, KeyCode.NEXT, KeyCode.PREV, KeyCode.CONTENT):
                        break
                    elif c == KeyCode.CORRECTION:
                        if chars:
                            del chars[-1]
                            self.send(BS + marker + BS)
                        else:
                            self.beep()
                    elif c == KeyCode.CANCEL:
                        if chars:
                            chars = []
                            self.goto_xy(x0, y0)
                            self.send(marker * max_length)
                            self.goto_xy(x0, y0)
                        else:
                            self.beep()
                    else:
                        self.beep()
                elif '\x20' <= c <= '\x7a':
                    if len(chars) < max_length:
                        chars.append(c)
                        self.send(c)
                    else:
                        self.beep()
                elif c == CR:
                    break
                else:
                    self.beep()

        return ''.join(chars), c

    def input(self, max_length=40, prompt=None, input_start_xy=None, marker=' '):
        """ Get a user input from the Minitel.

        Handles common editing actions, such as backspace and clear input.

        .. warning:: The serial link is flushed before waiting for the input.

        :param int max_length: maximum length of entered text
        :param tuple prompt: optional prompt to display, as a (text, width, x, y) tuple
        :param tuple input_start_xy: x, y coordinates for input area start. If None, use the current position
        :return: the entered value and the key used to terminate the entry
        :rtype: tuple
        """
        if prompt:
            text, prompt_width, prompt_x, prompt_y = prompt
            text = text.ljust(prompt_width)[:prompt_width]
            self.display_text(text, prompt_x, prompt_y)

        if input_start_xy:
            x, y = input_start_xy
            self.goto_xy(x, y)
        else:
            x, y = self.get_cursor_position()

        self.goto_xy(x, y)
        self.show_cursor()
        value, key = self.rlinput(max_length=max_length, marker=marker)
        self.show_cursor(False)
        self.send(' ' * (max_length - len(value)))
        return value, key

    def wait_for_key(self, key_set=(SEP + KeyCode.SEND,), max_wait=None):
        """ Waits for the user to type any key in the provided set.

        :param iterable key_set: the list of the codes of the accepted keys
        :param int max_wait: maximum wait time in seconds (if None, waits indefinitely)
        :return: the hit key, or None if nothing accepted has been typed in the given delay
        """
        special_keys = set((seq[1] for seq in key_set if len(seq) > 1))
        normal_keys = set(key_set) - special_keys

        self.ser.flushInput()
        limit = time.time() + (max_wait if max_wait else float('inf'))
        while time.time() < limit:
            c = self.receive()
            if c:
                if c == SEP:
                    if special_keys:
                        c = self.receive()
                        if c in special_keys:
                            return SEP + c
                        else:
                            self.beep()
                    else:
                        self.beep()
                else:
                    if c in normal_keys:
                        return c
                    else:
                        self.beep()

            # no need to eat CPU cycles since the user will not type at light speed ;)
            time.sleep(0.1)

    def display_text(self, text, x=0, y=0, clear_eol=False, clear_bol=False, charset=0):
        """ Displays a text at a given position of the screen, with various options.

        The ``clear_xxx`` options provide convenient way to clear parts of the target
        line while displaying the text.

        The charset to be used can be customised.

        .. seealso:: :py:meth:`set_charset`

        :param str text: the text to be displayed
        :param int x: horizontal position
        :param int y: vertical position
        :param bool clear_eol: if True the target line is cleared after the end of the displayed text
        :param bool clear_bol: if True the target line is cleared before the start end of the displayed text
        :param int charset: the charset to be used
        """
        self.goto_xy(x, y)
        self.set_charset(charset)
        if clear_bol:
            self.clear_begin_of_line()
        self.send(text)
        if clear_eol:
            self.clear_end_of_line()

    def display_status(self, text, x=0):
        """ Displays a text in the status line.

        :param str text: the text to display
        :param int x: the horizontal position in [0, 39] (default: 0)
        :raise ValueError: if horizontal position is invalid
        """
        if self._in_vt_mode:
            if 0 <= x < 40:
                self.send(US + '\x40' + chr(0x41 + x) + text + '\x0a')
            else:
                raise ValueError('invalid X position (%d)' % x)
        else:
            raise ValueError('not available in current mode')

    def activate_echo(self, activate=True):
        """ Activates or deactivates the local echo
        :param bool activate: True for local echo activation, False otherwise
        """
        if self._in_vt_mode:
            self.send(
                Protocol.PRO3 +
                (Protocol.ON if activate else Protocol.OFF) +
                ModuleCode.SCREEN_IN + ModuleCode.MODEM_OUT
            )
        else:
            raise ValueError('not available in current mode')

    def goto_xy(self, x, y):
        """ Moves the cursor to the given 0 based coordinates.

        :param int x: X (col) position
        :param int y: Y (line) position
        :raise ValueError: if coordinates are outside valid ranges
        """
        if not 0 <= y <= Y_MAX:
            raise ValueError('invalid Y position (%d)' % y)

        if self._in_vt_mode:
            if not 0 <= x < 40:
                raise ValueError('invalid X position (%d)' % x)
            self.send(US + chr(0x41 + y) + chr(0x41 + x))
        else:
            if not 0 <= x < 80:
                raise ValueError('invalid X position (%d)' % x)
            self.send(TeleinfoCommand.CUP % (y, x))

        # seems to need some time to execute
        time.sleep(0.1)

    def cursor_home(self):
        """ Moves the cursor to the top-left corner of the screen.
        """
        self.goto_xy(0, 0)

    def get_cursor_position(self):
        """ Returns the current cursor position.

        :return: X, Y coordinates as a tuple
        :rtype: tuple
        """
        _, y, x = self.request(GET_POS, 3)
        return ord(x) - 65, ord(y) - 65

    def show_cursor(self, on=True):
        """ Sets the visibility of the cursor.

        Ignored if not in Videotex mode.

        :param bool on: True for showing the caret, False to hide it
        """
        if self._in_vt_mode:
            if on:
                self.send('\x11')
            else:
                self.send('\x14')

    def set_colors(self, fg=None, bg=None):
        """ Sets the color of subsequently displayed text.

        The color is translated to a gray level on a monochrome Minitel.

        :param int fg: foreground color (if None, don't change it)
        :param int bg: background color (if None, don't change it)
        :raises: ValueError if color is out of range
        """
        seq = ''
        if fg is not None and fg != self.fg:
            if not 0 <= fg <= 7:
                raise ValueError('Foreground out of range: %d' % fg)

            if self._in_vt_mode:
                seq += ESC + chr(0x40 + fg)
            else:
                seq += TeleinfoCommand.ATTR % +(30 + fg)
            self.fg = fg

        if bg is not None and bg != self.bg:
            if not 0 <= bg <= 7:
                raise ValueError('Background out of range: %d' % bg)

            if self._in_vt_mode:
                seq += ESC + chr(0x50 + bg)
            else:
                seq += TeleinfoCommand.ATTR % (40 + bg)
            self.bg = bg

        if seq:
            self.send(seq)

    def reset(self):
        """ Guess what...
        """
        if self.mode == self.VIDEOTEX:
            self.send(Protocol.PRO1 + Protocol.RESET)
        else:
            self.send(ESC + 'c')

    def flush(self):
        """ Flushes the serial link (output direction).
        """
        self.ser.flush()
