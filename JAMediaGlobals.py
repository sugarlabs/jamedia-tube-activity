#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaGlobals.py por:
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

import gtk, os

DIRECTORIO_BASE = os.path.dirname(__file__)
ICONOS = os.path.join(DIRECTORIO_BASE, "Iconos/")

if not os.path.exists(os.path.join(os.environ["HOME"], "JAMediaDatos")):
    os.mkdir(os.path.join(os.environ["HOME"], "JAMediaDatos"))
    os.chmod(os.path.join(os.environ["HOME"], "JAMediaDatos"), 0755)
DIRECTORIO_YOUTUBE = os.path.join(os.environ["HOME"], "JAMediaDatos", "YoutubeVideos")
if not os.path.exists(DIRECTORIO_YOUTUBE):
    os.mkdir(DIRECTORIO_YOUTUBE)
    os.chmod(DIRECTORIO_YOUTUBE, 0755)

# Versiones viejas de gtk no funcionan si no se usa 0 a 65000. Ejem: 122*65000/255= 26000
GRIS= gtk.gdk.Color(60156, 60156, 60156, 1)
AMARILLO= gtk.gdk.Color(65000,65000,40275,1)
#VERDE= gtk.gdk.Color("#00ff00")
NARANJA= gtk.gdk.Color(65000,26000,0,1)
BLANCO= gtk.gdk.Color(65535, 65535, 65535,1)
NEGRO= gtk.gdk.Color(0, 0, 0, 1)
CELESTE= gtk.gdk.Color(63000, 65535, 65535,1)

WIDTH= 800
HEIGHT= 600
BUTTONS= 45

def close():
    for archivo in os.listdir(DIRECTORIO_YOUTUBE):
        tempfile = os.path.join(DIRECTORIO_YOUTUBE, archivo)
        if os.path.exists(tempfile): os.chmod(tempfile, 0755)
        