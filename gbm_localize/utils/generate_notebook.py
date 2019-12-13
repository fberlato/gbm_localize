import papermill as pm
import pkg_resources
import json
import numpy as np

template_dir = pkg_resources.resource_filename('gbm_localize', 'nb_templates')

all_det_list = ['n0','n1','n2','n3','n4','n5','n6','n7','n8','n9','na','nb','b0','b1']



def read_mpe_json_file(json_file):
    '''
    Reads the localization json file from the mpe.grb website and returns the parameters used for the fit.
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

    #spectrum = json_dict['grb_params'][vind]['model_type']
    det_list = json_dict['grb_params'][vind]['used_detectors'].split(',')
    src_int = [str(json_dict['grb_params'][vind]['active_time_start'])+'-'+str(json_dict['grb_params'][vind]['active_time_stop'])]
    bkg_neg_int = str(json_dict['grb_params'][vind]['bkg_neg_start'])+'-'+str(json_dict['grb_params'][vind]['bkg_neg_stop'])
    bkg_pos_int = str(json_dict['grb_params'][vind]['bkg_pos_start'])+'-'+str(json_dict['grb_params'][vind]['bkg_pos_stop'])
    bkg_int = [bkg_neg_int, bkg_pos_int]

    return det_list, src_int, bkg_int



def generate_nb_trigdat(trigger, trigdat_file, json_file=None, src_int=['0-5'], bkg_int=['-100--10','50-150'], det_list=all_det_list):
    '''
    Generates a notebook with the trigdat data lightcurves.
    :parameter trigger: trigger number.
    :parameter trigdat_file: path of the trigdat_file.
    :parameter src_int: source time interval, e.g. ['0-5'].
    :parameter bkg_int: background time interval, e.g. ['-100--10','50-150'].
    :parameter det_list: list of the detectors to be used, e.g. ['n0','n1','b0'].
    '''

    if json_file != None:
        det_list, src_int, bkg_int = read_mpe_json_file(json_file)
    
    parameter_dict = dict(trigger = trigger, data_dir = trigdat_file, src_int = src_int, bkg_int = bkg_int, det_list=det_list)
    
    pm.execute_notebook(
        template_dir+'/trigdat_nb_template.ipynb',
        'trigdat_nb_'+trigger+'.ipynb',
        parameters = parameter_dict
    )


