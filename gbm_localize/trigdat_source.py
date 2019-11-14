import matplotlib
matplotlib.use('Agg')

from mpi4py import MPI
mpi=MPI.COMM_WORLD
rank = mpi.Get_rank()

from astropy.coordinates import SkyCoord
import matplotlib.pyplot as plt
import numpy as np
from trigdat_reader import TrigReader
from threeML import *
import gbmgeometry as gbmgeo
from glob import glob
import json
import os



def get_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def det_number_to_name(num):
    if num<10:
        return 'n'+str(num)
    elif num==10:
        return 'na'
    elif num==11:
        return 'nb'
    elif num==12:
        return 'b0'
    elif num==13:
        return 'b1'

def det_occultation(intersec):
    occulted=[]
    for i in range (0,14):
        # check if there is intersection between soruce ray and detector i
        if not intersec[det_number_to_name(i)][0]['point']:
            occulted.append(False)
        else:
            occulted.append(True)
    return occulted




def read_json_file(json_file):
    '''
    Reads the localization json file and returns the parameters used for the fit.
    :parameter json_file: json file with the fit parameters.
    '''
    
    with open(json_file, 'r') as data_file:                                                                                                                                                            
        json_data = data_file.read()                                                                                                                                                                   
        json_dict = json.loads(json_data)[0]                                                                                                                                                           
        
    #looks for the most recent version of the trigdat json data                                                                                                                                     
    versions = []
    
    for i in range(len(json_dict['grb_params'])):
        ver = json_dict['grb_params'][i]['version']
        
        if ver == 'tte':                                                                                                                                                                               
            versions.append(-1)                                                                                                                                                                        
            continue                                                                                                                                                                                   
        else:                                                                                                                                                                                          
            versions.append(int(ver))
                    
    vind = np.argmin(versions)                                                                                                                                                                         

    spectrum = json_dict['grb_params'][vind]['model_type']
    det_list = json_dict['grb_params'][vind]['used_detectors'].split(',')
    src_int = [str(json_dict['grb_params'][vind]['active_time_start'])+'-'+str(json_dict['grb_params'][vind]['active_time_stop'])]
    bkg_neg_int = str(json_dict['grb_params'][vind]['bkg_neg_start'])+'-'+str(json_dict['grb_params'][vind]['bkg_neg_stop'])
    bkg_pos_int = str(json_dict['grb_params'][vind]['bkg_pos_start'])+'-'+str(json_dict['grb_params'][vind]['bkg_pos_stop'])
    bkg_int = [bkg_neg_int, bkg_pos_int]

    return spectrum, det_list, src_int, bkg_int



#def write_json_file


def fit_trigdat(trigger, result_path='.', trigdat_path=None, json_file=None, spectrum=None, det_list=None, src_int=None, bkg_int=None):

                                                                                                              

    #reads the json file, but if the user provides some parameters, those override the ones from the json file
    if json_file != None:
        parameters = read_json_file(json_file)

        if spectrum == None:
            spectrum = parameters[0]
            
        if det_list == None:
            det_list = parameters[1]
            
        if src_int == None:
            src_int = parameters[2]

        if bkg_int == None:
            bkg_int = parameters[3]
        

    #check that all parameters not None
    assert spectrum != None, "ERROR: select a spectral model!"
    assert det_list != None, "ERROR: provide a detector list!"
    assert src_int != None, "ERROR: select an active source interval!"
    assert bkg_int != None, "ERROR: select a background interval!"

                                                                              
    output_name = '_'+spectrum
    
    if trigdat_path == None:
        data_file = glob('glg_trigdat_all_bn'+trigger+'_v0*.fit')[0]       
    else:
        data_file = trigdat_path
        
    pos_int=gbmgeo.PositionInterpolator(T0=0,trigdat=data_file)
    quat=pos_int.quaternion(0)  # computed at t=0 (trigger time)
    dets=gbmgeo.GBM(quat)

    trig_reader = TrigReader(data_file,fine=True,verbose=False)
    trig_reader.set_active_time_interval(*src_int)                                                                                  
    trig_reader.set_background_selections(*bkg_int)

    trigdata  = trig_reader.to_plugin(*det_list)
    data_list = DataList(*trigdata)

    #starting position, not important
    ra, dec = 0.,0.

    
    if spectrum == 'band_function':

        band = Band()
        band.K.prior = Log_uniform_prior(lower_bound=1e-5, upper_bound=250)
        band.xp.prior = Log_uniform_prior(lower_bound=10, upper_bound=1e4)
        band.alpha.set_uninformative_prior(Uniform_prior)
        band.beta.set_uninformative_prior(Uniform_prior)
	model = Model(PointSource('grb',ra,dec,spectral_shape=band))
        
    elif spectrum == 'broken_powerlaw':
	
	bpl = Broken_powerlaw()
	bpl.K.prior = Log_uniform_prior(lower_bound=1e-5, upper_bound=250)
	bpl.xb.prior = Log_uniform_prior(lower_bound=10, upper_bound=1e5)
	bpl.alpha.set_uninformative_prior(Uniform_prior)
	bpl.beta.set_uninformative_prior(Uniform_prior)
	model = Model(PointSource('grb',ra,dec,spectral_shape=bpl))

    elif spectrum == 'cutoff_powerlaw':

	cpl=Cutoff_powerlaw()
	cpl.K.prior = Log_uniform_prior(lower_bound=1e-5, upper_bound=500)
	cpl.xc.prior = Log_uniform_prior(lower_bound=10, upper_bound=1e4)
	cpl.index.set_uninformative_prior(Uniform_prior)
        model = Model(PointSource('grb',ra,dec,spectral_shape=cpl))


    elif spectrum == 'powerlaw':

	pl=Powerlaw()
	pl.K.prior = Log_uniform_prior(lower_bound=1e-5, upper_bound=500)
	pl.index.set_uninformative_prior(Uniform_prior)
        model = Model(PointSource('grb',ra,dec,spectral_shape=pl))

    else:

	print 'ERROR: invalid spectral model'

        
    bayes = BayesianAnalysis(model, data_list)

    # MULTINEST
    wrap = [0]*len(model.free_parameters)   #not working properly
    wrap[0] = 1

    _ =bayes.sample_multinest(800,
                              chain_name='./chains/test',
                              importance_nested_sampling=False,
                              const_efficiency_mode=False,
                              wrapped_params=wrap,
                              verbose=True,
                              resume=False)


    #save MULTINEST results
    if (rank==0):
        bayes.results.write_to(result_path+'/grb_'+trigger+'_'+spectrum+'.fits',overwrite=True)
        
    results = bayes.results


    # energy spectrum
    spectrum_plot = display_spectrum_model_counts(bayes);
    spectrum_plot.savefig(result_path+'/grb_'+trigger+'_residuals_'+spectrum+'.pdf')

    # corner plot
    cc_plot = results.corner_plot_cc()
    cc_plot.savefig(result_path+'/grb_'+trigger+'_cornerplot_'+spectrum+'.pdf')



if __name__ == '__main__':
    fit_trigdat()
