#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual'

import argparse
import inspect
import textwrap
import logging
import time
import os

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname).1s] %(name)s: %(message)s"
)

import pynitel
from pynitel.forms import Form


class NoSuchTestError(Exception):
    pass


class Runner(object):
    @classmethod
    def get_tests_list(cls):
        return (
            (n[5:], m.__doc__.strip().split('\n')[0])
            for n, m in inspect.getmembers(cls, inspect.ismethod)
            if n.startswith('test_')
        )

    def __init__(self, cli_args):
        self._args = cli_args

    def run_test(self, test_name):
        method_name = 'test_' + test_name
        try:
            method = getattr(self, method_name)
        except AttributeError:
            raise NoSuchTestError(test_name)
        else:
            try:
                mt = pynitel.Minitel(port=self._args.port, baud=self._args.baud, debug=self._args.debug)
            except ValueError:
                logging.error('unable to initialize the Minitel. Is it connected and powered ?')
            else:
                mt.show_cursor(False)
                mt.clear_all()
                mt.display_status(mt.text_style_sequence(inverse=True) + "PyNitel demonstration".ljust(40))
                mt.cursor_home()
                try:
                    method(mt)

                finally:
                    mt.clear_all()
                    mt.display_status("I'll be back...")
                    mt.close()

    def test_display_attrs(self, mt):
        """ display attributes test

        :param minitel.Minitel mt: the Minitel instance
        """
        data = (
            ('normal', {}),
            ('blink', {'blink': True}),
            ('inverse', {'inverse': True}),
            (' underscore', {'underscore': True}),
            ('combined', {'blink': True, 'inverse': True}),
            ('back to normal', {}),
        )
        for y, parms in enumerate(data):
            mt.goto_xy(0, y)
            text, attrs = parms
            if attrs:
                mt.set_text_style(**attrs)
            mt.send(text)

        time.sleep(10)

    def test_image(self, mt):
        """ image display test
        """
        mt.clear_screen()
        script_path = os.path.dirname(__file__)
        with file(os.path.join(script_path, 'fixtures/pobot.vt'), 'rb') as fp:
            mt.send(fp.read())
        mt.display_text('ENVOI', 34, 23)
        mt.wait_for_key(max_wait=10)

    def test_input(self, mt):
        """ user input test
        """
        prompt_x, prompt_y = (0, 3)
        input_value = mt.input(max_length=10, prompt=('Enter your name', 20, prompt_x, prompt_y), marker='.')
        greetings_pos = (0, 5)
        if input_value:
            mt.display_text("Hello %s ;)" % input_value, *greetings_pos)
        else:
            mt.display_text("I'm a poor lonesome Minitel :(", *greetings_pos)
        time.sleep(10)

    def test_status_line(self, mt):
        mt.display_status(mt.text_style_sequence(inverse=True) + "I'm in status line".ljust(40))
        mt.display_text("And I'm in normal area")
        time.sleep(10)

    def test_probe(self, mt):
        """ probes device and display settings.

        :param minitel.Minitel mt: the device
        """
        p = mt.probe()
        print(textwrap.dedent("""
        -----------------------------------------------
         ROM content
        -----------------------------------------------
         - maker ............ %s
         - model ............ %s
         - version .......... %s
         - keyboard ......... %s
         - max baud ......... %d
         - 80 cols .......... %s
        -----------------------------------------------
        """).strip() % (
            p.maker,
            p.model_specs.name,
            p.version,
            p.model_specs.kbd_type,
            p.model_specs.baud,
            p.model_specs.w80
        ))

        speed = mt.get_speeds()[0]
        caps_lock, roll, width = mt.get_functional_status()

        print(textwrap.dedent("""
        -----------------------------------------------
         Current settings
        -----------------------------------------------
         - baud ............. %d
         - caps lock ........ %s
         - roll mode ........ %s
         - display width .... %d
        -----------------------------------------------
        """) % (
            speed, caps_lock, roll, width
        ))

    def test_form(self, mt):
        form = Form(mt)
        form.add_prompt(0, 2, 'First name')
        form.add_prompt(0, 4, 'Last name')
        form.add_prompt(30, 23, 'ENVOI')

        form.add_field('fname', 15, 2, 20)
        form.add_field('lname', 15, 4, 20)

        content = form.render_and_input({'fname': 'Eric'})
        print('form content: %s' % content)

    def test_form_dump_def(self, mt):
        form = Form(mt)
        form.add_prompt(0, 2, 'First name')
        form.add_prompt(0, 4, 'Last name')
        form.add_prompt(30, 23, 'ENVOI')

        form.add_field('fname', 15, 2, 20)
        form.add_field('lname', 15, 4, 20)

        print(form.dump_definition())

    def test_form_load_def(self, mt):
        form = Form(mt)
        script_path = os.path.dirname(__file__)
        with file(os.path.join(script_path, 'fixtures/form_def.json'), 'rb') as fp:
            form.load_definition(fp.read())

        content = form.render_and_input()
        print('form content: %s' % content)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'test_name',
        help="the name of the test to be done (use '?' for the list)"
    )
    parser.add_argument(
        '-p', '--port',
        help='device port',
        default='/dev/ttyUSB0'
    )
    parser.add_argument(
        '-b', '--baud',
        help='baud rate',
        type=int,
        choices=(1200, 4800, 9600),
        default=9600
    )
    parser.add_argument(
        '-d', '--debug',
        help='debug flag',
        action='store_true'
    )

    args = parser.parse_args()
    if args.test_name == '?':
        print('Available tests :')
        for name, descr in Runner.get_tests_list():
            print("- %-20s %s" % (name, descr))

    else:
        try:
            Runner(args).run_test(args.test_name)
        except NoSuchTestError as e:
            print('[ERROR] no such test : ' + e.message)
