#---------------------------------------------------------------------------
# Name:        etg/intl.py
# Author:      Robin Dunn
#
# Created:     
# Copyright:   (c) 2011 by Total Control Software
# License:     wxWindows License
#---------------------------------------------------------------------------

import etgtools
import etgtools.tweaker_tools as tools

PACKAGE   = "wx"   
MODULE    = "_core"
NAME      = "intl"   # Base name of the file to generate to for this script
DOCSTRING = ""

# The classes and/or the basename of the Doxygen XML files to be processed by
# this script. 
ITEMS  = [ 'wxLanguageInfo',
           'wxLocale',

           'language_8h.xml',
           ]    
    
#---------------------------------------------------------------------------

def run():
    # Parse the XML file(s) building a collection of Extractor objects
    module = etgtools.ModuleDef(PACKAGE, MODULE, NAME, DOCSTRING)
    etgtools.parseDoxyXML(module, ITEMS)
    
    #-----------------------------------------------------------------
    # Tweak the parsed meta objects in the module object as needed for
    # customizing the generated code and docstrings.
    
    c = module.find('wxLocale')
    assert isinstance(c, etgtools.ClassDef)
    c.addPrivateAssignOp()
    c.addPrivateCopyCtor()
    tools.removeVirtuals(c)

    
    c = module.find('wxLanguageInfo')
    c.find('WinLang').ignore()
    c.find('WinSublang').ignore()
    c.find('GetLCID').ignore()
    
    
    #-----------------------------------------------------------------
    tools.doCommonTweaks(module)
    tools.runGenerators(module)
    
    
#---------------------------------------------------------------------------
if __name__ == '__main__':
    run()

