import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import gbmgeometry as geo
import numpy as np
import os
from astropy.coordinates import SkyCoord
from trigdat_reader import TrigReader
import warnings                                                                                                                                
warnings.simplefilter('ignore') 

import pickle

all_det_list = ['n0','n1','n2','n3','n4','n5','n6','n7','n8','n9','na','nb','b0','b1']


def get_occulted_detectors(source_coord, trigdat_file):

    assert type(source_coord) is SkyCoord , 'ERROR: please provide a valid instance of astropy SkyCoord!'
    assert os.path.isfile(trigdat_file) , 'ERROR: invalid path for trigdat file!'
    
    trigdat = TrigReader(trigdat_file)
    #quaternion and spacecraft position at the trigger time
    sc_data = trigdat.quats_sc_time_burst()
    fermi = geo.Fermi(quaternion=sc_data[0], sc_pos=sc_data[1])

    #get the spacecraft reference frame
    sc_frame = fermi._frame

    #add rays connecting source and detectors
    fermi.add_ray(source_coord.transform_to(sc_frame))

    #dictionary with the occulted detectors
    occulted_dets = fermi.compute_intersections()

    fig = fermi.plot_fermi(with_rays=True, with_intersections=True)
        
    return occulted_dets, fig



