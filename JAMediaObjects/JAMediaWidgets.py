#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaWidgets.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   CeibalJAM! - Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import pygtk
import os
import gobject
import cairo
import platform
import time
import mimetypes

from gettext import gettext as _
from JAMediaMixer import JAMediaMixer
import JAMediaGlobals as G

class JAMediaButton(gtk.EventBox):
    
    __gsignals__ = {"clicked":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, )),
    "clickederecho":(gobject.SIGNAL_RUN_FIRST, gobject.
        TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}
    
    def __init__(self):
        
        gtk.EventBox.__init__(self)
        
        self.set_visible_window(True)
        self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        self.set_border_width(1)
        
        # http://developer.gnome.org/pygtk/stable/gdk-constants.html#gdk-event-mask-constants
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK |
            gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)
            
        self.connect("button_press_event", self.button_press)
        self.connect("button_release_event", self.button_release)
        self.connect("enter-notify-event", self.enter_notify_event)
        self.connect("leave-notify-event", self.leave_notify_event)
        
        self.imagen = gtk.Image()
        self.add(self.imagen)
        
        self.show_all()
        
    def button_release(self, widget, event):
        
        self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
        
    def leave_notify_event(self, widget, event):
        
        self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        
    def enter_notify_event(self, widget, event):
        
        self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
        
    def button_press(self, widget, event):
        
        if event.button == 1:
            self.modify_bg(gtk.STATE_NORMAL, G.NARANJA)
            self.emit("clicked", event)
            
        elif event.button == 3:
            #self.modify_bg(gtk.STATE_NORMAL, G.NARANJA)
            self.emit("clickederecho", event)
            
    def set_tooltip(self, texto):
        
        tooltips = gtk.Tooltips()
        tooltips.set_tip(self, texto, tip_private=None)
        
    def set_imagen(self, archivo):
        
        self.imagen.set_from_file(archivo)
        
    def set_tamanio(self, w, h):
        
        self.set_size_request(w,h)
        
class Superficie_de_Reproduccion(gtk.DrawingArea):
    
    __gsignals__ = {"ocultar_controles":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,))}
    
    def __init__(self):
        
        gtk.DrawingArea.__init__(self)
        
        #self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        self.set_size_request(G.WIDTH, G.HEIGHT)
        self.show_all()
        self.add_events(gtk.gdk.POINTER_MOTION_MASK |
        gtk.gdk.POINTER_MOTION_HINT_MASK)
        
        self.imagen = None
        
        self.connect("motion-notify-event", self.mousemotion)
        #self.connect("expose_event", self.repaintimagen)
        
    def set_imagen(self, archivo = None):
        
        if archivo:
            self.imagen = gtk.gdk.pixbuf_new_from_file(archivo)
            self.repaintimagen()
        else:
            self.imagen = None
            
    def repaintimagen(self, widget = None, event = None):
        
        if self.imagen:
            x,y,w,h = self.get_allocation()
            context =  self.window.cairo_create()
            ww, hh = self.imagen.get_width(), self.imagen.get_height()
            ct = gtk.gdk.CairoContext(context)
            
            while ww < w or hh < h:
                ww += 1
                hh = int (ww/4*3)
                
            while ww > w or hh > h:
                ww -= 1
                hh = int (ww/4*3)
                
            scaledPixbuf = self.imagen.scale_simple(ww, hh, gtk.gdk.INTERP_BILINEAR)
            ct.set_source_pixbuf(scaledPixbuf, w/2-ww/2, h/2-hh/2)
            context.paint()
            context.stroke()
        return True
    
    def expose(self, widget = None, event = None):
        
        #self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        pass
        
    def mousemotion(self, widget, event):
        
        x, y, state = event.window.get_pointer()
        xx,yy,ww,hh = self.get_allocation()
        area = ww/5
        if x in range(ww-area, ww) and y in range(yy,hh):
            self.emit("ocultar_controles", False)
            return
        else:
            self.emit("ocultar_controles", True)
            return
        
class Barra_de_Progreso(gtk.EventBox):
    
    __gsignals__ = {"change-value":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_INT, ))}
    
    def __init__(self):
        
        gtk.EventBox.__init__(self)
        
        self.scale = ProgressBar(gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))
        
        self.scale.connect("button-press-event", self.buttonpressevent)
        self.scale.connect("change-value", self.changevalueprogressbar)
        self.scale.connect("button-release-event", self.buttonreleaseevent)
        
        self.valor = 0
        self.presion = False
        
        #self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        
        self.add(self.scale)
        self.show_all()
        
    def buttonpressevent(self, widget, event):
        
        self.presion = True
        
    def buttonreleaseevent(self, widget, event):
        
        self.presion = False
        
    def set_progress(self, valor = 0):
        
        if not self.presion: self.scale.set_value(valor)
        
    def changevalueprogressbar(self, widget = None, flags = None, valor = None):
        
        if valor < 0 or valor > self.scale.ajuste.upper-2: return
        valor = int(valor)
        if valor != self.valor:
            self.valor = valor
        if not self.presion:
            self.scale.set_value(valor)
            self.emit("change-value", self.valor)
            
class ProgressBar(gtk.HScale):
    
    def __init__(self, ajuste):
        
        gtk.HScale.__init__(self, ajuste)
        
        self.ajuste = ajuste
        self.set_digits(0)
        #self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        self.set_draw_value(False)
        
        self.x, self.y, self.w, self.h = (0,0,200,40)
        self.borde, self.ancho = (15, 10)
        
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS, "iconplay.png"), 25, 25)
        self.pixbuf = pixbuf.rotate_simple(gtk.gdk.PIXBUF_ROTATE_COUNTERCLOCKWISE)
        
        self.connect("expose_event", self.expose)
        self.connect("size-allocate", self.size_allocate)
        
    def expose( self, widget, event ):
        
        x, y, w, h = (self.x, self.y, self.w, self.h)
        ancho, borde = (self.ancho, self.borde)
        
        gc = gtk.gdk.Drawable.new_gc(self.window)
        # http://developer.gnome.org/pygtk/stable/class-gdkgc.html
        # http://developer.gnome.org/pygtk/stable/class-gdkdrawable.html#method-gdkdrawable--draw-rectangle
        # draw_rectangle(gc, filled, x, y, width, height)
        
        gc.set_rgb_fg_color(G.BLANCO)
        self.window.draw_rectangle( gc, True, x, y, w, h )
        
        gc.set_rgb_fg_color(G.AMARILLO)
        ww = w- borde*2
        xx = x+ w/2 - ww/2
        hh = ancho
        yy = y+ h/2 - ancho/2
        self.window.draw_rectangle( gc, True, xx, yy, ww, hh )
        
        anchoimagen, altoimagen = (self.pixbuf.get_width(), self.pixbuf.get_height())
        ximagen = int((xx- anchoimagen/2) + self.get_value() * (ww / (self.ajuste.upper - self.ajuste.lower)))
        yimagen = yy + hh/2 - altoimagen/2
        
        gc.set_rgb_fg_color(G.NARANJA)
        self.window.draw_rectangle( gc, True, xx, yy, ximagen, hh)
        
        gc.set_rgb_fg_color(G.NEGRO)
        self.window.draw_rectangle( gc, False, xx, yy, ww, hh )
        
        self.window.draw_pixbuf( gc, self.pixbuf, 0, 0, ximagen, yimagen,
        anchoimagen, altoimagen, gtk.gdk.RGB_DITHER_NORMAL, 0, 0 )
        
        return True
    
    def size_allocate( self, widget, allocation ):
        
        self.x, self.y, self.w, self.h= allocation
        return False
    
class ButtonJAMediaMixer(JAMediaButton):
    
    def __init__(self):
        
        JAMediaButton.__init__(self)
        
        self.set_tooltip("JAMediaMixer")
        #self.set_imagen(os.path.join(G.ICONOS, "volumen.png"))
        #self.set_tamanio(G.BUTTONS, G.BUTTONS)
        path = os.path.join(G.ICONOS, "volumen.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        self.imagen.set_from_pixbuf(pixbuf)
        self.set_tamanio( G.BUTTONS, G.BUTTONS )
        
        self.jamediamixer = JAMediaMixer()
        self.jamediamixer.reset_sound()
        self.jamediamixer.hide()
        
        self.connect("clicked", self.get_jamediamixer)
        self.show_all()
        
    def get_jamediamixer(self, widget= None, event= None):
        
        self.jamediamixer.present()
        
class ToolbarLista(gtk.Toolbar):
    
    __gsignals__ = {"load_list":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_INT,)),
    "add_stream":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, [])}
    
    def __init__(self):
        
        gtk.Toolbar.__init__(self)
        
        #self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        
        boton = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS, "lista.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        imagen.set_from_pixbuf(pixbuf)
        boton.set_icon_widget(imagen)
        imagen.show()
        self.insert(boton, -1)
        boton.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(boton, _("Selecciona una Lista."), tip_private = None)
        boton.connect("clicked", self.get_menu)
        
        item = gtk.ToolItem()
        self.label = gtk.Label("")
        #self.label.modify_fg(gtk.STATE_NORMAL, G.BLANCO)
        self.label.show()
        item.add(self.label)
        self.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)
        
        self.boton_agregar = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS, "agregar.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        imagen.set_from_pixbuf(pixbuf)
        self.boton_agregar.set_icon_widget(imagen)
        imagen.show()
        self.insert(self.boton_agregar, -1)
        self.boton_agregar.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(self.boton_agregar,
            _("Agregar Streaming"), tip_private = None)
        self.boton_agregar.connect("clicked", self.emit_add_stream)
        self.show_all()
        
    def get_menu(self, widget):
        
        menu = gtk.Menu()
        '''
        item = gtk.MenuItem(_("JAMedia Radio"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 0)

        item = gtk.MenuItem(_("JAMedia TV"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 1)

        item = gtk.MenuItem(_("Mis Emisoras"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 2)

        item = gtk.MenuItem(_("Mis Canales"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 3)

        item = gtk.MenuItem(_("Mis Archivos"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 4)

        item = gtk.MenuItem(_("Audio-JAMediaVideo"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 5)

        item = gtk.MenuItem(_("Video-JAMediaVideo"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 6)

        item = gtk.MenuItem(_("JAMediaTube"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 7)

        item = gtk.MenuItem(_("Archivos Externos"))
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 8)'''

        item = gtk.MenuItem("JAMediaTube")
        menu.append(item)
        item.connect_object("activate", self.emit_load_list, 0)
        
        menu.show_all()
        gtk.Menu.popup(menu, None, None, None, 1, 0)
        
    def emit_load_list(self, indice):
        
        self.emit("load_list", indice)
        
    def emit_add_stream(self, widget):
        
        self.emit("add_stream")
        
class Barra_de_Reproduccion(gtk.HBox):
    
    __gsignals__ = {"activar":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, (gobject.TYPE_STRING,))}
    
    def __init__(self):
        
        gtk.HBox.__init__(self, False, 0)
        
        # ****** BOTON_ATRAS
        self.botonatras = JAMediaButton()
        self.botonatras.set_tooltip(_("Pista Anterior"))
        path = os.path.join(G.ICONOS, "siguiente.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32).flip(True)
        self.botonatras.imagen.set_from_pixbuf(pixbuf)
        self.botonatras.set_tamanio( G.BUTTONS, G.BUTTONS )
        self.botonatras.connect("clicked", self.clickenatras)
            
        # ****** BOTON PLAY
        self.botonplay = JAMediaButton()
        self.botonplay.set_tooltip(_("Reproducir o Pausar"))
        path = os.path.join(G.ICONOS, "play.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        self.botonplay.imagen.set_from_pixbuf(pixbuf)
        self.botonplay.set_tamanio( G.BUTTONS, G.BUTTONS )
        self.botonplay.connect("clicked", self.clickenplay_pausa)
            
        # ****** BOTON SIGUIENTE
        self.botonsiguiente = JAMediaButton()
        self.botonsiguiente.set_tooltip(_("Pista Siguiente"))
        path = os.path.join(G.ICONOS, "siguiente.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        self.botonsiguiente.imagen.set_from_pixbuf(pixbuf)
        self.botonsiguiente.set_tamanio( G.BUTTONS, G.BUTTONS )
        self.botonsiguiente.connect("clicked", self.clickensiguiente)
        
        # ****** BOTON STOP
        self.botonstop = JAMediaButton()
        self.botonstop.set_tooltip(_("Detener Reproducción"))
        path = os.path.join(G.ICONOS, "stop.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        self.botonstop.imagen.set_from_pixbuf(pixbuf)
        self.botonstop.set_tamanio( G.BUTTONS, G.BUTTONS )
        self.botonstop.connect("clicked", self.clickenstop)
        
        self.pack_start(self.botonatras, True, True, 0)
        self.pack_start(self.botonplay, True, True, 0)
        self.pack_start(self.botonsiguiente, True, True, 0)
        self.pack_start(self.botonstop, True, True, 0)
        
        self.show_all()
        
    def set_paused(self):
        
        path = os.path.join(G.ICONOS, "play.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        self.botonplay.imagen.set_from_pixbuf(pixbuf)
        
    def set_playing(self):
        
        path = os.path.join(G.ICONOS, "pausa.png")
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        self.botonplay.imagen.set_from_pixbuf(pixbuf)
        
    def clickenstop(self, widget= None, event= None):
        
        self.emit("activar", "stop")
        
    def clickenplay_pausa(self, widget= None, event= None):
        
        self.emit("activar", "pausa-play")
        
    def clickenatras(self, widget= None, event= None):
        
        self.emit("activar", "atras")
        
    def clickensiguiente(self, widget= None, event= None):
        
        self.emit("activar", "siguiente")
        
class StandarDialog(gtk.MessageDialog):
    
    def __init__(self, parent, title, label):
        
        gtk.MessageDialog.__init__(self, parent, gtk.DIALOG_MODAL,
            gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO)
        #self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        self.set_title(title)
        self.set_markup(label)
        