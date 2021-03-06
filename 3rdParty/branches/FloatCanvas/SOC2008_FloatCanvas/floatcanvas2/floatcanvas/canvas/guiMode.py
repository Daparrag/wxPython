'''

Module that holds the GUI modes used by FloatCanvas

This approach was inpired by Christian Blouin, who also wrote the initial
version of the code.

'''

import wx
from ..resources import Resources, navCanvasIcons
import numpy as N


class Cursors(object):
    '''
         Singleton-like class to hold the standard Cursors    
    '''
    
    def __init__(self):
        ''' Build a list with the default cursors, specialize for mac '''
        self.cursors = { 'default' : wx.NullCursor }

        # cursor are automatically downscaled to 16x16 on the mac      
        self.addCursor( 'Hand', Resources.getHandImage() )
        self.addCursor( 'GrabHand', Resources.getGrabHandImage() )
        self.addCursor( 'MagPlus', navCanvasIcons.getviewmag_plusImage(), (9, 9) )
        self.addCursor( 'MagMinus', navCanvasIcons.getviewmag_minusImage(), (9, 9) )        
        self.addCursor( 'Move', navCanvasIcons.getpackage_games_arcadeImage(), (9, 9) )        
        self.addCursor( 'Rotate', navCanvasIcons.getdesignerImage(), (9, 9) )        
        self.addCursor( 'Scale', navCanvasIcons.getviewmagfitImage(), (9, 9) )        

            
    def addCursor(self, name, img, hotspot = None):
        ''' Adds a cursor to our inventory '''
        if hotspot is not None:
            img.SetOptionInt( wx.IMAGE_OPTION_CUR_HOTSPOT_X, hotspot[0] )
            img.SetOptionInt( wx.IMAGE_OPTION_CUR_HOTSPOT_Y, hotspot[1] )

        img.ConvertAlphaToMask()
        self.cursors[ name ] = cursor = wx.CursorFromImage( img )
        return cursor
        
            
    def get(cls, name):
        ''' Retrieve a cursor from the inventory. If there's no instance present
             yet, create one and use it for future requests. This makes for some
             lazy binding, because we can import this module now without having
             to create wx.App object first.
        '''
        if not hasattr(cls, 'instance'):
            cls.instance = Cursors()
            
        return cls.instance.cursors[ name ]
        
    get = classmethod( get )    


class GUIModeBase(object):
    '''
    Basic mouse mode and baseclass for other GUIModes.

    This one can (un-)register to all events and derived classes are free to
    implement any handlers. The default handler tries to find a method on_x
    where x is the name of the event (e.g. 'left_down') and calls it if present.
    This default behaviour allows derived classes to easily implement event
    handlers.
    '''
  
    active = False

    def Deactivate(self):
        '''
        Deactivate this mode, we're likely to switch to a different mode.
        Unregister events.
        '''
        self.canvas.unsubscribe( self.OnEvent, 'raw_input' )
        del self.canvas
        self.active = False
    
    def Activate(self, canvas):
        '''
        Activate this mode, register events.
        '''
        assert not self.active
        self.active = True
        self.canvas = canvas
        self.canvas.subscribe( self.OnEvent, 'raw_input' )


    def OnEvent(self, evt):
        handler = self._get_handler( evt.type )
        if handler:
            handler( evt )
        
    def _get_handler(self, fc_event_name):
        ''' by default return a handler named like on_x where x is the name of
            the event (e.g. 'left_down'). This allows derived classes to easily
            implement event handlers.
        '''
        method_name = 'on_%s' % fc_event_name

        #print method_name
        try:
            handler = getattr(self, method_name)
        except AttributeError:
            pass
        else:
            return handler
    

      
        
class GUIModeMouse(GUIModeBase):
    '''
    Mouse mode just raises any event it receives.
    '''

    def Activate(self, canvas):
        canvas.window.Cursor = Cursors.get('default')
        return super( GUIModeMouse, self ).Activate( canvas )

    def _get_handler(self, fc_event_name):
        ''' We just raise the event we got to the appropriate node '''
        return self.raiseEvent
    
    def raiseEvent(self, event):
        ''' can be called by derived classes to perform a hittest and send an
            event to any hit nodes. If no node was hit, the event is sent to the
            background, the canvas node itself.
        '''
        # send the event only to the topmost node for now
        self.canvas.sendEvent( 'input.%s' % event.type, event )
        event.node.sendEvent( event.type, event )


from ..math import numpy

class GUIModeMove(GUIModeBase):
    ''' Move mode allows the user to drag the canvas around by using a hand-like
        tool. It also allows zooming with the scroll wheel.
    '''
    def __init__(self):
        self.startMove = None

    def Activate(self, canvas):
        canvas.window.Cursor = Cursors.get('Hand')
        return super( GUIModeMove, self ).Activate( canvas )

    def on_left_down(self, event):
        ''' Record where on the canvas the button went down and capture mouse
        '''
        self.canvas.window.Cursor = Cursors.get('GrabHand')
        self.canvas.window.CaptureMouse()
        self.startMove = event.GetPosition()
        self.startCamPos = self.canvas.camera.position.copy()
 
    def on_left_up(self, event):
        ''' Release mouse and restore cursor '''
        self.canvas.window.Cursor = Cursors.get('Hand')
        self.canvas.window.ReleaseMouse()
        self.startMove = None

    def on_move(self, event):
        ''' If the user is dragging the mouse, move the camera of the canvas '''
        if event.Dragging() and event.LeftIsDown() and not self.startMove is None:
            transform = self.canvas.camera.transform
            transform.translation = (0,0)
            self.canvas.camera.position = self.startCamPos - transform( [event.coords.screen - self.startMove] )[0]

    def on_wheel(self, event):
        ''' By default, zoom in/out by a 0.1 factor per Wheel event.
            todo: make this configurable.
        '''
        if event.GetWheelRotation() < 0:
            self.canvas.zoom( 0.9 )
        else:
            self.canvas.zoom( 1.1 )


from ..math import boundingBox

class GUIModeZoomIn(GUIModeBase):
    ''' Zoom in mode allows the user to zoom in on parts of the canvas. He can
        either left_click which centers the view at the clicked position and
        zooms a bit in. The user can also drag a 'rubberband box' to select an
        area he wants to view. Or he can right click to zoom out. Or scroll to
        zoom.
    '''
    def Activate(self, canvas):
        canvas.window.Cursor = Cursors.get( 'MagPlus' )
        return super( GUIModeZoomIn, self ).Activate( canvas )

    def on_left_down(self, event):
        self.startBox = event.GetPosition()
        self.prevBox = None
        self.canvas.window.CaptureMouse()

    def on_left_up(self, event):
        ''' zoom in either by using a rubberband box or at the specific point.
            todo: make minimum cursor movement (5,5) and default zoom factor
                   (1.5) configurable
        '''
        if event.LeftUp() and not self.startBox is None:
            box = boundingBox.fromPoints( ( self.startBox, event.coords.screen ) )
            # if mouse has moved less that five pixels, don't use the box.
            if ( box.Size > (5,5) ).all():
                start = self.canvas.pointToWorld( box.min )
                end = self.canvas.pointToWorld( box.max )
                bb = boundingBox.fromPoints( (start, end) )
                self.canvas.zoomToExtents( bb, padding_percent = 0 )
            else:
                center = self.canvas.pointToWorld( self.startBox )
                self.canvas.zoom( 1.5, center )
            self.prevBox = None
            self.startBox = None
            self.canvas.window.ReleaseMouse()

    def on_move(self, event):
        ''' Take care of drawing the rubberband box '''
        if event.Dragging() and event.LeftIsDown() and not (self.startBox is None):
            dc = wx.ClientDC( self.canvas.window )
            dc.BeginDrawing()
            dc.SetPen( wx.Pen('WHITE', 2, wx.SHORT_DASH) )
            dc.SetBrush( wx.TRANSPARENT_BRUSH )
            dc.SetLogicalFunction( wx.XOR )
            if not self.prevBox is None:
                dc.DrawRectanglePointSize( self.prevBox.min, self.prevBox.Size )
            thisBox = boundingBox.fromPoints( ( self.startBox, event.coords.screen ) )
            dc.DrawRectanglePointSize( thisBox.min, thisBox.Size )
            dc.EndDrawing()
            
            self.prevBox = thisBox
            
    #def UpdateScreen(self):
    #    """
    #    Update gets called if the screen has been repainted in the middle of a zoom in
    #    so the Rubber Band Box can get updated
    #    """
    #    if self.PrevRBBox is not None:
    #        dc = wx.ClientDC(self.Canvas)
    #        dc.SetPen(wx.Pen('WHITE', 2, wx.SHORT_DASH))
    #        dc.SetBrush(wx.TRANSPARENT_BRUSH)
    #        dc.SetLogicalFunction(wx.XOR)
    #        dc.DrawRectanglePointSize(*self.PrevRBBox)

    def on_right_down(self, event):
        ''' zoom out.
            todo: make default zoom factor (1.5) configurable
        '''
        self.canvas.zoom( 1 / 1.5, event.coords.world, centerCoords = 'world' )

    def on_wheel(self, event):
        ''' By default, zoom in/out by a 0.1 factor per Wheel event.
            todo: make this configurable.
        '''
        if event.GetWheelRotation() < 0:
            self.canvas.zoom( 0.9 )
        else:
            self.canvas.zoom( 1.1 )
            

class GUIModeZoomOut(GUIModeBase):
    ''' Zoom out mode allows the user to zoom out off parts of the canvas. He
        can either left_click which centers the view at the clicked position and
        zooms a bit out. Or he can right click to zoom in. Or scroll to zoom.
    '''
    def Activate(self, canvas):
        canvas.window.Cursor = Cursors.get( 'MagMinus' )
        return super( GUIModeZoomOut, self ).Activate( canvas )

    def on_left_down(self, event):
        ''' zoom out.
            todo: make default zoom factor (1.5) configurable
        '''
        self.canvas.zoom( 1 / 1.5, event.coords.world, centerCoords = 'world' )

    def on_right_down(self, event):
        ''' zoom in.
            todo: make default zoom factor (1.5) configurable
        '''
        self.canvas.zoom( 1.5, event.coords.world, centerCoords = 'world' )

    def on_wheel(self, event):
        ''' By default, zoom in/out by a 0.1 factor per Wheel event.
            todo: make this configurable.
        '''
        if event.GetWheelRotation() < 0:
            self.canvas.zoom( 0.9 )
        else:
            self.canvas.zoom( 1.1 )



from ..math import numpy
class GUIModeObjectManipulation(GUIModeBase):
    ''' Base class for the move, rotate and scale modes.
    '''
    def Activate(self, canvas):
        canvas.window.Cursor = Cursors.get( self.cursor )
        self.node = None
        return super( GUIModeObjectManipulation, self ).Activate( canvas )

    def on_left_down(self, event):
        ''' get the node and remember where we clicked it '''
        node = event.nodes[0]
        if event.nodes[0] == self.canvas:
            return
        
        self.node = node
        self.downCoords = event.coords.world
        self.offset =  self.node.position - self.downCoords
        self.downRotation =  self.node.rotation
        self.downScale =  self.node.scale
        self.downSize = self.node.boundingBox.Size

    def on_left_up(self, event):
        self.node = None


class GUIModeMoveObjects(GUIModeObjectManipulation):
    ''' Can be used to move objects on canvas.
    '''
    cursor = 'Move'
    
    def on_move(self, event):
        ''' move the object '''
        if self.node:
            self.node.position = event.coords.world + self.offset

from ..math import get_angle
class GUIModeRotateObjects(GUIModeObjectManipulation):
    ''' Can be used to move objects on canvas.
    '''
    cursor = 'Rotate'
    
    def on_move(self, event):
        ''' rotate the object '''
        if self.node:
            angle = get_angle( self.offset, event.coords.world - self.node.position )
            self.node.rotation = self.downRotation + angle

class GUIModeScaleObjects(GUIModeObjectManipulation):
    ''' Can be used to move objects on canvas.
    '''
    cursor = 'Scale'
    
    def on_move(self, event):
        ''' move the object '''
        if self.node:
            extra_scale = (event.coords.world - self.downCoords) / self.downSize
            new_scale = self.downScale + extra_scale
            if abs(new_scale).all() > 0.001:
                self.node.scale = new_scale
