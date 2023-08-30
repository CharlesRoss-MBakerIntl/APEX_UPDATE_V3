import pandas as pd
import datetime
import pytz
import traceback
import os
import requests

from teams_notifications import submission_log
from teams_notifications import error_log

from agol_restapi_tools import token_generation
from agol_restapi_tools import oid_field
from agol_restapi_tools import military_time_convert
from agol_restapi_tools import agol_table_to_pd_with_geometry

from agol_table_pull import survey_data
from agol_table_pull import start_points_data
from agol_table_pull import end_points_data

from agol_update import update_status
from agol_update import update_points

# USERNAME = os.environ['USERNAME']
# PASSWORD = os.environ['PASSWORD']

USERNAME = "AKDOT_COMMUNICATIONS"
PASSWORD = "Skisnowbird1"




############################ SET URL LINKS AND GENERATE TOKEN #############################

# Start Points
start_points_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/Start_Points/FeatureServer'

# End Points
end_points_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/End_Points/FeatureServer'

# Set Token
token = token_generation(username = USERNAME, password = PASSWORD)




################## PULL START AND END COORDINATES #######################

def pull_start_end(uid, project_name):

    error = False

    # Select from the Start Feature Point layer
    start_sel = agol_table_to_pd_with_geometry(start_points_url, 0, token, "UID", uid = uid)

    if start_sel[0]['features'] != []:
        
        start_sel_x = start_sel[0]['features'][0]['geometry']['coordinates'][0]
        start_sel_y = start_sel[0]['features'][0]['geometry']['coordinates'][1]


    # UID Does Not Exist within the Start Points Table, Raise Exception and Report Error
    elif start_sel[0]['features'] == []:
        
        log = {
                'Event': "UID Does Not Exist within Start Point Layer",
                'Date': datetime.datetime.now(pytz.timezone('US/Alaska')).date(),
                'Time': datetime.datetime.now(pytz.timezone('US/Alaska')).time(),
                'UID': uid,
                'Project': project_name
            }
        
        error_log(log)

        error = True
    

    # Select from the End Feature Point layer
    end_sel = agol_table_to_pd_with_geometry(end_points_url, 0, token, "UID", uid = uid)

    if end_sel[0]['features'] != []:
        
        end_sel_x = end_sel[0]['features'][0]['geometry']['coordinates'][0]
        end_sel_y = end_sel[0]['features'][0]['geometry']['coordinates'][1]


    # UID Does Not Exist within the Start Points Table, Raise Exception and Report Error
    elif end_sel[0]['features'] == []:
         
        log = {
            'Event': "UID Does Not Exist within End Point Layer",
            'Date': datetime.datetime.now(pytz.timezone('US/Alaska')).date(),
            'Time': datetime.datetime.now(pytz.timezone('US/Alaska')).time(),
            'UID': uid,
            'Project': project_name
        }
    
        error_log(log)

        error = True


    # If no Error Return Coordinates
    if error == False:

        return start_sel_x, start_sel_y, end_sel_x, end_sel_y
    
    # Return True if Eror Occured
    elif error == True:
        
        #Send Notification to Submission Log
        submission_log(f"{uid}: {project_name} Skipped Start/End Update due to missing values", "Approved Project Skip of Missing Start/End Values", color = 'FFAFAF')
        
        return error
