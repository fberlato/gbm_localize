import papermill as pm
import pkg_resources

template_dir = pkg_resources.resource_filename('gbm_localize', 'nb_templates')

all_det_list = ['n0','n1','n2','n3','n4','n5','n6','n7','n8','n9','na','nb','b0','b1']


def generate_nb_trigdat(trigger, trigdat_file, src_int=['0-5'], bkg_int=['-100-10','50-150'], det_list=all_det_list):
    '''
    Generates a notebook with the trigdat data lightcurves.
    :parameter trigger: trigger number.
    :parameter trigdat_file: path of the trigdat_file.
    :parameter src_int: source time interval, e.g. ['0-5'].
    :parameter bkg_int: background time interval, e.g. ['-100-10','50-150'].
    :parameter det_list: list of the detectors to be used, e.g. ['n0','n1','b0'].
    '''

    parameter_dict = dict(trigger = trigger, data_dir = trigdat_file, src_interval = src_int, bkg_int = bkg_int, det_list=det_list)
    
    pm.execute_notebook(
        template_dir+'/trigdat_nb_template.ipynb',
        'trigdat_nb_'+trigger+'.ipynb',
        parameters = parameter_dict
    )


