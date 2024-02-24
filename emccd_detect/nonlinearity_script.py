# -*- coding: utf-8 -*-
"""Example script for EMCCDDetect calls."""

import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import pandas as pd

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

def nonlinearityFactor(c_init,em_gain):
    from scipy.interpolate import interp1d
    
    # Specify filename containing nonlinearity data
    nonlin_df =  pd.read_csv('nonlin_estimate.csv') #'nonlin_of_1.csv') #
    
    # Extract the magnitudes covered, the gains covered
    marks = np.array(nonlin_df.iloc[1:,0])
    gains_avail = np.float64(np.array(nonlin_df.columns[1:]))
    
    # Find the gain covered that is nearest to specified em_gain
    nearest_gain = interp1d(gains_avail,gains_avail,kind='nearest')
    gain_used = nearest_gain(em_gain)
    g_u_idx = np.searchsorted(gains_avail, gain_used)
    
    # Extract the nonlinearity factors relevant to the gain being used
    nonlins_known = np.array(nonlin_df.iloc[1:,g_u_idx+1])
    
    # From this data, interpolate the nonlinearity factor for each pixel
    c_flat = c_init.flatten()
    nl_flat = np.interp(c_flat,marks,nonlins_known)
    nl = nl_flat.reshape(c_init.shape)
    c_final = np.multiply(c_init,nl)
    return nl, c_final

if __name__ == '__main__':
    exposureTimes = np.array([2,5,7],dtype=int) #np.array([1],dtype=int) #
    numFrames = 48 #1 #
    display = 1
    save = 1
    # Set up some inputs here
    here = os.path.abspath(os.path.dirname(__file__))
    # Get fluxmap
    fits_path = Path(here, 'data', 'Fluxmap_HLCb1_0magG0V.fits') #'flat1k.fits') # 'sci_fluxmap.fits') #
    master_fluxmap = fits.getdata(fits_path).astype(float)  # (photons/pix/s for 0 mag)
    mag = 4 # Magnitude of star we're actually using
    fluxmap = master_fluxmap #* 10**(-0.4*(mag))
    # Put fluxmap in 1024x1024 image section
    full_fluxmap = np.zeros((1024, 1024)).astype(float)
    full_fluxmap[0:fluxmap.shape[0], 0:fluxmap.shape[1]] = fluxmap
    # Slow part only needs to be done first time:
    if 'emccd' not in locals():
        from emccd_detect.emccd_detect import EMCCDDetect, emccd_detect
        # For the simplest possible use of EMCCDDetect, use its defaults
        emccd = EMCCDDetect()
        # If you are using Python<=3.9, you can also apply CTI to the frame.  If
        # you have Python>3.9, this will not work if you are using the arcticpy
        # installation that was included with this emccd_detect package. Below is
        # how you could apply CTI.
        # See (<https://github.com/jkeger/arcticpy/tree/row_wise/arcticpy>) for
        # details on the optional inputs to add_cti() so that you can specify
        # something meaningful for the EMCCD you have in mind.
        # (using "try" so that this script still runs in the case that arcticpy
        # is not viable.  In that case, running this method update_cti()
        # will not work.)
        try:
            emccd.update_cti()
        except:
            pass
    # Now the action begins:
    for frametime in exposureTimes:
        for iframe in range(1,numFrames+1):
            # Simulate only the fluxmap
            sim_sub_frame = emccd.sim_sub_frame(fluxmap, frametime)
            # Simulate the full frame (surround the full fluxmap with prescan, etc.)
            sim_full_frame = emccd.sim_full_frame(full_fluxmap, frametime)
            # to turn off CTI application to future frames made with the same class
            # instance (If arcticpy not viable, trying to run unset_cti() will not
            # work):
            try:
                emccd.unset_cti()
            except:
                pass
        
            # For more control, each of the following parameters can be specified
            # Custom metadata path, if the user wants to use a different metadata file
            meta_path = Path(here, 'emccd_detect', 'util', 'metadata.yaml')
            # Note that the defaults for full_well_serial and eperdn are specified in
            # the metadata file
            em_gain=1.
            emccd = EMCCDDetect(
                em_gain=em_gain,
                full_well_image=60000.,  # e-
                full_well_serial=100000.,  # e-
                dark_current=.00028,  # e-/pix/s
                cic=0.02,  # e-/pix/frame
                read_noise=140.,  # e-/pix/frame
                bias= 3000.,  # e-
                qe=0.9,
                cr_rate=0, #5.,  # hits/cm^2/s
                pixel_pitch=13e-6,  # m
                eperdn=8.5,
                nbits=14,
                numel_gain_register=604,
                meta_path=meta_path
            )
            
            # # Simulate only the fluxmap
            # sim_sub_frame = emccd.sim_sub_frame(fluxmap, frametime)
            # # Determine the nonlinearity of this array
            # subframe_nonlinearity, subframe_x_nonlin = nonlinearityFactor(sim_sub_frame, em_gain)
            
            # Simulate the full frame (surround the full fluxmap with prescan, etc.)
            sim_full_frame = emccd.sim_full_frame(full_fluxmap, frametime)
            # Add the nonlinearity:
            fullframe_nonlinearity, fullframe_x_nonlin = nonlinearityFactor(sim_full_frame, em_gain)
            
            # Save Full Frame With Nonlinearity to FITS
            if save:
                fitsfile = fits.HDUList([fits.PrimaryHDU(fullframe_x_nonlin)])
                fitsfile.writeto('./Output/Nonlinearity_'+str(frametime)+'s_'+str(iframe)+'.fits',overwrite=True)#Linear_'+str(frametime)+'s_'+str(iframe)+'.fits',overwrite=True)
        
            # # The class also has some convenience functions to help with inspecting the
            # # simulated frame
            # # Get a gain divided, bias subtracted frame in units of e-
            # frame_e = emccd.get_e_frame(sim_full_frame)
            # # Return just the 1024x1024 region of a full frame
            # image = emccd.slice_fluxmap(sim_full_frame)
            # # Return the prescan region of a full frame
            # prescan = emccd.slice_prescan(sim_full_frame)
        
        
            # # For legacy purposes, the class can also be called from a function wrapper
            # sim_old_style = emccd_detect(fluxmap, frametime, em_gain=5000.)
        
            # Plot images
            # imagesc(full_fluxmap, 'Input Fluxmap')
            # imagesc(sim_sub_frame, 'Output Sub Frame')
            # imagesc(subframe_x_nonlin, 'Output Sub Frame w Nonlinearity')
            # imagesc(subframe_nonlinearity, 'Nonlinearity of Sub Frame')
            # imagesc(sim_full_frame, 'Output Full Frame')
            if iframe == 1 & display:
                imagesc(fullframe_x_nonlin, 'Output Full Frame w Nonlinearity @ '+str(frametime)+'s exposure')
            # imagesc(fullframe_nonlinearity, 'Nonlinearity of Full Frame')
            # plt.show()
