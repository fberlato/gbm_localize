from gbm_localize.trigdat_fit import fit_trigdat
from gbm_localize.utils.download_data import download_trigger_data, download_json
from gbm_localize.utils.generate_notebook import generate_nb_trigdat
from glob import glob
import os



class MPE_Trigger(object):

    def __init__(self, trigger, overwrite=False):

        self.trigger = trigger
        self.overwrite = overwrite
        
        self.setup_trigdat_event()
        
        self.trigdat_file = glob('glg_trigdat_all_bn'+trigger+'_v0*.fit')[0]
        self.json_file = 'json_'+trigger+'.json'
        self.conf_file = 'config_data_'+trigger+'.json' 
        
    
    def setup_trigdat_event(self):

        #checks whether there is a trigdat file
        if len(glob(self.trigger+'/glg_trigdat_all_bn'+self.trigger+'_v0*.fit')) == 0:
            download_trigger_data(self.trigger, data_type='trigdat')

        #if not os.path.isfile(self.json_file):
        download_json(self.trigger)

        os.chdir(self.trigger)

        if self.overwrite or os.path.isfile('trigdat_nb_'+self.trigger+'.ipynb') == False:
            trigdat_file = glob('glg_trigdat_all_bn'+self.trigger+'_v0*.fit')[0]
            json_file = 'json_'+self.trigger+'.json'
        
            generate_nb_trigdat(self.trigger, trigdat_file=trigdat_file, json_file=json_file)



    def refit_grb(self):
        fit_trigdat(self.trigger, trigdat_file=self.trigdat_file, conf_file=self.conf_file)
