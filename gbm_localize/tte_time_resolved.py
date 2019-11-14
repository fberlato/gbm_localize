import matplotlib
matplotlib.use('Agg')

from mpi4py import MPI
mpi=MPI.COMM_WORLD
rank = mpi.Get_rank()

from astropy.coordinates import SkyCoord
from gbmgeometry import *
#import matplotlib.pyplot as plt
import numpy as np
from trigdat_reader import TrigReader
from threeML import *
from glob import glob
from collections import OrderedDict
import warnings
import os
import sys


import gbm_drm_gen as drm
#from astropy.time import Time

def get_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


trigger='190829830'

spectrum = 'band'
suffix='_tte_'+str(spectrum)


string_path=os.getcwd()


#os.chdir('/home/franz/grb_results/results/'+trigger+'/')

det_list = ['n6','n7','n8','n9','nb','b1']
#gbm_dl = download_GBM_trigger_data('bn'+trigger, detectors=det_list) 

#for bayesblocks only
bayes_blocks = True
brightest_det = 'n7'
bblocks_start = 40.
bblocks_stop = 25.

bkg_int = ['-100--10','80-200']
src_int = ['49-54']
rsp_time = 51.

det_ts = OrderedDict()

for det in det_list:                                                                                                                               
    #ts = TimeSeriesBuilder.from_gbm_tte(det,gbm_dl[det]['tte'],gbm_dl[det]['rsp'] )
    tte_file = glob('glg_tte_'+det+'_bn'+trigger+'_v0*.fit')[0]                 
    rsp_file = glob('glg_cspec_'+det+'_bn'+trigger+'_v0*.rsp*')[0]
    
    ts = TimeSeriesBuilder.from_gbm_tte(det, tte_file, rsp_file)
    ts.set_background_interval(*bkg_int)
    ts.set_active_time_interval(*src_int)
    det_ts[det] = ts


if bayes_blocks == True:
    det_ts[brightest_det].create_time_bins(bblocks_start, bblocks_stop, 'bayesblocks')
    for det in det_list:
        if det != brightest_det:
            det_ts[det].create_time_bins(start=det_ts[brightest_det].bins.starts, stop=det_ts[brightest_det].bins.stops, method='custom')


            
det_rsp = OrderedDict()

for det in det_list:
    rsp = drm.DRMGenTTE(tte_file=glob('glg_tte_'+det+'_bn'+trigger+'_v0*.fit')[0],
                        trigdat=glob('glg_trigdat_all_bn'+trigger+'_v0*.fit')[0],
                        mat_type=2,                                                                                                           
                        cspecfile=glob('glg_cspec_'+det+'_bn'+trigger+'_v0*.pha')[0])
    det_rsp[det] = rsp

    
for i in range(len(det_ts[brightest_det])):
    
    if det_ts[brightest_det].significance[i] >= 5:

        for det in det_list:
            src_int = [str(det_ts[brightest_det].bins.start[i])+'-'+str(det_ts[brightest_det].bins.stop[i])]
            rsp_time = (det_ts[brightest_det].bins.start[i] + det_ts[brightest_det].bins.stop[i])/2
            det_ts[det].set_active_time_interval(*src_int)

            
        det_sl = OrderedDict()

        for det in det_ts.keys():
            if det != 'b0' and det != 'b1':
                sl = det_ts[det].to_spectrumlike()
                sl.set_active_measurements('8.1-900')
                det_sl[det] = sl
            else:
                sl = det_ts[det].to_spectrumlike()
                sl.set_active_measurements('250-30000')
                det_sl[det] = sl


        det_bl = OrderedDict()

        for det in det_list:
            det_bl[det] = drm.BALROGLike.from_spectrumlike(det_sl[det], rsp_time, det_rsp[det], free_position=True)


        data_tte = DataList(*det_bl.values())


        if spectrum == 'band':

            band = Band()                                                                                                                             
            band.K.prior = Log_uniform_prior(lower_bound=1e-5, upper_bound=500)                                                                       
            band.xp.prior = Log_uniform_prior(lower_bound=10, upper_bound=1e4)                                                                        
            band.alpha.set_uninformative_prior(Uniform_prior)                                                                                         
            band.beta.set_uninformative_prior(Uniform_prior)   

            ra, dec = 0, 0
            ps = PointSource('grb',ra, dec, spectral_shape=cpl)
            model = Model(ps)
            
        elif spectrum == 'cpl':
            
            cpl = Cutoff_powerlaw()                                                                                                                 
            cpl.K.prior = Log_uniform_prior(lower_bound=1e-3, upper_bound=500)                                                                   
            cpl.xc.prior = Log_uniform_prior(lower_bound=10, upper_bound=1e4)                                                                     
            cpl.index.set_uninformative_prior(Uniform_prior)  

            ra, dec = 0, 0
            ps = PointSource('grb',ra, dec, spectral_shape=cpl)
            model = Model(ps)
            
        else:

            print 'ERROR: invalid spectral model!'

            
        bayes = BayesianAnalysis(model, data_tte)

        
        # MULTINEST
        wrap = [0]*len(model.free_parameters)   #not working properly
        wrap[0] = 1
        
        _ = bayes.sample_multinest(800,
                                  chain_name=string_path+'/chains/',
                                  importance_nested_sampling=False,
                                  const_efficiency_mode=False,
                                  wrapped_params=wrap,
                                  verbose=True,
                                  resume=False)


        #save MULTINEST results
        if rank == 0:
            bayes.results.write_to('loc_balrog'+suffix+'_'+str(i)+'.fits',overwrite=True)

            result = bayes.results

            # corner plot
            cc_plot = result.corner_plot_cc()
            cc_plot.savefig('cc_plot'+suffix+'_'+str(i)+'.pdf')

            # energy spectrum
            spectrum_plot = display_spectrum_model_counts(bayes, step=False);
            spectrum_plot.savefig('spectrum_plot'+suffix+'_'+str(i)+'.pdf')

        del det_sl
        del det_bl
