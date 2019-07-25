import matplotlib
matplotlib.use('Agg')

from mpi4py import MPI
mpi=MPI.COMM_WORLD
rank = mpi.Get_rank()

from astropy.coordinates import SkyCoord
import astropy.coordinates as coord
import astropy.units as u
from gbmgeometry import *
import pandas as pd
from astropy.table import Table
import matplotlib.pyplot as plt
import numpy as np
from trigdat_reader import TrigReader
from threeML import *
from glob import glob
import warnings
warnings.simplefilter('ignore')
import os
import sys
import random

import gbm_drm_gen as drm
#from astropy.time import Time

def get_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


trigger='190525032'

suffix='_sun_tte'


string_path=os.getcwd()


#os.chdir('/home/franz/grb_results/results/'+trigger+'/')

det_list = ['n6','n7','n8','n9','na','nb','b1']
gbm_dl = download_GBM_trigger_data('bn'+trigger, detectors=det_list) 


bkg_int = ['-100--10','60-100']
src_int = ['0.5-2.0']#['-0.04-0.23']

det_ts = []

for det in det_list:                                                                                                                               
    ts = TimeSeriesBuilder.from_gbm_tte(det,gbm_dl[det]['tte'],gbm_dl[det]['rsp'] )
    ts.set_background_interval(*bkg_int)
    ts.set_active_time_interval(*src_int)
    det_ts.append(ts)



det_sl = []

for series in det_ts:
    if series._name != 'b0' and series._name != 'b1':
        sl = series.to_spectrumlike()
        sl.set_active_measurements('8.1-900')
        det_sl.append(sl)
    else:
        sl = series.to_spectrumlike()
        sl.set_active_measurements('250-30000')
        det_sl.append(sl)



det_rsp = []

for det in det_list:
    rsp = drm.DRMGenTTE(tte_file=glob('glg_tte_'+det+'_bn'+trigger+'_v0*.fit')[0],                                                                                 trigdat=glob('glg_trigdat_all_bn'+trigger+'_v0*.fit')[0],                                                                                  mat_type=2,                                                                                                           
                        cspecfile=glob('glg_cspec_'+det+'_bn'+trigger+'_v0*.pha')[0])
    det_rsp.append(rsp)
        


det_bl = []

for i,det in enumerate(det_list):
    det_bl.append(drm.BALROGLike.from_spectrumlike(det_sl[i],0.,det_rsp[i], free_position=True))




data_tte = DataList(*det_bl)


#band = Band()                                                                                                                             
#band.K.prior = Log_uniform_prior(lower_bound=1e-5, upper_bound=500)                                                                       
#band.xp.prior = Log_uniform_prior(lower_bound=10, upper_bound=1e4)                                                                        
#band.alpha.set_uninformative_prior(Uniform_prior)                                                                                         
#band.beta.set_uninformative_prior(Uniform_prior)   

cpl = Cutoff_powerlaw()                                                                                                                 
cpl.K.prior = Log_uniform_prior(lower_bound=1e-3, upper_bound=500)                                                                   
cpl.xc.prior = Log_uniform_prior(lower_bound=10, upper_bound=1e4)                                                                     
cpl.index.set_uninformative_prior(Uniform_prior)  

ra=10.
dec=-10.

ps = PointSource('grb',ra, dec, spectral_shape=cpl)
model = Model(ps)
bayes = BayesianAnalysis(model, data_tte)

# MULTINEST
wrap = [0]*len(model.free_parameters)   #not working properly
wrap[0] = 1

_ =bayes.sample_multinest(800,
                        chain_name=string_path+'/chains/',
                        importance_nested_sampling=False,
                        const_efficiency_mode=False,
                        wrapped_params=wrap,
                        verbose=True,
                        resume=False)


#save MULTINEST results
if (rank==0):
	bayes.results.write_to(string_path+'/loc_balrog'+suffix+'.fits',overwrite=True)

res=bayes.results


# corner plot
cc_plot = res.corner_plot_cc()
cc_plot.savefig(string_path+'/cc_plot'+suffix+'.pdf')

# energy spectrum
spectrum_plot = display_spectrum_model_counts(bayes, step=False);
spectrum_plot.savefig(string_path+'/spectrum_plot'+suffix+'.pdf')

