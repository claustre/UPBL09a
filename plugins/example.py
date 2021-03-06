#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Example of plugins made from functions 
"""

from __future__ import with_statement, print_function
__authors__ = ["Jérôme Kieffer"]
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20140319"
__status__ = "development"
version = "0.1"

import os
import numpy
from dahu.plugin import plugin_from_function
import logging
logger = logging.getLogger("plugin.pyFAI")

def square(x):
    return x * x

plugin_from_function(square)
