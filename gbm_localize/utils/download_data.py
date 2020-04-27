import requests
import urllib.request as ulib
import os
import json
from itertools import product


all_det = ['n0','n1','n2','n3','n4','n5','n6','n7','n8','n9','na','nb','b0','b1']


def download_trigger_data(trigger, data_type='trigdat', data_dir=None):
    '''
    Downloads the trigger data from the FTP server.
    :parameter trigger: trigger number.
    :parameter data_type: trigdat, tte (default is trigdat).
    :parameter data_dir: directory where the data is downloaded.
    '''

    original_dir = os.getcwd()
    
    #to be sure that even non-string input still works
    trigger = str(trigger)
    
    year = trigger[0:2]
    month = trigger[2:4]
    day = trigger[4:6]

    if type(data_type) == str:
        data_type = [data_type]
        

    if data_dir == None:
        if os.path.isdir(trigger) == True:
            os.chdir(trigger)
        else:
            os.mkdir(trigger)
            os.chdir(trigger)
    else:
        if os.path.isdir(data_dir) == True:
            os.chdir(data_dir)
        else:
            os.mkdir(data_dir)
            os.chdir(data_dir)
        
    url = 'https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/triggers/20'+year+'/bn'+trigger+'/current/'


    if 'trigdat' in data_type or 'all' in data_type:
            
        for i in range (0,10):
            file_name = 'glg_trigdat_all_bn'+trigger+'_v0'+str(i)+'.fit'
            file_url = url + file_name
            request = requests.get(file_url)
        
            if request.status_code == 200:
                break

        assert request.status_code == 200, 'ERROR: trigdat data not found!'

        downloaded_file = ulib.urlopen(file_url)

        if os.path.isfile(file_name) == True:
            pass
        else:
            with open(file_name, "wb") as local_file:
                local_file.write(downloaded_file.read())

            print(file_name+' downloaded!')

            
    #tte data
    if 'tte' in data_type or 'all' in data_type:
        for i in range (0,10):
            file_name = 'glg_tte_n0_bn'+trigger+'_v0'+str(i)+'.fit'
            file_url = url + file_name
            request = requests.get(file_url)
        
            if request.status_code == 200:
                break

        assert request.status_code == 200, 'ERROR: tte data not found!'

        for det in all_det:
            file_name = 'glg_tte_'+det+'_bn'+trigger+'_v0'+str(i)+'.fit'        

            if os.path.isfile(file_name) == True:
                print('File %s already present, skipping.' % file_name)
                continue
            
            else:
                file_url = url + file_name
                downloaded_file = ulib.urlopen(file_url)

                with open(file_name, "wb") as local_file:
                    local_file.write(downloaded_file.read())

                print(file_name+' downloaded!')


    if 'all' in data_type:
        #everything else
        datas = ['cspec','ctime']
        exts = ['pha','rsp','rsp2']
        names = product(datas, exts)

        for name in names:

            if name[0] in data_type or 'all' in data_type:
            
                for i in range (0,10):
                    file_name = 'glg_'+name[0]+'_n0_bn'+trigger+'_v0'+str(i)+'.'+name[1]
                    file_url = url + file_name
                    request = requests.get(file_url)

                    print(url)
                    print(file_name)
                
                    if request.status_code == 200:
                        if name[1] == 'rsp':
                        
                            file_name = 'glg_'+name[0]+'_n0_bn'+trigger+'_v0'+str(i)+'.rsp2'
                            file_url = url + file_name
                            request = requests.get(file_url)

                            if request.status_code == 200:
                                continue
                        
                            else:
                                break
                            
                        else:
                            break

                        assert request.status_code == 200, 'ERROR: '+name[0]+' data with extension '+name[1]+' not found!'
            
                        for det in all_det:
                            file_name = 'glg_'+name[0]+'_'+det+'_bn'+trigger+'_v0'+str(i)+'.'+name[1]
                
                            if os.path.isfile(file_name) == True:
                                print('File %s already present, skipping.' % file_name)
                                continue
                
                            else:
                                file_url = url + file_name
                                downloaded_file = ulib.urlopen(file_url)

                            with open(file_name, "wb") as local_file:
                                local_file.write(downloaded_file.read())
                        
                            print(file_name+' downloaded!')


    os.chdir(original_dir)

    

def download_json(trigger, data_dir=None):
    '''
    Downloads the json file for the trigger from the website.
    :parameter trigger: trigger of the GRB.
    :parameter data_dir: directory where the data is downloaded.
    '''
    
    original_dir = os.getcwd()
    
    if data_dir == None:
        if os.path.isdir(trigger) == True:
            os.chdir(trigger)
        else:
            os.mkdir(trigger)
            os.chdir(trigger)
    else:
        if os.path.isdir(data_dir) == True:
            os.chdir(data_dir)
        else:
            os.mkdir(data_dir)
            os.chdir(data_dir)
 
    
    trigger = str(trigger)
    url = 'https://grb.mpe.mpg.de/grb/GRB'+trigger+'/json/'
    
    resp = ulib.urlopen(url)
    json_data = json.loads(resp.read())

    with open('json_'+trigger+'.json', 'w') as outfile:
        json.dump(json_data, outfile)


    os.chdir(original_dir)
