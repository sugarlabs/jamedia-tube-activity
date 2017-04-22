#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, commands, platform

print "Desinstalando de:", platform.platform()
print commands.getoutput('rm -r /usr/local/share/JAMediaTube')
print commands.getoutput('rm /usr/share/applications/JAMediaTube.desktop')
print commands.getoutput('rm /usr/local/bin/JAMediaTube')
print commands.getoutput('rm /usr/local/bin/JAMediaTubeUninstall')
print "JAMediaTube se ha Desinstalado Correctamente del Sistema"

