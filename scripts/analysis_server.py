#!/usr/bin/env python
# coding: utf8
"""

Data analysis Tango device server ... for UPBL09a

"""
__author__ = "Jérôme Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "07/02/2014"
__status__ = "beta"
__docformat__ = 'restructuredtext'
from __future__ import with_statement, print_function
import sys
import logging
logger = logging.getLogger("dahu")

from dahu.server import DahuDSClass, DahuDS

# set loglevel at least at INFO
if logger.getEffectiveLevel() > logging.INFO:
    logger.setLevel(logging.INFO)
try:
    from argparse import ArgumentParser
except:
    from pyFAI.argparse import ArgumentParser
#import h5py
import PyTango

if __name__ == '__main__':
    logger.info("Starting Dahu Tango Device Server")
    description = """Data Analysis Tango device server 
"""
    epilog = """ Provided by the Data analysis unit - ESRF 
        """
    usage = "analysis_server [-d] --ncpu5  tango-options"
    parser = ArgumentParser(description=description, epilog=epilog, add_help=True)
    parser.add_argument("-V", "--version", action='version', version='%(prog)s 0.0')
    parser.add_argument("-d", "--debug", dest="debug", default=False,
                        action="store_true", help="Switch to debug mode ",)
    parser.add_argument("-v", "--verbose", dest="tango_verbose", default=None,
                        help="tango trace level")
    parser.add_argument("-f", "--file", dest="tango_file", default=None,
                        help="tango log filename")
    parser.add_argument("-n", "--nbcpu", dest="nbcpu", type=int,
                  help="Maximum bumber of processing threads to be started", default=None)
    parser.add_argument(dest="tango", nargs="*", help="Tango device server options")
    options = parser.parse_args()

    tangoParam = ["DahuDS"] + options.tango
    if options.tango_verbose:
        tangoParam += ["-v%s" % options.tango_verbose]
    if options.tango_file:
        tangoParam += ["-file=%s" % options.tango_file]

    # Analyse arguments and options
    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Switch logger to debug level")

    try:
        print(tangoParam)
        py = PyTango.Util(tangoParam)
        py.add_TgClass(DahuDSClass, DahuDS, 'DahuDS')
        U = py.instance() #PyTango.Util.instance()
        U.server_init()
        U.server_run()
    except PyTango.DevFailed as err:
        logger.error('PyTango --> Received a DevFailed exception: %s' % err)
        sys.exit(-1)
    except Exception as err:
        logger.error('PyTango --> An unforeseen exception occurred....%s' % err)
        sys.exit(-1)
