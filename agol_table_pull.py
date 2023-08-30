import requests
import pandas as pd
import datetime
import pytz
import json
import requests

from agol_restapi_tools import agol_table_to_pd
from agol_restapi_tools import locate_uid


####################################################################### PULL UPDATED SURVEY ENTRIES ################################################################

def survey_data(survey_url, layer, token):
    
    #Pull Full Survey
    uid_check = agol_table_to_pd(service_url = survey_url, 
                                layer = layer, 
                                token = token, 
                                convert_dates = "n",
                                drop_objectids = 'n')
    

    #Fill UIDS that are Blank
    for index, row in uid_check.iterrows():

        if row['UID'] == None or row['UID'] == '':
            
            uid = locate_uid(row["Proj_Name"], token)
            
            url = f"{survey_url}/{layer}/applyEdits"
            
            payload = [
                {
                    "attributes": {
                    "OBJECTID": row['objectid'],
                    "UID":uid
                    }
                }
                    ]
            
            params = {
                'f':'json',
                'token':token,
                'updates':f'{payload}'
            }
            
            response = requests.post(url, params)



    #Pull Survey Again After Update
    table = agol_table_to_pd(service_url = survey_url, 
                                layer = layer, 
                                token = token, 
                                convert_dates = "n",
                                drop_objectids = 'n')
    
    
    #If the Pulled Table is NOT Empty
    if table.empty == False:

        #Filter any UID's that are Blank
        if 'UID' in table.columns:
            table = table[table["UID"] != ""]

            #Set Survey Entries to Number
            if table['UID'].dtype == 'object':
                table['UID'] = table['UID'].astype(int)


        #Set Project Name to Match Project Data
        if 'Proj_Name' in table.columns:
            table.rename(columns = {'Proj_Name':'Project_Name'}, inplace = True)  


        return table


    #If Table is Empty, Table Did Not Load Correctly, Return Exception
    else:
        raise Exception("Survey Table Loaded Incorrectly")
    




def start_points_data(starts_url, layer, token):
    
    #Pull Full Survey
    table = agol_table_to_pd(service_url = starts_url, 
                                layer = layer, 
                                token = token, 
                                convert_dates = "n",
                                drop_objectids = 'n')
    
    #If the Pulled Table is NOT Empty
    if table.empty == False:

        return table


    #If Table is Empty, Table Did Not Load Correctly, Return Exception
    else:
        raise Exception("Start Points Table Loaded Incorrectly")
    




def end_points_data(ends_url, layer, token):
    
    #Pull Full Survey
    table = agol_table_to_pd(service_url = ends_url, 
                                layer = layer, 
                                token = token, 
                                convert_dates = "n",
                                drop_objectids = 'n')
    
    #If the Pulled Table is NOT Empty
    if table.empty == False:

        return table


    #If Table is Empty, Table Did Not Load Correctly, Return Exception
    else:
        raise Exception("End Points Table Loaded Incorrectly")
    





def approved_data(approved_url, layer, token):
    
    #Pull Full Approved Project Data Table
    table = agol_table_to_pd(service_url = approved_url, 
                                layer = layer, 
                                token = token, 
                                convert_dates = "n",
                                drop_objectids = 'n')

    #If the Pulled Table is NOT Empty
    if table.empty == False:

        return table
    



############## PULL APPROVED ATTRIBUTE FEATURES ####################

def pull_features(service_url, token):
    
    url = f"{service_url}/0/query"

    params = {
        'f':'json',
        'token':token,
        'where':'1=1',
        'outFields':'*'
    }

    response = requests.post(url, params).json()

    features = response['features']

    return features