/////////////////////////////////////////////////////////////////////////////
// Name:        _popupwin.i
// Purpose:     SWIG interface defs for wxPopupWindow and derived classes
//
// Author:      Robin Dunn
//
// Created:     22-Dec-1998
// RCS-ID:      $Id$
// Copyright:   (c) 2003 by Total Control Software
// Licence:     wxWindows license
/////////////////////////////////////////////////////////////////////////////

// Not a %module


//---------------------------------------------------------------------------

%{
#include <wx/popupwin.h>
%}

//---------------------------------------------------------------------------
%newgroup;

MustHaveApp(wxPopupWindow);

// wxPopupWindow: a special kind of top level window used for popup menus,
// combobox popups and such.
MustHaveApp(wxPopupWindow);

class wxPopupWindow : public wxWindow {
public:
    %pythonAppend wxPopupWindow         "self._setOORInfo(self)"
    %pythonAppend wxPopupWindow()       ""
    
    wxPopupWindow(wxWindow *parent, int flags = wxBORDER_NONE);
    %RenameCtor(PrePopupWindow, wxPopupWindow());

    bool Create(wxWindow *parent, int flags = wxBORDER_NONE);

    // move the popup window to the right position, i.e. such that it is
    // entirely visible
    //
    // the popup is positioned at ptOrigin + size if it opens below and to the
    // right (default), at ptOrigin - sizePopup if it opens above and to the
    // left &c
    //
    // the point must be given in screen coordinates!
    void Position(const wxPoint& ptOrigin,
                  const wxSize& size);
};


//---------------------------------------------------------------------------
%newgroup;

%{
class wxPyPopupTransientWindow : public wxPopupTransientWindow
{
public:
    wxPyPopupTransientWindow() : wxPopupTransientWindow() {}
    wxPyPopupTransientWindow(wxWindow* parent, int style = wxBORDER_NONE)
        : wxPopupTransientWindow(parent, style) {}

    PYCALLBACK_1_EXTRACT(wxPopupTransientWindow, bool, rval = false, ProcessLeftDown, (wxMouseEvent &a))
    PYCALLBACK_0_VOID(wxPopupTransientWindow, OnDismiss)
    PYCALLBACK_0_EXTRACT(wxPopupTransientWindow, bool, rval = false, CanDismiss)

    PYPRIVATE;
};

%}


MustHaveApp(wxPyPopupTransientWindow);

// wxPopupTransientWindow: a wxPopupWindow which disappears automatically
// when the user clicks mouse outside it or if it loses focus in any other way

%rename(PopupTransientWindow) wxPyPopupTransientWindow;
class wxPyPopupTransientWindow : public wxPopupWindow
{
public:
    %pythonAppend wxPyPopupTransientWindow         "self._setOORInfo(self);" setCallbackInfo(PopupTransientWindow)
    %pythonAppend wxPyPopupTransientWindow()       ""
    
    wxPyPopupTransientWindow(wxWindow *parent, int style = wxBORDER_NONE);
    %RenameCtor(PrePopupTransientWindow, wxPyPopupTransientWindow());

    void _setCallbackInfo(PyObject* self, PyObject* _class);

    // popup the window (this will show it too) and keep focus at winFocus
    // (or itself if it's NULL), dismiss the popup if we lose focus
    virtual void Popup(wxWindow *focus = NULL);

    // hide the window
    virtual void Dismiss();

    virtual bool CanDismiss();
    virtual bool ProcessLeftDown(wxMouseEvent& event);

};

//---------------------------------------------------------------------------
