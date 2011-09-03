#---------------------------------------------------------------------------
# Name:        etg/font.py
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
NAME      = "font"   # Base name of the file to generate to for this script
DOCSTRING = ""

# The classes and/or the basename of the Doxygen XML files to be processed by
# this script. 
ITEMS  = [  'wxFont',
            'wxFontMetrics',
           ]    
    
#---------------------------------------------------------------------------

def run():
    # Parse the XML file(s) building a collection of Extractor objects
    module = etgtools.ModuleDef(PACKAGE, MODULE, NAME, DOCSTRING)
    etgtools.parseDoxyXML(module, ITEMS)
    
    #-----------------------------------------------------------------
    # Tweak the parsed meta objects in the module object as needed for
    # customizing the generated code and docstrings.


    # TODOs
    module.find('wxTheFontList').ignore()
    module.find('wxNORMAL_FONT').ignore()
    module.find('wxSMALL_FONT').ignore()
    module.find('wxITALIC_FONT').ignore()
    module.find('wxSWISS_FONT').ignore()
    
    
    c = module.find('wxFont')
    assert isinstance(c, etgtools.ClassDef)
    tools.removeVirtuals(c)
    
    # TODO: Since the TypeCode is inserted before the derived class
    # (sipwxFont) is defined, we can't use the new version of addCppCtor. Can
    # this be fixed?
    c.addCppCtor_sip("""(
        int pointSize,
        wxFontFamily family,
        int flags = wxFONTFLAG_DEFAULT,
        const wxString& faceName = wxEmptyString,
        wxFontEncoding encoding = wxFONTENCODING_DEFAULT )""",
        body="""\
        wxFont* font = wxFont::New(pointSize, family, flags, *faceName, encoding);
        sipCpp = new sipwxFont(*font);
        delete font;
        """)

    # Same as the above, but as a factory function
    module.addCppFunction('wxFont*', 'FFont', """(
        int pointSize,
        wxFontFamily family,
        int flags = wxFONTFLAG_DEFAULT,
        const wxString& faceName = wxEmptyString,
        wxFontEncoding encoding = wxFONTENCODING_DEFAULT )""",
        body="""\
        wxFont* font = wxFont::New(pointSize, family, flags, *faceName, encoding);
        return font;
        """, factory=True)

    
    for item in c.findAll('New'):
        item.factory = True
    
    c.addProperty('Encoding GetEncoding SetEncoding')
    c.addProperty('FaceName GetFaceName SetFaceName')
    c.addProperty('Family GetFamily SetFamily')
    c.addProperty('NativeFontInfoDesc GetNativeFontInfoDesc SetNativeFontInfo')
    c.addProperty('NativeFontInfoUserDesc GetNativeFontInfoUserDesc SetNativeFontInfoUserDesc')
    c.addProperty('PointSize GetPointSize SetPointSize')
    c.addProperty('PixelSize GetPixelSize SetPixelSize')
    c.addProperty('Style GetStyle SetStyle')
    c.addProperty('Weight GetWeight SetWeight')

    # TODO, there is now a Underlined method so we can't have a
    # property of the same name.
    #c.addProperty('Underlined GetUnderlined SetUnderlined')

       
    
    #-----------------------------------------------------------------
    tools.doCommonTweaks(module)
    tools.runGenerators(module)
    
    
    
#---------------------------------------------------------------------------
if __name__ == '__main__':
    run()

