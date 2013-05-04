#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  download.py
#
#  Copyright 2013 Antergos
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  Antergos Team:
#   Alex Filgueira (faidoc) <alexfilgueira.antergos.com>
#   Raúl Granados (pollitux) <raulgranados.antergos.com>
#   Gustau Castells (karasu) <karasu.antergos.com>
#   Kirill Omelchenko (omelcheck) <omelchek.antergos.com>
#   Marc Miralles (arcnexus) <arcnexus.antergos.com>
#   Alex Skinner (skinner) <skinner.antergos.com>

import pm2ml
import sys
import subprocess

ARIA2_DOWNLOAD_ERROR_EXIT_CODES = (0, 2, 3, 4, 5)

def download_packages(package_names):
    pacman_conf = "/etc/pacman.conf"
    pacman_cache = "/var/cache/pacman/pkg"
    
    args = str("-c %s" % pacman_conf).split() 
    args += package_names
    args += ["--noconfirm"]
    args += "-r -p http -l 50".split()
    
    pargs, conf, download_queue, not_found, missing_deps = pm2ml.build_download_queue(args)
    
    #print(pargs.output_dir)
    
    metalink = pm2ml.download_queue_to_metalink(
        download_queue,
        output_dir=pargs.output_dir,
        set_preference=pargs.preference
    )

    '''
    print(metalink)

    if not_found:
        sys.stderr.write('Not found:\n')
        for nf in sorted(not_found):
            sys.stderr.write('  %s\n' % nf)
  
    if missing_deps:
        sys.stderr.write('Unresolved dependencies:\n')
        for md in sorted(missing_deps):
            sys.stderr.write('  %s\n' % md)
    '''
    
    aria2_args = ["allow-overwrite=true",
        "always-resume=false",
        "auto-file-renaming=false",
        "check-integrity=true",
        "conditional-get=true",
        "continue=false",
        "file-allocation=none",
        "log-level=warn",
        "max-concurrent-downloads=50",
        "max-connection-per-server=5",
        "min-split-size=5M",
        "split=10",
        "show-console-readout=false",
        "--dir=%s" % pacman_cache]
    
    aria2_cmd = ['/usr/bin/aria2c', '--metalink-file=-', ] + aria2_args
    
    #print(aria2_cmd)
    
    aria2c_p = subprocess.Popen(aria2_cmd, stdin=subprocess.PIPE)
    aria2c_p.communicate(input=str(metalink).encode())
    e = aria2c_p.wait()
    #if e not in ARIA2_DOWNLOAD_ERROR_EXIT_CODES:
    #    print('error: aria2c exited with %d' % e)

if __name__ == '__main__':
    download_packages(["vim"])