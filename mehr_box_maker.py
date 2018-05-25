 #! /usr/bin/env python
'''
Generates Inkscape SVG file containing box components needed to 
laser cut a tabbed construction box taking kerf into account

Copyright (C) 2018 Thore Mehr thore.mehr@gmail.com
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
__version__ = "1.0" ### please report bugs, suggestions etc to bugs@twot.eu ###

import math,inkex,simplestyle,Mehr_plate

class mehr_box_maker(inkex.Effect):
  def __init__(self):
      # Call the base class constructor.
      inkex.Effect.__init__(self)
      # Define options
      self.OptionParser.add_option('--page',action='store',type='string',dest='page',default='page_1')
      self.OptionParser.add_option('--unit',action='store',type='string',dest='unit',default='mm')
      self.OptionParser.add_option('--inside',action='store',type='string',dest='inside')
     
      self.OptionParser.add_option('--X_size',action='store',type='float',dest='X_size',default='0.0')
      self.OptionParser.add_option('--Y_size',action='store',type='float',dest='Y_size',default='0.0')
      self.OptionParser.add_option('--Z_size',action='store',type='float',dest='Z_size',default='0.0')
        
      self.OptionParser.add_option('--tab_mode',action='store',type='string',dest='tab_mode',default='number')
      self.OptionParser.add_option('--tab_size',action='store',type='float',dest='tab_size',default='0.0')
        
        
      self.OptionParser.add_option('--X_tabs',action='store',type='int',dest='X_tabs',default='0')
      self.OptionParser.add_option('--Y_tabs',action='store',type='int',dest='Y_tabs',default='0')
      self.OptionParser.add_option('--Z_tabs',action='store',type='int',dest='Z_tabs',default='0')
        
      self.OptionParser.add_option('--d_top',action='store',type='inkbool',dest='d_top',default=True)
      self.OptionParser.add_option('--d_bottom',action='store',type='inkbool',dest='d_bottom',default=True)
      self.OptionParser.add_option('--d_left',action='store',type='inkbool',dest='d_left',default=True)
      self.OptionParser.add_option('--d_right',action='store',type='inkbool',dest='d_right',default=True)
      self.OptionParser.add_option('--d_front',action='store',type='inkbool',dest='d_front',default=True)
      self.OptionParser.add_option('--d_back',action='store',type='inkbool',dest='d_back',default=True)

      self.OptionParser.add_option('--thickness',action='store',type='float',dest='thickness',default=4,help='Thickness of Material')
      self.OptionParser.add_option('--kerf',action='store',type='float',dest='kerf',default=0.2)
      self.OptionParser.add_option('--spaceing',action='store',type='float',dest='spaceing',default=1)
        
      self.OptionParser.add_option('--X_compartments',action='store',type='int',dest='X_compartments',default=1)
      self.OptionParser.add_option('--X_divisions',action='store',type='string',dest='X_divisions')
      self.OptionParser.add_option('--X_mode',action='store',type='string',dest='X_mode')
      self.OptionParser.add_option('--X_fit',action='store',type='inkbool',dest='X_fit')

      self.OptionParser.add_option('--Y_compartments',action='store',type='int',dest='Y_compartments',default=1)
      self.OptionParser.add_option('--Y_divisions',action='store',type='string',dest='Y_divisions')
      self.OptionParser.add_option('--Y_mode',action='store',type='string',dest='Y_mode')
      self.OptionParser.add_option('--Y_fit',action='store',type='inkbool',dest='Y_fit')

  
  def effect(self):
    thickness=self.unittouu(str(self.options.thickness)+self.options.unit)
    kerf=self.unittouu(str(self.options.kerf)+self.options.unit)/2#kerf is diameter in UI and radius in lib
    
    spaceing=self.unittouu(str(self.options.spaceing)+self.options.unit)
    XYZ=[self.unittouu(str(self.options.X_size)+self.options.unit),self.unittouu(str(self.options.Y_size)+self.options.unit),self.unittouu(str(self.options.Z_size)+self.options.unit)]

    if(self.options.inside=='0'):#if the sizes are outside sizes reduce the size by thickness if the side gets drawn
      draw=(self.options.d_left,self.options.d_front,self.options.d_top,self.options.d_right,self.options.d_back,self.options.d_bottom)#order in XYZXYZ
      for i in range(6):
        XYZ[i%3]-=(thickness if draw[i] else 0)#remove a thickness if drawn

#compartments on the X axis, devisons in Y direction
    X_divisions_distances=[]
    if (self.options.X_compartments>1):
      if (self.options.X_mode=='even'):#spliting in even compartments
        X_divisions_distances=[((XYZ[0])-(self.options.X_compartments-1)*(thickness))/self.options.X_compartments]
      else:
        for dist in self.options.X_divisions.replace(",",".").split(";"):#fixing seperator, spliting string
          X_divisions_distances+=[float(self.unittouu(dist+self.options.unit))]#translate into universal units
      X_divisions_distances[0]+=kerf#fixing for kerf
      if self.options.X_mode!='absolut':#for even and relative fix list lenght and offset compartments to absolut distances
        while (len(X_divisions_distances)<self.options.X_compartments+1):#making the list long enought for relative offsets
          X_divisions_distances+=X_divisions_distances
        for i in range(1,self.options.X_compartments):#offset to absolut distances
          X_divisions_distances[i]+=X_divisions_distances[i-1]+thickness-kerf
      X_divisions_distances=X_divisions_distances[0:self.options.X_compartments]#cutting excesive lenght off
      
      if(X_divisions_distances[-2]+thickness>XYZ[0])and not self.options.X_fit:
        inkex.errormsg("X Axis compartments outside of plate")
      if self.options.X_fit:
        XYZ[0]=X_divisions_distances[-1]-kerf
      X_divisions_distances=X_divisions_distances[0:-1]#cutting the last of

    Y_divisions_distances=[]
    if (self.options.Y_compartments>1):
      if (self.options.Y_mode=='even'):#spliting in even compartments
        Y_divisions_distances=[((XYZ[1])-(self.options.Y_compartments-1)*(thickness))/self.options.Y_compartments]
      else:
        for dist in self.options.Y_divisions.replace(",",".").split(";"):#fixing seperator, spliting string
          Y_divisions_distances+=[float(self.unittouu(dist+self.options.unit))]#translate into universal units
      Y_divisions_distances[0]+=kerf#fixing for kerf
      if self.options.Y_mode!='absolut':#for even and relative fix list lenght and offset compartments to absolut distances
        while (len(Y_divisions_distances)<self.options.Y_compartments+1):#making the list long enought for relative offsets
          Y_divisions_distances+=Y_divisions_distances
        for i in range(1,self.options.Y_compartments):#offset to absolut distances
          Y_divisions_distances[i]+=Y_divisions_distances[i-1]+thickness-kerf
      Y_divisions_distances=Y_divisions_distances[0:self.options.Y_compartments]#cutting excesive lenght off
      
      if(Y_divisions_distances[-2]+thickness>XYZ[1])and not self.options.X_fit:
        inkex.errormsg("Y Axis compartments outside of plate")
      if self.options.Y_fit:
        XYZ[1]=Y_divisions_distances[-1]-kerf
      Y_divisions_distances=Y_divisions_distances[0:-1]#cutting the last of

    if (self.options.tab_mode=='number'):#fixed number of tabs
      Tabs_XYZ=[self.options.X_tabs,self.options.Y_tabs,self.options.Z_tabs]
    else:#compute apropriate number of tabs for the edges
      tab_size=float(self.unittouu(str(self.options.tab_size)+self.options.unit))
      Tabs_XYZ=[max(1,int(XYZ[0]/(tab_size))/2),max(1,int(XYZ[1]/(tab_size))/2),max(1,int(XYZ[2]/(tab_size))/2)]
	
    
#top and bottom plate
    tabs_tb=(Tabs_XYZ[0] if self.options.d_back else 0,Tabs_XYZ[1] if self.options.d_right else 0,Tabs_XYZ[0] if self.options.d_front else 0,Tabs_XYZ[1] if self.options.d_left else 0)
    start_tb=(True  if self.options.d_back else False,True  if self.options.d_right else False,True  if self.options.d_front else False,True  if self.options.d_left else False)
    Plate_tb=Mehr_plate.Mehr_plate((XYZ[0],XYZ[1]),tabs_tb,start_tb,thickness,kerf)#top and bottom plate
    for d in X_divisions_distances:
      Plate_tb.add_holes('Y',d,Tabs_XYZ[1])
    for d in Y_divisions_distances:
      Plate_tb.add_holes('X',d,Tabs_XYZ[0])
#left and right plate
    tabs_lr=(Tabs_XYZ[2] if self.options.d_back else 0,Tabs_XYZ[1] if self.options.d_top else 0,Tabs_XYZ[2] if self.options.d_front else 0,Tabs_XYZ[1] if self.options.d_bottom else 0) 
    start_lr=(True  if self.options.d_back else False,False,True  if self.options.d_front else False,False)
    Plate_lr=Mehr_plate.Mehr_plate((XYZ[2],XYZ[1]),tabs_lr,start_lr,thickness,kerf)#left and right plate
    for d in Y_divisions_distances:
      Plate_lr.add_holes('X',d,Tabs_XYZ[2])
#front and back plate
    tabs_fb=(Tabs_XYZ[0] if self.options.d_top else 0,Tabs_XYZ[2] if self.options.d_right else 0,Tabs_XYZ[0] if self.options.d_bottom else 0,Tabs_XYZ[2] if self.options.d_left else 0)#
    start_fb=(False,False,False,False)
    Plate_fb=Mehr_plate.Mehr_plate((XYZ[0],XYZ[2]),tabs_fb,start_fb,thickness,kerf)#font and back plate
    for d in X_divisions_distances:
      Plate_fb.add_holes('Y',d,Tabs_XYZ[2])

    Plate_xc=Mehr_plate.Mehr_plate((XYZ[2],XYZ[1]),tabs_lr,(False,False,False,False),thickness,kerf)
    for d in Y_divisions_distances:
      Plate_xc.holes+=[Plate_xc.rect([0,Plate_xc.corner_offset[1]+d+kerf],[Plate_xc.AABB[0]/2-kerf,thickness-2*kerf])]
     
    Plate_yc=Mehr_plate.Mehr_plate((XYZ[0],XYZ[2]),tabs_fb,(False,False,False,False),thickness,kerf)
    for d in X_divisions_distances:
      Plate_yc.holes+=[Plate_yc.rect([Plate_yc.corner_offset[0]+d+kerf,0],[thickness-2*kerf,Plate_yc.AABB[1]/2-kerf])]

     
    X_offset=0
    Y_offset=0
    if(self.options.d_top):
      Plate_tb.draw([X_offset+spaceing,spaceing],["#000000","#ff0000"],self.current_layer)#drawing a plate using black for the outline and red for holes
      X_offset+=Plate_tb.AABB[0]+spaceing
      Y_offset=max(Y_offset,Plate_tb.AABB[1])
    if(self.options.d_bottom):
      Plate_tb.draw([X_offset+spaceing,spaceing],["#000000","#ff0000"],self.current_layer)
      X_offset+=Plate_tb.AABB[0]+spaceing
      Y_offset=max(Y_offset,Plate_tb.AABB[1])
      
    if(self.options.d_left):
      Plate_lr.draw([X_offset+spaceing,spaceing],["#000000","#ff0000"],self.current_layer)
      X_offset+=Plate_lr.AABB[0]+spaceing
      Y_offset=max(Y_offset,Plate_lr.AABB[1])
    if(self.options.d_right):
      Plate_lr.draw([X_offset+spaceing,spaceing],["#000000","#ff0000"],self.current_layer)
      X_offset+=Plate_lr.AABB[0]+spaceing
      Y_offset=max(Y_offset,Plate_lr.AABB[1])
      
    if(self.options.d_front):
      Plate_fb.draw([X_offset+spaceing,spaceing],["#000000","#ff0000"],self.current_layer)
      X_offset+=Plate_fb.AABB[0]+spaceing
      Y_offset=max(Y_offset,Plate_fb.AABB[1])
    if(self.options.d_back):
      Plate_fb.draw([X_offset+spaceing,spaceing],["#000000","#ff0000"],self.current_layer)
      X_offset+=Plate_fb.AABB[0]+spaceing
      Y_offset=max(Y_offset,Plate_fb.AABB[1])
    X_offset=0
    for i in range(self.options.X_compartments-1):
      Plate_xc.draw([X_offset+spaceing,spaceing+Y_offset],["#000000","#ff0000"],self.current_layer)
      X_offset+=Plate_xc.AABB[0]+spaceing
    X_offset=0
    Y_offset+=spaceing+Plate_xc.AABB[1]
    for i in range(self.options.Y_compartments-1):
      Plate_yc.draw([X_offset+spaceing,spaceing+Y_offset],["#000000","#ff0000"],self.current_layer)
      X_offset+=Plate_yc.AABB[0]+spaceing
    
    
effect = mehr_box_maker()
effect.affect()