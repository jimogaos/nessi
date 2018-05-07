#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------
# Filename: subvalley_inversion.py
#   Author: Damien Pageot
#    Email: nessi.develop@protonmail.com
#
# Copyright (C) 2018 Damien Pageot
# ------------------------------------------------------------------
"""
Inversion of Rayleigh dispersion diagrams using PSO.
:copyright:
    Damien Pageot (nessi.develop@protonmail.com)
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
from mpi4py import MPI

from nessi.io import SUdata


# ------------------------------------------------------------------
# >> Initialize MPI
# ------------------------------------------------------------------

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


# ------------------------------------------------------------------
# >> Reference data
# ------------------------------------------------------------------

# One reference data is assigned to each slave.
if rank != 0:
    sufile = 'data/dobsz'+str(rank-1).zfill(2)+'.su'
    dobsz = SUdata()
    dobsz.read(sufile)


# ------------------------------------------------------------------
# >> Get information from SU header
# ------------------------------------------------------------------

# Get the source and receiver positions.
if rank != 0:
    
    # Get scale for coordinates
    scalco = dobsz.header[0]['scalco']
    if scalco < 0:
        scale = -1./float(scalco)
    else:
        scale = float(scalco)
    
    # Get the source position
    sx = dobsz.header[0]['sx']*scale
    sz = dobsz.header[0]['sy']*scale
    
    # Get the receiver line
    nrec = len(dobsz.header)    
    acq = np.zeros((nrec, 2), dtype=np.float32)
    acq[:, 0] = dobsz.header[:]['gx']*scale
    acq[:, 1] = dobsz.header[:]['gy']*scale


# >> Get time sampling
if rank != 0:
    ns = dobsz.header[0]['ns']
    dts = dobsz.header[0]['dt']/1000000.
    tmax = float(ns-1)*dts
    
    
# ------------------------------------------------------------------
# >> Define modeling parameters
# ------------------------------------------------------------------

if rank != 0:

    # >> Run parameters
    runpar = {'name': 'subvalley',
            'tmax': tmax, 'dt': 0.000005, # Time marching 
            'snap': 0, 'dtsnap': 0.001}   # Snapshots

    # >> Model grid parameters
    modpar = {'n1': 51, 'n2': 301, 'dh': 0.5, # Grid dimensions
            'ifsurf': 1, 'npml': 20, 'apml': 1200., 'ppml': 8} # Boundary conditions

    # >> Acquisition parameters
    acqpar = {'sx': sx, 'sy': sz, # Source parameters
            'f0': 15., 't0': 0.1, 'spread': -1, 'type': 2,
            'acquisition': acq, 'dts': dts} # Receiver file name and data sampling


# ------------------------------------------------------------------
# >> Reference dispersion diagrams
# ------------------------------------------------------------------

# Calculating the dispersion diagrams
if rank != 0:
    disp = dobsz.masw(vmin=200., vmax=1200., dv=5., fmin=10., fmax=50.)
    plt.imshow(disp, aspect='auto', cmap='jet')
    plt.show()