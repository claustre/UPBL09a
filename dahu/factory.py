#!/usr/bin/env python
# -*- coding: utf8 -*-
#

"""
Data Analysis Highly tailored for Upbl09a 
"""
__authors__ = ["Jérôme Kieffer"]
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20140304"
__status__ = "development"
version = "0.1"
from __future__ import with_statement, print_function
import os, sys
import logging
logger = logging.getLogger("dahu.factory")
from threading import Semaphore
from .utils import get_workdir 
dahu_root = os.path.dirname(os.path.abspath(__file__))
            

def fully_qualified_name(obj):
    """
    Return the fully qualified name of an object
    
    @param obj: any python object
    @return: the full name as a string
    """
    if "__module__" not in dir(obj) or "__name__" not in dir(obj):
        obj = obj.__class__    
    module =   obj.__module__
    name =  obj.__name__
    return module+"."+name

class Factory(object):
    """
    This is a factory, it instanciates a plugin from it name
    """
    REGISTRY = {}
    reg_sem = Semaphore()
    def __init__(self, workdir=None, plugin_path=None):
        """
        @param workdir: place were we are allowed to write
        @param plugin_path: places where plugins are ... in addition to the content of DAHU_PLUGINS"
        """
        self._sem = Semaphore()
        self.workdir = workdir or "."
        self.plugin_dirs = {} #key: directory name, value=list of modules
        self.add_directory(os.path.join(dahu_root, "plugins"))
        for directory in (plugin_path or []):
             self.add_directory(directory)
        if "DAHU_PLUGINS" in os.environ:
            for directory in os.environ["DAHU_PLUGINS"].split(os.pathsep):
                self.add_directory(directory)
        
    def add_directory(self, dirname):
        abs_dir = os.path.abspath(directory)
        if not os.path.isdir(dirname):
            logger.warning("No such directory: %s"%directory)
            return
        python_files = [ i for i in os.listdir(abs_dir) if i.endswith(".py")]
        with self._sem:
            self.plugin_dirs[abs_dir] = python_files
            
    def search_plugins(self, directory=None):
        """
        Search for all plugins into this directory
        """
        if not directory:
            dahu_root = os.path.dirname(os.path.abspath(__file__))
            directory = os.path.join(dahu_root, "plugins")
        if directory not in sys.path:
            sys.path.insert(0,directory)
        if os.path.isdir(directory):
            py_files = [os.path.join(directory,afile) 
                        for afile in os.listdir(directory)
                        if os.path.isfile(afile) and \
                        afile.endswith(".py")]
            for mod_file in py_files:
                try:
                    module = __import__(py_files)
                except ImportError:
                    pass
                else:
                    pass
                    
##TODO

    def __call__(self, name):
        """
        create a plugin instance from its name
        """
        if name in self.REGISTRY:
            return self.REGISTRY[name]()
        with self._sem:
            # TODO:
            if "." in name:
                splitted = name.split(".")
                module_name = ".".join(splitted[:-1])
                class_name = splitted[-1]
            else:
                logger.error("plugin name have to be fully qualified")
                module_name = "dahu.plugins"
                class_name = name
            if module_name in sys.modules:
                module = sys.modules[module_name]
            else:
                module = __import__(module_name)
            assert module_name.startswith(module.__name__)
            remaining = module_name[len(module.__name__)+1:]
            if remaining:
                module =  module.__getattribute__(remaining)
            klass = module.__dict__[ class_name ]
            assert klass.IS_DAHU_PLUGIN
            with self.reg_sem:
                self.REGISTRY[name] = klass
        return self.REGISTRY[name]()

    @classmethod
    def register(cls, klass):
        """
        Register a class as a plugin which can be instanciated.
        
        This can be used as a decorator
        
        @plugin_factor.register 
        
        @param klass
        @return klass
        """
        fqn = fully_qualified_name(klass)
        with cls.reg_sem:
            cls.REGISTRY[fqn] = klass
        return klass
    
        
plugin_factory = Factory(get_workdir()) 
