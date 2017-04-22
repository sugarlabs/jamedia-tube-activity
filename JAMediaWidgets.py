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
import os
import gobject
import commands
import urllib
import time
import sys

from gettext import gettext as _
import JAMediaGlobals as G
from JAMediaYoutubeInterfase import JAMediaYouyubeDownload

class JAMediaButton(gtk.EventBox):
    
    __gsignals__ = {"clicked":(gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))}
    
    def __init__(self):
        
        gtk.EventBox.__init__(self)
        
        self.set_visible_window(True)
        self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        self.set_border_width(1)
        
        # http://developer.gnome.org/pygtk/stable/gdk-constants.html#gdk-event-mask-constants
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK |
        gtk.gdk.POINTER_MOTION_MASK |
        gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)
            
        self.connect("button_press_event", self.button_press)
        self.connect("button_release_event", self.button_release)
        self.connect("enter-notify-event", self.enter_notify_event)
        self.connect("leave-notify-event", self.leave_notify_event)
        
        self.imagen= gtk.Image()
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
            
    def set_tooltip(self, texto):
        
        tooltips = gtk.Tooltips()
        tooltips.set_tip(self, texto, tip_private=None)
        
    def set_imagen(self, archivo):
        
            self.imagen.set_from_file(archivo)
            
    def set_tamanio(self, w, h):
        
        self.set_size_request(w,h)
        
class AlertBusqueda(gtk.Window):
    
    __gsignals__ = {"lanzarbusqueda":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, [])}
    
    def __init__(self, ventanajamedia):
        
        super(AlertBusqueda, self).__init__(gtk.WINDOW_POPUP)
        self.ventanajamedia= ventanajamedia
        
        self.set_resizable(False)
        self.set_border_width(20)
        self.set_transient_for(self.ventanajamedia)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        #self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        
        self.set_layout()
        self.show_all()
        
        gobject.idle_add(self.emit_realized)
        
    def set_layout(self):
        
        vbox= gtk.VBox()
        imagen = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(G.ICONOS, "yt_videos_black.png"))
        imagen.set_from_pixbuf(pixbuf)
        vbox.pack_start(imagen, False, False, 3)
        vbox.pack_start(gtk.Label(_("Buscando Videos, por favor espera . . .")), False, False, 5)
        self.add(vbox)
        
    def emit_realized(self, widget = None):
        
        self.emit("lanzarbusqueda")
        
class Barra_de_Busquedas(gtk.Toolbar):
    
    __gsignals__ = {"comenzarbusqueda":(gobject.SIGNAL_RUN_FIRST,
    gobject.TYPE_NONE, (gobject.TYPE_STRING, ))}
    
    def __init__(self):
        
        gtk.Toolbar.__init__(self)
        
        #self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
        #self.modify_fg(gtk.STATE_NORMAL, G.NEGRO)
        self.entrytext = None
        self.botonbuscar = None
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)
        
        item = gtk.ToolItem()
        label = gtk.Label(_("Buscar por:"))
        label.show()
        item.add(label)
        self.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.insert(separator, -1)
        
        item = gtk.ToolItem()
        self.entrytext = gtk.Entry()
        self.entrytext.set_size_request(400, -1)
        self.entrytext.set_max_length(50)
        self.entrytext.show()
        item.add(self.entrytext)
        self.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.insert(separator, -1)
        
        self.botonbuscar = gtk.ToolButton()
        imagen = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(G.ICONOS,'iconplay.png'), 32, 32)
        pixbuf = pixbuf.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
        imagen.set_from_pixbuf(pixbuf)
        self.botonbuscar.set_icon_widget(imagen)
        imagen.show()
        self.botonbuscar.connect('clicked', self.emit_buscar)
        self.insert(self.botonbuscar, -1)
        self.botonbuscar.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(self.botonbuscar, _("Comenzar Búsqueda"), tip_private=None)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)
        
        self.show_all()
        
        self.botonbuscar.connect("clicked", self.emit_buscar)
        
    def emit_buscar(self, widget = None):
        
        texto = self.entrytext.get_text()
        if texto: self.emit("comenzarbusqueda", texto)
        self.entrytext.set_text("")
        
class Toolbar0(gtk.Toolbar):
    
    __gsignals__ = {'salir':(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, []),
    'jamedia_jamediatube':(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, [])}
    
    def __init__(self):
        
        gtk.Toolbar.__init__(self)
        
        #self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.insert(separator, -1)
        
        salir = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS, 'JAMediaTube.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 42, 32)
        imagen.set_from_pixbuf(pixbuf)
        salir.set_icon_widget(imagen)
        imagen.show()
        salir.connect('clicked', self.emit_jamedia_jamediatube)
        self.insert(salir, -1)
        salir.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(salir, "JAMediaTube - JAMedia", tip_private=None)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)
        
        imagen = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(G.ICONOS,'ceibaljam.png'))
        imagen.set_from_pixbuf(pixbuf)
        imagen.show()
        item = gtk.ToolItem()
        item.add(imagen)
        self.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.insert(separator, -1)
        
        imagen = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(G.ICONOS,'uruguay.png'))
        imagen.set_from_pixbuf(pixbuf)
        imagen.show()
        item = gtk.ToolItem()
        item.add(imagen)
        self.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.insert(separator, -1)
        
        imagen = gtk.Image()
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(G.ICONOS,'licencia.png'))
        imagen.set_from_pixbuf(pixbuf)
        imagen.show()
        item = gtk.ToolItem()
        item.add(imagen)
        self.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.insert(separator, -1)
        
        item = gtk.ToolItem()
        label = gtk.Label("fdanesse@gmail.com")# - https://sites.google.com/site/sugaractivities/jam")
        #label.modify_fg(gtk.STATE_NORMAL, G.BLANCO)
        label.show()
        item.add(label)
        self.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)
        
        salir = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS,'salir.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        imagen.set_from_pixbuf(pixbuf)
        salir.set_icon_widget(imagen)
        imagen.show()
        salir.connect('clicked', self.emit_salir)
        self.insert(salir, -1)
        salir.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(salir, _("Salir de JAMediaTube"), tip_private=None)
        
        self.show_all()
        
    def emit_salir(self, widget = None):
        
        self.emit("salir")
        
    def emit_jamedia_jamediatube(self, widget = None):
        
        self.emit("jamedia_jamediatube")
        
class Toolbar1(gtk.Toolbar):
    
    __gsignals__ = {'move':(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, []),
    'clear':(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, [])}
    
    def __init__(self):
        
        gtk.Toolbar.__init__(self)
        
        #self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)
        
        clear_button = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS,'alejar.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        imagen.set_from_pixbuf(pixbuf)
        clear_button.set_icon_widget(imagen)
        imagen.show()
        clear_button.connect('clicked', self.emit_clear)
        self.insert(clear_button, -1)
        clear_button.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(clear_button, _("Eliminar Todos."), tip_private=None)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.insert(separator, -1)
        
        append_button = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS,'iconplay.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        imagen.set_from_pixbuf(pixbuf)
        append_button.set_icon_widget(imagen)
        imagen.show()
        append_button.connect('clicked', self.emit_move)
        self.insert(append_button, -1)
        append_button.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(append_button, _("Agregar Todos."), tip_private=None)
        
        self.show_all()
        
    def emit_clear(self, button):
        
        self.emit('clear')
        
    def emit_move(self, button):
        
        self.emit('move')
        
class Toolbar2(gtk.Toolbar):
    
    __gsignals__ = {'download':(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, []),
    'clear':(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, [])}
    
    def __init__(self):
        
        gtk.Toolbar.__init__(self)
        
        self.disconnectdownload = False
        
        #self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        append_button = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS,'iconplay.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        pixbuf = pixbuf.flip(True)
        imagen.set_from_pixbuf(pixbuf)
        append_button.set_icon_widget(imagen)
        imagen.show()
        append_button.connect('clicked', self.emit_clear)
        self.insert(append_button, -1)
        append_button.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(append_button, _("Quitar Todos."), tip_private=None)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.insert(separator, -1)
        
        download_button = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS,'iconplay.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        pixbuf = pixbuf.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
        imagen.set_from_pixbuf(pixbuf)
        download_button.set_icon_widget(imagen)
        imagen.show()
        download_button.connect('clicked', self.emit_download)
        self.insert(download_button, -1)
        download_button.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(download_button, _("Descargar Todos."), tip_private=None)
        
        self.show_all()
        
    def emit_clear(self, button):
        
        self.emit('clear')
        
    def emit_download(self, button):
        
        if self.disconnectdownload: return
        self.emit('download')
        
class WidgetVideoItem(gtk.EventBox):
    
    __gsignals__ = {"clicked":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, []),
    "clickederecho":(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, [])}
    
    def __init__(self, videodict):
        
        gtk.EventBox.__init__(self)
        
        self.set_visible_window(True)
        self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        self.set_border_width(1)
        
        # http://developer.gnome.org/pygtk/stable/gdk-constants.html#gdk-event-mask-constants
        self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
        gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK |
        gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK)
        
        self.videodict = videodict
        self.layout()
        
        self.connect("enter-notify-event", self.enter_notify_event)
        self.connect("leave-notify-event", self.leave_notify_event)
        
        self.show_all()
        
    def layout(self):
        
        hbox = gtk.HBox()
        vbox = gtk.VBox()
        
        keys = self.videodict.keys()
        
        if "previews" in keys:
            imagen = gtk.Image()
            url = self.videodict["previews"][0][0]
            archivo = "/tmp/preview%d" % time.time()
            fileimage, headers = urllib.urlretrieve(url, archivo)
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(fileimage, 200, 200)
            imagen.set_from_pixbuf(pixbuf)
            hbox.pack_start(imagen, False, False, 3)
            commands.getoutput('rm %s' % (archivo))
            
        vbox.pack_start(gtk.Label("%s: %s" % (_("id"),
            self.videodict["id"])), True, True, 0)
        vbox.pack_start(gtk.Label("%s: %s" % (_("Título"),
            self.videodict["titulo"])), True, True, 0)
        vbox.pack_start(gtk.Label("%s: %s" % (_("Categoría"),
            self.videodict["categoria"])), True, True, 0)
        #vbox.pack_start(gtk.Label("%s: %s" % (_("Etiquetas"),
        #    self.videodict["etiquetas"])), True, True, 0)
        #vbox.pack_start(gtk.Label("%s: %s" % (_("Descripción"),
        #   self.videodict["descripcion"])), True, True, 0)
        vbox.pack_start(gtk.Label("%s: %s %s" % (_("Duración"),
            int(float(self.videodict["duracion"])/60.0), _("Minutos"))),
            True, True, 0)
        #vbox.pack_start(gtk.Label("%s: %s" % (_("Reproducción en la Web"),
        #   self.videodict["flash player"])), True, True, 0)
        vbox.pack_start(gtk.Label("%s: %s" % ("url",
            self.videodict["url"])), True, True, 0)
        
        for label in vbox.get_children():
            
            label.set_justify(gtk.JUSTIFY_LEFT)
            label.show()
            
        hbox.pack_start(vbox, False, False, 0)
        vbox.show_all()
        hbox.show_all()
        self.add(hbox)
        
    def leave_notify_event(self, widget, event):
        
        self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        
    def enter_notify_event(self, widget, event):
        
        self.modify_bg(gtk.STATE_NORMAL, G.AMARILLO)
        
class WidgetDescarga(gtk.VBox):
    
    __gsignals__ = {'end':(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, [])}
    
    def __init__(self, videoitem):
        
        super(WidgetDescarga, self).__init__()
        
        #self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        
        self.toolbar = gtk.Toolbar()
        #self.toolbar.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        
        self.labeltitulo = None
        self.salir = None
        self.labelprogress = None
        self.progress = 0.0
        self.barradeprogreso = None
        
        self.datostemporales = None
        self.ultimosdatos = None
        self.contadortestigo = 0
        
        self.url = videoitem.videodict["url"]
        self.titulo = videoitem.videodict["titulo"]
        
        self.jamediayoutubedownload = None
        
        self.set_layout()
        self.show_all()
        
        self.labeltitulo.set_text(self.titulo)
        videoitem.destroy()
        gobject.idle_add(self.start_download)
        
    def set_layout(self):
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.toolbar.insert(separator, -1)
        
        self.labeltitulo = gtk.Label("")
        #self.labeltitulo.modify_fg(gtk.STATE_NORMAL, G.AMARILLO)
        item = gtk.ToolItem()
        item.add(self.labeltitulo)
        self.labeltitulo.show()
        self.toolbar.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.toolbar.insert(separator, -1)
        
        self.labelprogress = gtk.Label("")
        #self.labelprogress.modify_fg(gtk.STATE_NORMAL, G.AMARILLO)
        item = gtk.ToolItem()
        item.add(self.labelprogress)
        self.labelprogress.show()
        self.toolbar.insert(item, -1)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        self.toolbar.insert(separator, -1)
        
        self.salir = gtk.ToolButton()
        imagen = gtk.Image()
        path = os.path.join(G.ICONOS,'stop.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(path, 32, 32)
        pixbuf = pixbuf.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
        imagen.set_from_pixbuf(pixbuf)
        self.salir.set_icon_widget(imagen)
        imagen.show()
        self.salir.connect('clicked', self.cancel_download)
        self.toolbar.insert(self.salir, -1)
        self.salir.show()
        tooltips = gtk.Tooltips()
        tooltips.set_tip(self.salir, _("Cancelar Descarga"), tip_private=None)
        
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        self.toolbar.insert(separator, -1)
        
        self.barradeprogreso = Barra_de_Progreso()
        self.barradeprogreso.show()
        
        self.pack_start(self.toolbar, True, True, 0)
        self.pack_start(self.barradeprogreso, True, True, 0)
        
    def start_download(self):
        
        self.progress = 0.0
        self.datostemporales = None
        self.ultimosdatos = None
        self.contadortestigo = 0
        self.actualizador = gobject.timeout_add(1000, self.handle)
        self.jamediayoutubedownload = JAMediaYouyubeDownload(self.url, self.titulo)
        self.jamediayoutubedownload.connect("progressdownload", self.progressdownload)
        self.jamediayoutubedownload.download_archivo()
        
    def handle(self):
        
        if self.ultimosdatos != self.datostemporales:
            self.ultimosdatos = self.datostemporales
            self.contadortestigo = 0
        else:
            self.contadortestigo += 1
        if self.contadortestigo > 8:
            self.cancel_download()
            #print "No se pudo descargar el archivo:", self.titulo
            return False
        return True
    
    def progressdownload(self, widget, progress):
        
        self.datostemporales = progress
        datos = progress.split(" ")
        
        if datos[0] == '[youtube]':
            dat = progress.split('[youtube]')[1]
            if self.labelprogress.get_text() != dat:
                self.labelprogress.set_text( dat )
                
        elif datos[0] == '[download]':
            dat = progress.split('[download]')[1]
            if self.labelprogress.get_text() != dat:
                self.labelprogress.set_text( dat )
                
        elif datos[0] == '\r[download]':
            porciento = 0.0
            if "%" in datos[2]:
                porciento = datos[2].split("%")[0]
            elif "%" in datos[3]:
                porciento = datos[3].split("%")[0]
            porciento = float(porciento)
            self.barradeprogreso.changevalueprogressbar(widget = None,
                flags = None, valor = int(porciento))
            if porciento >= 100.0: # nunca llega
                self.cancel_download()
                return False
            else:
                dat = progress.split("[download]")[1]
                if self.labelprogress.get_text() != dat:
                    self.labelprogress.set_text( dat )
                    
        if "100.0%" in progress.split(" "):
            self.cancel_download()
            return False
        return True
    
    def cancel_download(self, button=None, event=None):
        
        # No funciona correctamente, la descarga continúa.
        self.jamediayoutubedownload.end()
        self.emit("end")
        return False
    
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
        #self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
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
        #self.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        self.set_draw_value(False)
        self.x, self.y, self.w, self.h = (0,0,200,40)
        self.borde, self.ancho = (15, 10)
        self.connect("expose_event", self.expose)
        self.connect("size-allocate", self.size_allocate)
        
    def expose( self, widget, event ):
        
        x, y, w, h = (self.x, self.y, self.w, self.h)
        ancho, borde = (self.ancho, self.borde)
        gc = gtk.gdk.Drawable.new_gc(self.window)
        # http://developer.gnome.org/pygtk/stable/class-gdkgc.html
        # http://developer.gnome.org/pygtk/stable/class-gdkdrawable.html#method-gdkdrawable--draw-rectangle
        # draw_rectangle(gc, filled, x, y, width, height)
        #gc.set_rgb_fg_color(G.NEGRO)
        self.window.draw_rectangle( gc, True, x, y, w, h )
        gc.set_rgb_fg_color(G.AMARILLO)
        ww = w- borde*2
        xx = x+ w/2 - ww/2
        hh = ancho
        yy = y+ h/2 - ancho/2
        self.window.draw_rectangle( gc, True, xx, yy, ww, hh )
        anchoimagen, altoimagen = (25,25)
        ximagen = int((xx- anchoimagen/2) + self.get_value() * (ww / (self.ajuste.upper - self.ajuste.lower)))
        yimagen = yy + hh/2 - altoimagen/2
        gc.set_rgb_fg_color(G.NARANJA)
        self.window.draw_rectangle( gc, True, xx, yy, ximagen, hh)
        #gc.set_rgb_fg_color(G.BLANCO)
        #gc.set_rgb_fg_color(G.NEGRO)
        self.window.draw_rectangle( gc, False, xx, yy, ww, hh )
        return True
    
    def size_allocate( self, widget, allocation ):
        
        self.x, self.y, self.w, self.h= allocation
        return False
    
class StandarDialog(gtk.MessageDialog):
    
    def __init__(self, parent, title, label):
        
        gtk.MessageDialog.__init__(self, parent,
            gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_YES_NO)
        #self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        self.set_title(title)
        self.set_markup(label)
        