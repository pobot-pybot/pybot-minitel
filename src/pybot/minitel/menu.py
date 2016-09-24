#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Eric Pascual'


from forms import Form


class Menu(object):
    """ Displays a menu with choices and handles the user input.

    The input is checked against the list of selectable options, the
    menu staying displayed until a valid one is entered.

    Canceling is possible by using the SOMMAIRE (content) key.
    """
    def __init__(self, mt, title, choices,
                 prompt=None, line_skip=0, margin_top=0, prompt_line=None, addit=None
                 ):
        """
        Parameters:
            mt (:py:class:`Minitel`): the Minitel instance
            title (str or list of str): the menu title, displayed centered on the screen
            choices (list of str): the options
            prompt (str): the prompt displayed with the input field. Default: "Your choice"
            line_skip (int): vertical space between options. Default (0) places options on consecutive lines
            margin_top (int): vertical space before the menu title. Default: 0
            prompt_line (int): line number on which the input prompt is displayed
            addit (list of tuple): additional prompts as a list of (x, y, text) tuples
        """
        if not mt:
            raise ValueError('mt parameter is mandatory')

        if not choices:
            raise ValueError('choices parameter must be an iterable of option labels')

        if len(choices) < 2:
            raise ValueError('choices must contain at least 2 items')

        if isinstance(title, basestring):
            title = [title]

        if not prompt:
            prompt = "Your choice"

        addit = addit or []

        choice_max = len(choices)
        prompt = "%s [1..%d] : " % (prompt, choice_max)
        prompt_text = prompt + ('..' if choice_max > 9 else '.') + " + ENVOI"
        x_prompt = max(0, (40 - len(prompt_text)) / 2)

        form = Form(mt)

        y = margin_top
        for line in title:
            form.add_prompt(0, y, line.center(40))
            y += 1

        choice_lines = ["%2d - %s" % (i + 1, s) for i, s in enumerate(choices)]
        max_len = max(len(s) for s in choice_lines)
        x = max(0, (40 - max_len) / 2)
        y += 1
        y_inc = line_skip + 1
        for line in choice_lines:
            form.add_prompt(x, y, line)
            y += y_inc

        y = prompt_line or y + 1
        form.add_prompt(x_prompt, y, prompt_text)
        form.add_field('choice', x_prompt + len(prompt), y, 1 if choice_max < 10 else 2)

        for addit_prompt in addit:
            form.add_prompt(*addit_prompt)

        self._mt = mt
        self._form = form
        self._choice_max = choice_max

    def get_choice(self, max_wait=None, cancelable=True):
        """ Waits for the user input and returns it.

        The entered value is checked against the number of options, and rejected if not valid.
        Input can be cancelled by using the `SOMMAIRE` key, if not disabled by `cancelable=False`
        parameter.

        Parameters:
            max_wait (int): maximum wait time in seconds for selecting an option (if None, waits indefinitely)
            cancelable (bool); if True, the cancel key (SOMMAIRE) can be used, and the method will exit
            and return None. If False, cancel key use is treated as an invalid choice.
        Returns:
            the option number (starting from 1) or None if input has been canceled
        """
        self._form.render()
        while True:
            content = self._form.input(max_wait=max_wait)
            if content:
                try:
                    choice = int(content['choice'])
                    if not 1 <= choice <= self._choice_max:
                        raise ValueError()
                except ValueError:
                    self._mt.beep()
                else:
                    return choice

            else:
                if cancelable:
                    return None
                else:
                    self._mt.beep()
