#!/usr/bin/env python
# -*- coding: utf8 -*-
#

"""
Data Analysis Highly tailored for Upbl09a 
"""
from __future__ import with_statement, print_function
__authors__ = ["Jérôme Kieffer"]
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20140304"
__status__ = "development"
version = "0.1"
import os, sys, imp
import os.path as op
import logging
logger = logging.getLogger("dahu.factory")
from threading import Semaphore
from .utils import get_workdir, fully_qualified_name

dahu_root = os.path.dirname(os.path.abspath(__file__))

class Factory(object):
    """
    This is a factory, it instanciates a plugin from it name
    """
    registry = {}
    modules = {}
    plugin_dirs = {}  # key: directory name, value=list of modules
    reg_sem = Semaphore()
    def __init__(self, workdir=None, plugin_path=None):
        """
        @param workdir: place were we are allowed to write
        @param plugin_path: places where plugins are ... in addition to the content of DAHU_PATH"
        """
        self._sem = Semaphore()
        self.workdir = workdir or "."
        self.add_directory(os.path.join(dahu_root, "plugins"))
        for directory in (plugin_path or []):
            self.add_directory(directory)
        if "DAHU_PLUGINS" in os.environ:
            for directory in os.environ["DAHU_PATH"].split(os.pathsep):
                self.add_directory(directory)

    def add_directory(self, directory):
        abs_dir = os.path.abspath(directory)
        if not os.path.isdir(directory):
            logger.warning("No such directory: %s" % directory)
            return
        python_files = [ i[:-3] for i in os.listdir(abs_dir)
                       if op.isfile(op.join(abs_dir, i)) and i.endswith(".py")]
        with self._sem:
            self.plugin_dirs[abs_dir] = python_files

    def search_plugin(self, plugin_name):
        """
        Search for a given plugins ...
        starting from the FQN package.class, 
        """
        if "." not in plugin_name:
            logger.error("plugin name have to be fully qualified, here: %s" % plugin_name)
            return
        splitted = plugin_name.split(".")
        module_name = ".".join(splitted[:-1])
        class_name = splitted[-1]

        for dirname, modules in self.plugin_dirs.iteritems():
            if  module_name in modules and module_name not in self.modules:
                print("load %s %s" % (module_name, os.path.join(dirname, module_name + ".py")))
                mod = imp.load_source(module_name, os.path.join(dirname, module_name + ".py"))
                with self.reg_sem:
                    self.modules[module_name] = mod

    def __call__(self, name):
        """
        create a plugin instance from its name
        """
        if name in self.registry:
            return self.registry[name]()
        with self._sem:
            self.search_plugin(name)
        if plugin_name not in self.registry:
            logger.error("Plugin directories have been searched but plugin"
                           " %s was not found" % plugin_name)
        else:
            return self.registry[name]()


    @classmethod
    def register(cls, klass, fqn=None):
        """
        Register a class as a plugin which can be instanciated.
        
        This can be used as a decorator
        
        @plugin_factor.register 
        
        @param klass: class to be registered as a plugin
        @param fqn: fully qualified name 
        @return klass
        """
        if fqn is None:
            fqn = fully_qualified_name(klass)
        with cls.reg_sem:
            cls.registry[fqn] = klass
        return klass


plugin_factory = Factory(get_workdir())
register = plugin_factory.register
