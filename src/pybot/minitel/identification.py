# -*- coding: utf-8 -*-

""" Minitel types and models identification.
"""

__author__ = 'Eric Pascual'

from collections import namedtuple

ModelSpecs = namedtuple('ModelSpecs', 'name can_swap kbd_type baud w80 chars')

MODELS_SPECS = {
    'b': ModelSpecs('Minitel 1', False, 'ABCD', 1200, False, False),
    'c': ModelSpecs('Minitel 1', False, 'Azerty', 1200, False, False),
    'd': ModelSpecs('Minitel 10', False, 'Azerty', 1200, False, False),
    'e': ModelSpecs('Minitel 1 Color', False, 'Azerty', 1200, False, False),
    'f': ModelSpecs('Minitel 10', True, 'Azerty', 1200, False, False),
    'g': ModelSpecs('Emul', True, 'Azerty', 9600, True, True),
    'j': ModelSpecs('Printer', False, None, 1200, False, False),
    'r': ModelSpecs('Minitel 1', True, 'Azerty', 1200, False, False),
    's': ModelSpecs('Minitel 1 Color', True, 'Azerty', 1200, False, False),
    't': ModelSpecs('Terminatel 252', False, None, 1200, False, False),
    'u': ModelSpecs('Minitel 1B', True, 'Azerty', 4800, True, False),
    'v': ModelSpecs('Minitel 2', True, 'Azerty', 9600, True, True),
    'w': ModelSpecs('Minitel 10B', True, 'Azerty', 4800, True, False),
    'y': ModelSpecs('Minitel 5', True, 'Azerty', 9600, True, True),
    'z': ModelSpecs('Minitel 12', True, 'Azerty', 9600, True, True),
    '?': ModelSpecs('Unknown model', False, 'ABCD', 1200, False, False)
}

MAKERS = {
    'A': 'Matra',
    'B': 'RTIC',
    'C': 'Telic-Alcatel',
    'D': 'Thomson',
    'E': 'CCS',
    'F': 'Fiet',
    'G': 'Fime',
    'H': 'Unitel',
    'I': 'Option',
    'J': 'Bull',
    'K': 'Télématique',
    'L': 'Desmet',
    'p': 'Philips',
    'tm': 'Telic-Matra'
}


class DeviceSpecs(object):
    """ Specifications of a given model.

    This class is a data holder for identification and capabilities of a model.
    Instances are created with the content of the device identification data
    as stored in ROM, which are decoded to provide a more human friendly version.

    The decoded information are available in the following attributes :

        - ``maker``
        - ``version``
        - ``model_specs``

    .. seealso:: :py:class:`ModelSpecs` definition to know what is included in the
        model technical specifications
    """
    model_specs = MODELS_SPECS['?']
    maker = None
    version = None

    def __init__(self, model, maker, version):
        """
        :param str model: model code as stored in ROM
        :param str maker: maker code as stored in ROM
        :param str version: version as stored in ROM
        """
        # patch some quirks
        if maker == 'B' and model == 'v':
            maker = 'p'
        elif maker == 'C':
            if version in ('4', '5', ';', '<'):
                maker = 'tm'

        self.model_specs = MODELS_SPECS[model]
        self.maker = MAKERS[maker]
        self.version = version

    def __repr__(self):
        return "DeviceSpecs(maker='%s', model_specs=%s, version='%s')" % (self.maker, self.model_specs, self.version)