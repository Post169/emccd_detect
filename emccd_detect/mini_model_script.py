# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 07:26:33 2024

@author: david
"""

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.signal import sawtooth
import matplotlib.pyplot as plt

def imagesc(data, title=None, vmin=None, vmax=None, cmap='viridis',
            aspect='equal', colorbar=True):
    """Plot a scaled colormap."""
    fig, ax = plt.subplots()
    im = ax.imshow(data, vmin=vmin, vmax=vmax, cmap=cmap, aspect=aspect,
                   origin='lower')

    if title:
        ax.set_title(title)
    if colorbar:
        fig.colorbar(im, ax=ax)

    return fig, ax

# c = np.array([[204,306,364,400,281],
#               [481,349,269,432,371],
#               [419,328,259,167,115],
#               [234,282,318,299,314],
#               [489,385,238,127,115]])*10
# c = np.ones([5,5])*600
size = 400
c = np.ones([size,1]) * np.linspace(500, 6998, size)
nonlin_df =  pd.read_csv('nonlin_array.csv')
# marks = np.array([100,200,300,400,500])
marks = np.array(nonlin_df.iloc[1:,0])
em_gain = 1
gains_avail = np.float64(np.array(nonlin_df.columns[1:]))
nearest_gain = interp1d(gains_avail,gains_avail,kind='nearest')
gain_used = nearest_gain(em_gain)
g_u_idx = np.searchsorted(gains_avail, gain_used)
# nonlin = np.array([1.1,-1.8,-1.3,1.4,1.6])
nonlins_known = np.array(nonlin_df.iloc[1:,g_u_idx+1])

c_flat = c.flatten()
nl_flat = np.interp(c_flat,marks,nonlins_known)
nl = nl_flat.reshape([size,size])
e = np.multiply(c,nl)
ratio = e/c


imagesc(c,'c')
imagesc(e,'e')
imagesc(ratio,'ratio')