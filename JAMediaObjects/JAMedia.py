#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMedia.py por:
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

# Necesita:
#	python 2.7.1 - gtk 2.0
#	gstreamer-plugins-base
#	gstreamer-plugins-good
#	gstreamer-plugins-ugly
#	gstreamer-plugins-bad
#	gstreamer-ffmpeg

''' Para embeber el reproductor en cualquier lugar de tu interfaz gráfica:
    self.socket = gtk.Socket()
    self.add(self.socket)
    self.jamediaplayer = JAMediaPlayer()
    self.socket.add_id(self.jamediaplayer.get_id())'''

import gtk
import os
import sys
import gobject
import gst
import pygst
#import time
#import datetime
#import commands
#import subprocess
#import string
#import platform

from gettext import gettext as _
from JAMediaReproductor import JAMediaReproductor
from JAMediaLista import JAMediaLista
import JAMediaGlobals as G
#from Archivos_y_Directorios import Archivos_y_Directorios
#from JAMediaLista import JAMediaLista
from JAMediaWidgets import *

#ISOLPC = False
#if "olpc" in platform.platform(): ISOLPC = True

gobject.threads_init()
gtk.gdk.threads_init()

class JAMedia(gtk.Window):
    
    def __init__(self):
        
        super(JAMedia, self).__init__()
        
        self.set_title("JAMedia")
        self.set_icon_from_file(os.path.join(G.ICONOS, "JAMedia.png"))
        self.set_resizable(True)
        self.set_size_request(G.WIDTH, G.HEIGHT)
        self.set_border_width(2)
        self.set_position(gtk.WIN_POS_CENTER)
        #self.modify_bg(gtk.STATE_NORMAL, G.GRIS)
        
        self.socket = gtk.Socket()
        self.add(self.socket)
        self.jamediaplayer = JAMediaPlayer()
        self.socket.add_id(self.jamediaplayer.get_id())
        self.show_all()
        self.realize()
        
        #self.add_events(gtk.gdk.ALL_EVENTS_MASK)
        self.connect("delete_event", self.delete_event)
        self.connect("destroy", self.salir)
        
    def delete_event(self, widget = None, event = None, data = None):
        
        self.salir()
        return False
    
    def salir(self, widget = None):
        
        sys.exit(0)
        
class JAMediaPlayer(gtk.Plug):
    
    __gsignals__ = {'OK':(gobject.SIGNAL_RUN_FIRST,
        gobject.TYPE_NONE, [])}
    
    def __init__(self):
        
        gtk.Plug.__init__(self, 0L)
        
        self.pantalla = None
        self.player = None
        self.barradeprogreso = None
        self.volumen = None
        self.toolbar_list = None
        self.lista_de_reproduccion = None
        self.controlesrepro = None
        self.hbox_barra_progreso = None
        self.vbox_lista_reproduccion = None
        
        #self.set_layout()
        self.show_all()
        self.realize()
        
        self.connect("embedded", self.embed_event)
        
        self.item_activo_en_lista = None
        self.controlesview = True
        
        gobject.idle_add(self.setup_init)
        
    def set_layout(self):
        
        self.pantalla = Superficie_de_Reproduccion()
        self.barradeprogreso = Barra_de_Progreso()
        self.volumen = ButtonJAMediaMixer()
        self.toolbar_list = ToolbarLista()
        self.lista_de_reproduccion = JAMediaLista()
        self.controlesrepro = Barra_de_Reproduccion()
        
        hpanel = gtk.HPaned()
        
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        #vbox.pack_start(self.info_grabar, False, False, 0)
        vbox.pack_start(self.pantalla, True, True, 0)
        #vbox.pack_start(self.info_reproduccion, False, False, 0)
        hbox.pack_start(self.barradeprogreso, True, True, 0)
        hbox.pack_start(self.volumen, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        hpanel.pack1(vbox, resize = False, shrink = True)
        
        vbox = gtk.VBox()
        vbox.pack_start (self.toolbar_list, False, False, 0)
        vbox.pack_start(self.lista_de_reproduccion, True, True, 0)
        #vbox.pack_start(self.barradeopcionesuno, False, False, 0)
        vbox.pack_end(self.controlesrepro, False, False, 0)
        hpanel.pack2(vbox, resize = False, shrink = False)
        
        self.hbox_barra_progreso = hbox
        self.vbox_lista_reproduccion = vbox
        
        hpanel.show_all()
        
        self.add(hpanel)
        self.volumen.jamediamixer.set_transient_for(self)
        self.volumen.jamediamixer.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
    def setup_init(self):
        
        self.set_layout()
        self.player = JAMediaReproductor(self.pantalla.window.xid)
        self.toolbar_list.connect("load_list", self.load_list)
        #self.toolbar_list.connect("add_stream", self.add_stream)
        self.lista_de_reproduccion.connect("play", self.load_and_play)
        self.lista_de_reproduccion.connect("getmenu", self.set_menu_list)
        self.controlesrepro.connect("activar", self.activar)
        self.barradeprogreso.connect("change-value", self.changevalueprogressbar)
        self.player.connect("endfile", self.endfile)
        self.player.connect("estado", self.cambioestadoreproductor)
        self.player.connect("newposicion", self.update_progress)
        self.pantalla.connect("ocultar_controles", self.ver_controles)
        #self.pantalla.connect('expose-event', self.paint_pantalla)
        self.load_list(None, 0)
        self.emit("OK")
        
    def ver_controles(self, widget, valor):
        
        if valor == self.controlesview:
            return
        else:
            self.controlesview = valor
            
        if self.controlesview:
            self.vbox_lista_reproduccion.hide()
            self.hbox_barra_progreso.hide()
            #self.info_grabar.hide()
            #self.info_reproduccion.hide()
        else:
            self.vbox_lista_reproduccion.show()
            self.hbox_barra_progreso.show()
            #self.info_grabar.show()
            #self.info_reproduccion.show()
    '''
    def paint_pantalla(self, widget, event):
        if not self.videoenfuente or self.item_activo_en_lista.tipo == "Radio" \
            or self.mplayer_server.get_estado() == "stoped Audio_Video":
            self.pantalla.paint()
        return True'''

    # Barra de Reproduccion >>>
    def activar(self, widget= None, senial= None):
        
        if senial == "atras":
            #self.pantalla.expose()
            self.lista_de_reproduccion.previous()
        elif senial == "siguiente":
            #self.pantalla.expose()
            self.lista_de_reproduccion.next()
        elif senial == "stop":
            self.player.stop()
            self.controlesrepro.set_paused()
            #self.pantalla.expose()
        elif senial == "pausa-play":
            if self.player.estado == gst.STATE_PLAYING:
                self.player.pause()
            else:
                self.player.play()
    # <<< Barra de Reproduccion
    
    # Reproductor >>>
    def endfile(self, widget = None, senial = None):
        
        self.controlesrepro.set_paused()
        #self.pantalla.expose()
        self.lista_de_reproduccion.next()
        
    def cambioestadoreproductor(self, widget = None, senial = None):
        
        if "playing" in senial:
            self.controlesrepro.set_playing()
        elif "paused" in senial or "None" in senial:
            self.controlesrepro.set_paused()
            
    def update_progress(self, objetoemisor, valor):
        
        self.barradeprogreso.set_progress(float(valor))
    # <<< Reproductor
    
    def changevalueprogressbar(self, widget= None, valor= None):
        
        self.player.set_position(valor)
        
    def embed_event(self, widget):
        
        print "JAMediaPlayer embebido"
            
    # JAMediaLista >>>
    def load_list(self, widget, indice):
        
        # elemento = [None, texto, url, tipo]
        # El parámetro None, se agregó para los previews de la lista (JAMedia-10),
        # Para estandarizar todo con JAMediaTube y JAMediaVideo.
        self.toolbar_list.boton_agregar.hide()
        self.item_activo_en_lista = None
        '''
        if indice == 0:
            self.toolbar_list.boton_agregar.hide()
            tipo = "Radio"
            lista = []
            for x in self.Lista_de_Radios:
                elem = x.split(",")
                texto = elem[0]
                url = elem[1]
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text(_("JAMedia Radio"))
        elif indice == 1:
        # llenar lista con TV
            self.toolbar_list.boton_agregar.hide()
            tipo = "TV"
            lista = []
            for x in self.Lista_de_Television:
                elem = x.split(",")
                texto = elem[0]
                url = elem[1]
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text(_("JAMedia TV"))
        elif indice == 2:
        # llenar lista con Streaming del usuario
            self.toolbar_list.boton_agregar.show()
            tipo = "Radio"
            lista = []
            for x in self.Lista_de_MisRadios:
                elem = x.split(",")
                texto = elem[0]
                url = elem[1]
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text(_("Mis Emisoras"))
        elif indice == 3:
        # llenar lista con Streaming del usuario
            self.toolbar_list.boton_agregar.show()
            tipo = "TV"
            lista = []
            for x in self.Lista_de_MisTelevision:
                elem = x.split(",")
                texto = elem[0]
                url = elem[1]
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text(_("Mis Canales"))
        elif indice == 4:
        # llenar lista con archivos de videos en el directorio de jamedia
            archivos = sorted(os.listdir(G.DIRECTORIO_MIS_ARCHIVOS))
            tipo = "Audio_Video"
            lista = []
            for texto in archivos:
                url = os.path.join(G.DIRECTORIO_MIS_ARCHIVOS, texto)
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text(_("Mis Archivos"))
        elif indice == 5:
            archivos = sorted(os.listdir(G.AUDIO_JAMEDIA_VIDEO))
            tipo = "Audio_Video"
            lista = []
            for texto in archivos:
                url = os.path.join(G.AUDIO_JAMEDIA_VIDEO, texto)
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text(_("Audio-JAMediaVideo"))
        elif indice == 6:
            archivos = sorted(os.listdir(G.VIDEO_JAMEDIA_VIDEO))
            tipo = "Audio_Video"
            lista = []
            for texto in archivos:
                url = os.path.join(G.VIDEO_JAMEDIA_VIDEO, texto)
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text(_("Video-JAMediaVideo"))
        elif indice == 7:
            archivos = sorted(os.listdir(G.DIRECTORIO_YOUTUBE))
            tipo = "Audio_Video"
            lista = []
            for texto in archivos:
                url = os.path.join(G.DIRECTORIO_YOUTUBE, texto)
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text(_("JAMediaTube"))
        elif indice == 8:
            Selector_de_Archivos(self)
        else:
            print "hay acciones sin asignar para opciones del combo"
        return False'''
    
        if indice == 0:
            archivos = sorted(os.listdir(G.DIRECTORIO_YOUTUBE))
            tipo = "Audio_Video"
            lista = []
            for texto in archivos:
                url = os.path.join(G.DIRECTORIO_YOUTUBE, texto)
                elemento = [None, texto, url, tipo]
                lista.append(elemento)
            self.lista_de_reproduccion.set_lista(lista)
            self.toolbar_list.label.set_text("JAMediaTube")
        #elif indice == 1:
        #	Selector_de_Archivos(self)
        else:
            print "hay acciones sin asignar para opciones del combo"
        return False
    
    def load_and_play(self, widget, item):
        
        self.item_activo_en_lista = item
        #self.mplayer_server.quit(None)
        #if ISOLPC: self.videoenfuente = True # por compatibilidad con sugar
        #self.mplayer_server.play(self.item_activo_en_lista.url, self.item_activo_en_lista.tipo)
        #def play(self, widget= None, url= None):
        #self.pantalla.expose()
        self.player.load(item.url)
        #self.menureproduccion.label.set_text(url)
        
    def set_menu_list(self, widget, item, boton, pos, tiempo):
        
        menu = gtk.Menu()
        if item.tipo == "Audio_Video":
            quitar = gtk.MenuItem(_("Quitar de la Lista"))
            menu.append(quitar)
            quitar.connect_object("activate", self.set_accion_archivos, item, "Quitar")
            #Plectura, Pescritura, Pejecucion = self.origenes_de_datos.verificar_permisos(item.url)
            Plectura, Pescritura, Pejecucion = G.verificar_permisos(item.url)
            origen = "%s%s" % (os.path.dirname(item.url), "/")
            #destino = "%s%s" % (G.DIRECTORIO_MIS_ARCHIVOS, "/")
            #if Plectura and origen != destino:
                #copiar = gtk.MenuItem(_("Copiar a JAMedia"))
                #menu.append(copiar)
                #copiar.connect_object("activate", self.set_accion_archivos, item, "Copiar")
            #if Pescritura and origen != destino:
                #mover = gtk.MenuItem(_("Mover a JAMedia"))
                #menu.append(mover)
                #mover.connect_object("activate", self.set_accion_archivos, item, "Mover")
            if Pescritura:
                borrar = gtk.MenuItem(_("Borrar el Archivo"))
                menu.append(borrar)
                borrar.connect_object("activate", self.set_accion_archivos, item, "Borrar")
        '''
        else:
            quitar = gtk.MenuItem(_("Quitar de la Lista"))
            menu.append(quitar)
            quitar.connect_object("activate", self.set_accion_stream, item, "Quitar")
            if self.toolbar_list.label.get_text() == _("JAMedia Radio")\
            or self.toolbar_list.label.get_text() == _("JAMedia TV"):
                copiar = gtk.MenuItem(_("Copiar a mis Streaming"))
                menu.append(copiar)
                copiar.connect_object("activate", self.set_accion_stream, item, "Copiar")
                mover = gtk.MenuItem(_("Mover a mis Streaming"))
                menu.append(mover)
                mover.connect_object("activate", self.set_accion_stream, item, "Mover")
            borrar = gtk.MenuItem(_("Eliminar Streaming"))
            menu.append(borrar)
            borrar.connect_object("activate", self.set_accion_stream, item, "Borrar")
            grabar = gtk.MenuItem(_("Grabar Transmisión"))
            menu.append(grabar)
            grabar.connect_object("activate", self.set_accion_stream, item, "Grabar")'''
        menu.show_all()
        gtk.Menu.popup(menu, None, None, None, boton, tiempo)
        
    def set_accion_archivos(self, item, accion):
        
        '''
        # accion == "Copiar":
            dialog = StandarDialog(self, "Mensaje JAMedia",
                _("¿ Confirmas que Deseas Copiar el Archivo ?"))
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                #self.origenes_de_datos.copiar_archivo_JAMedia_Video(item.url)
                G.copiar_archivo_JAMedia_Video(item.url)'''
        if accion == "Borrar":
            dialog = StandarDialog(self, "Mensaje JAMedia",
                _("¿ Confirmas que Deseas Borrar el Archivo ?"))
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                #self.origenes_de_datos.borrar_archivo_JAMedia(item.url)
                G.borrar_archivo_JAMedia(item.url)
                item.destroy()
            '''
            elif accion == "Mover":
                dialog = StandarDialog(self, "Mensaje JAMedia", _("¿ Confirmas que Deseas Mover el Archivo ?"))
                response = dialog.run()
                dialog.destroy()
                if response == gtk.RESPONSE_YES:
                    #self.origenes_de_datos.mover_archivo_JAMedia(item.url)
                    G.mover_archivo_JAMedia(item.url)
                    item.destroy()'''
        elif accion == "Quitar":
            dialog = StandarDialog(self, "Mensaje JAMedia",
                _("¿ Confirmas que deseas Quitar de la Lista ?"))
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                item.destroy()
        # <<< JAMediaLista
        
if __name__=="__main__":
    JAMedia()
    gtk.main()
    