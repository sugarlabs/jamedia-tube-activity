#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaTube.py por:
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
import time
import sys
import gobject
import commands

from sugar.activity import activity
from gettext import gettext as _
import JAMediaGlobals as G
commands.getoutput('PATH=%s:$PATH' % (G.DIRECTORIO_BASE))
#commands.getoutput('PATH=$PATH:%s & export PATH' % (G.DIRECTORIO_BASE))

from JAMediaWidgets import *
import JAMediaYoutubeInterfase as YT
import JAMediaObjects
from JAMediaObjects.JAMedia import JAMediaPlayer
from JAMediaObjects.JAMedia import JAMedia

gobject.threads_init()
gtk.gdk.threads_init()

class JAMediaTube(activity.Activity):
    
    def __init__(self, handle):
        
        activity.Activity.__init__(self, handle)
        
        self.set_title("JAMediaTube")
        #self.modify_bg(gtk.STATE_NORMAL, G.BLANCO)
        self.set_icon_from_file(os.path.join(G.ICONOS, "JAMediaTube.png"))
        self.set_size_request(G.WIDTH,G.HEIGHT)
        self.set_border_width(5)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(True)

        self.barradebusquedas = None
        self.boxinfoprogressdownload = None
        self.vboxvideos = None
        self.vboxparadescargar = None
        self.toolbar0 = None
        self.toolbar1 = None
        self.toolbar2 = None
        self.label_resultados = None # _("Videos Encontrados:")
        self.label_descargas = None # _("Videos para Descargar:"))
        self.jamedia = None
        self.jamediaview = False
        self.socket = None
        self.panel_listas = None
        self.vboxbase = None
        self.vboxinterno = None

        self.set_layout()
        self.show_all()
        self.realize()

        self.connect("delete_event", self.delete_event)

        self.barradebusquedas.connect("comenzarbusqueda", self.comenzarbusqueda)

        self.toolbar0.connect('salir', self.salir)
        self.toolbar0.connect('jamedia_jamediatube', self.show_player)
        self.toolbar1.connect("move", self.movervideos)
        self.toolbar1.connect("clear", self.eliminarvideos)
        self.toolbar2.connect("clear", self.movervideos)
        self.toolbar2.connect("download", self.download)

        gobject.timeout_add(1000, self.handle)
        gobject.idle_add(self.add_jamedia)

    def add_jamedia(self):
        
        self.jamedia = JAMediaPlayer()
        self.socket.add_id(self.jamedia.get_id())
        self.jamedia.connect("OK", self.add_jamediatube)

    def add_jamediatube(self, widget = None):
        
        self.socket.hide()
        self.jamediaview = False
        self.vboxbase.pack_start(self.vboxinterno, True, True, 0)
        self.vboxinterno.show_all()

    def show_player(self, widget):
        
        if self.jamediaview:
            self.jamediaview = False
            self.socket.hide()
            self.vboxinterno.show_all()
        else:
            self.jamediaview = True
            self.vboxinterno.hide()
            self.socket.show()

    def handle(self):
        
        busqueda = len(self.vboxvideos.get_children())
        self.label_resultados.set_text("%s %s" % (_("Videos Encontrados:"), busqueda))
        descargas = len(self.vboxparadescargar.get_children())
        self.label_descargas.set_text("%s %s" % (_("Videos para Descargar:"), descargas))
        return True

    def download (self, widget=None):
        
        videos = self.vboxparadescargar.get_children()
        if videos:
            self.toolbar2.disconnectdownload = True
            videoitem = videos[0]
            self.vboxparadescargar.remove(videoitem)
            descarga = WidgetDescarga(videoitem)
            self.boxinfoprogressdownload.add(descarga)
            descarga.connect("end", self.next_download)
        else:
            self.toolbar2.disconnectdownload = False

    def next_download(self, widget):
        
        widget.destroy()
        self.download()

    def eliminarvideos(self, widget):
        
        if widget == self.toolbar1:
            if not self.vboxvideos.get_children(): return
            dialog = StandarDialog(self, "Mensaje JAMedia",
                _("¿ Eliminar Toda la Búsqueda ?"))
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                for child in self.vboxvideos.get_children():
                    self.vboxvideos.remove(child)
                    child.destroy()
                    
    def movervideos(self, widget):
        
        if widget == self.toolbar1:
            for child in self.vboxvideos.get_children():
                self.vboxvideos.remove(child)
                self.vboxparadescargar.pack_start(child, False, False, 1)
                tooltips = gtk.Tooltips()
                text = "Arrastra Hacia La Izquierda para Quitarlo de las Descargas"
                tooltips.set_tip(child, _(text), tip_private=None)
                
        elif widget == self.toolbar2:
            for child in self.vboxparadescargar.get_children():
                self.vboxparadescargar.remove(child)
                self.vboxvideos.pack_start(child, False, False, 1)
                tooltips = gtk.Tooltips()
                text = "Arrastra Hacia La Derecha para Agregarlo a Descargas"
                tooltips.set_tip(child, _(text), tip_private=None)
        
    def comenzarbusqueda(self, widget, palabras):
        
        alert = AlertBusqueda(self)
        alert.connect("lanzarbusqueda", self.lanzarbusqueda, palabras)
        
    def lanzarbusqueda(self, widget, palabras):
        
        for child in self.vboxvideos.get_children():
            self.vboxvideos.remove(child)
            child.destroy()
            
        for video in YT.Buscar(palabras):
            videowidget = WidgetVideoItem(video)
            tooltips = gtk.Tooltips()
            text = "Arrastra Hacia La Derecha para Agregarlo a Descargas"
            tooltips.set_tip(videowidget, _(text), tip_private=None)
            self.vboxvideos.pack_start(videowidget, False, False, 1)
            videowidget.drag_source_set(gtk.gdk.BUTTON1_MASK, targets, gtk.gdk.ACTION_MOVE)
            #videowidget.drag_source_set_icon_pixbuf(child.imagen.pixbuf)
        widget.destroy()

    def set_layout(self):
        
        self.vboxbase = gtk.VBox()
        self.toolbar0 = Toolbar0()
        self.vboxbase.pack_start(self.toolbar0, False, False, 5)

        self.vboxinterno = gtk.VBox()
        #self.vboxbase.pack_start(self.vboxinterno, True, True, 0)

        self.barradebusquedas = Barra_de_Busquedas()
        self.boxinfoprogressdownload = gtk.EventBox()
        self.boxinfoprogressdownload.set_visible_window(False)
        self.panel_listas = gtk.HPaned()
        self.vboxinterno.pack_start(self.barradebusquedas, False, False, 0)
        self.vboxinterno.pack_start(self.boxinfoprogressdownload, False, False, 0)
        self.vboxinterno.pack_start(self.panel_listas, True, True, 0)

        vbox = gtk.VBox() # videos encontrados
        self.vboxvideos = gtk.VBox()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(self.vboxvideos)
        self.toolbar1 = Toolbar1()
        toolbar = gtk.Toolbar()
        #toolbar.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        toolbar.insert(separator, -1)
        self.label_resultados = gtk.Label(_("Videos Encontrados:"))
        #self.label_resultados.modify_fg(gtk.STATE_NORMAL, G.AMARILLO)
        item = gtk.ToolItem()
        item.add(self.label_resultados)
        self.label_resultados.show()
        toolbar.insert(item, -1)
        vbox.pack_start(toolbar, False, False, 0)
        vbox.pack_start(sw, True, True, 0)
        vbox.pack_start(self.toolbar1, False, False, 0)
        self.panel_listas.pack1(vbox, resize=True, shrink=True)

        vbox = gtk.VBox() # videos en descarga
        self.vboxparadescargar = gtk.VBox()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add_with_viewport(self.vboxparadescargar)
        self.toolbar2 = Toolbar2()
        toolbar = gtk.Toolbar()
        #toolbar.modify_bg(gtk.STATE_NORMAL, G.NEGRO)
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(5, -1)
        separator.set_expand(False)
        toolbar.insert(separator, -1)
        self.label_descargas = gtk.Label(_("Videos para Descargar:"))
        #self.label_descargas.modify_fg(gtk.STATE_NORMAL, G.AMARILLO)
        item = gtk.ToolItem()
        item.add(self.label_descargas)
        self.label_descargas.show()
        toolbar.insert(item, -1)
        vbox.pack_start(toolbar, False, False, 0)
        vbox.pack_start(sw, True, True, 0)
        vbox.pack_start(self.toolbar2, False, False, 0)
        self.panel_listas.pack2(vbox, resize=True, shrink=True)

        self.socket = gtk.Socket() # para embeber jamedia
        # self.vboxbase.pack_start(self.vboxinterno, True, True, 0)
        self.vboxbase.pack_start(self.socket, True, True, 0)
        #self.add(self.vboxbase)
        self.set_canvas(self.vboxbase)

        self.vboxparadescargar.drag_dest_set(gtk.DEST_DEFAULT_ALL,
            targets, gtk.gdk.ACTION_MOVE)
        self.vboxparadescargar.connect("drag-drop", self.drag_drop)
        self.vboxvideos.drag_dest_set(gtk.DEST_DEFAULT_ALL,
            targets, gtk.gdk.ACTION_MOVE)
        self.vboxvideos.connect("drag-drop", self.drag_drop)

    def drag_drop(self, destino, drag_context, x, y, cosas):
        
        objeto = drag_context.get_source_widget()
        if objeto.get_parent() == destino: return

        objeto.get_parent().remove(objeto)
        destino.pack_start(objeto, False, False, 1)

        if destino == self.vboxparadescargar:
            tooltips = gtk.Tooltips()
            text = "Arrastra Hacia La Izquierda para Quitarlo de las Descargas"
            tooltips.set_tip(objeto, text, tip_private=None)
        elif destino == self.vboxvideos:
            tooltips = gtk.Tooltips()
            text = "Arrastra Hacia La Derecha para Agregarlo a Descargas"
            tooltips.set_tip(objeto, text, tip_private=None)

    def delete_event(self, widget, event, data=None):
        self.salir()
        return False

    def salir(self, widget= None, event= None):
        G.close()
        sys.exit(0)

targets = [("Moviendo", gtk.TARGET_SAME_APP, 1)]
