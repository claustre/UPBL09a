#!/usr/bin/env python
# -*- coding: utf8 -*-
#
from __future__ import with_statement, print_function

__doc__ = """
Data Analysis Highly tailored fror Upbl09a 
"""
__authors__ = ["Jérôme Kieffer"]
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20140318"
__status__ = "development"
version = "0.1"
from .factory import register, plugin_factory
from .utils import fully_qualified_name
import os

class Plugin(object):
    """
    A plugin is instanciated
    
    * Gets its input parameters as a dictionary from the setup method
    * Performs some work in the process
    * Sets the result as output attribute, should be a dictionary
    * The process can be an infinite loop or a server which can be aborted using the abort method 
    
    """
    DEFAULT_SET_UP = "setup"  # name of the method used to set-up the plugin (close connection, files)
    DEFAULT_PROCESS = "process"  # specify how to run the default processing
    DEFAULT_TEAR_DOWN = "teardown"  # name of the method used to tear-down the plugin (close connection, files)
    DEFAULT_ABORT = "abort"  # name of the method used to abort the plugin (if any. Tear_Down will be called)

    def __init__(self):
        """         
        We assume an empty constructor
        """
        self.input = None
        self.output = {}
        self._logging = []  # stores the logging information to send back
        self.is_aborted = False

    def get_name(self):
        return self.__class__.__name__

    def setup(self, kwargs=None):
        """
        This is the second constructor to setup 
        input variables and possibly initialize
        some objects 
        """
        self.input = kwargs

    def process(self, kargs=None):
        """
        main processing of the plugin
        """
        pass

    def teardown(self):
        """
        method used to tear-down the plugin (close connection, files)
        """
        self.output["logging"] = self._logging

    def get_info(self):
        """
        """
        return os.linesep.join(self._logging)

    def abort(self):
        """
        Method called to stop a server process
        """
        self.is_aborted = True


class PluginFromFunction(Plugin):
    """
    Template class to build  a plugin from a function
    """
    def __init__(self):
        """
        @param funct: function to be wrapped  
        """
        Plugin.__init__(self)

    def __call__(self, **kwargs):
        """
        Behaves like a normal function: for debugging 
        """
        self.setup(kwargs)
        self.process()
#        self.teardown()
        return self.output

    def process(self):
        self.output = self.function(**self.input)


def plugin_from_function(function):
    """
    Create a plugin class from a given function and registers it into the 
    
    @param function: any function 
    @return: plugin name to be used by the plugin_factory to get an instance
    """
    class_name = function.__module__ + "." + function.__name__
    klass = type(class_name, (PluginFromFunction,),
                 {'function' : staticmethod(function)})
    register(klass, class_name)
    return class_name


if __name__ == "__main__":
    # here I should explain how to run the plugin as stand alone:
    p = Plugin()
    p.setup()
    p.process()
    p.teardown()

    # second example: create a plugin from a function:
    def square(a):
        return a * a
    plugin_name = plugin_from_function(square)
    print(plugin_name)

    # here is how to get a plugin instance from the
    plugin = plugin_factory(plugin_name)
    #plugin from functions are callable:
    print(plugin(a=5))


