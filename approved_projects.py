import pandas as pd
import datetime
import pytz
import traceback
import os
import re
import requests

from agol_restapi_tools import token_generation
from agol_restapi_tools import oid_field
from agol_restapi_tools import agol_table_to_pd_with_geometry

from agol_table_pull import survey_data
from agol_table_pull import start_points_data
from agol_table_pull import end_points_data
from agol_table_pull import approved_data
from agol_table_pull import pull_features

from agol_update import update_status
from agol_update import update_points
from agol_update import update_csv
from agol_update import update_approved
from agol_update import update_approval_stamp

from teams_notifications import submission_log
from teams_notifications import error_log

from pull_start_end import pull_start_end

from update_ibi import alaska_511_transfer

anchorage_timezone = pytz.timezone('America/Anchorage')

USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']



############################ SET URL LINKS AND GENERATE TOKEN #############################

#Survey URL
survey_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/APEX_FORM_VIEW/FeatureServer'

#Approved Proejct Information URL
approved_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/APEX_Manager_Approved_Projects/FeatureServer'

#Start Points
start_points_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/Start_Points/FeatureServer'

#End Points
end_points_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/End_Points/FeatureServer'

#Set Token
token = token_generation(username = 'AKDOT_COMMUNICATIONS', password = 'Skisnowbird1')




############################## RESET PREVIOUS ENTRIES TO NULL AND MOST RECENT TO "UPDATED"  ########################

def approved_projects():      
   
    # Pull the Survey Data
    survey = survey_data(survey_url, 0, token)

    # Pull Updated and Approved Data that have not been Flagged as Prcoessed
    updated = survey[survey['Weekly_Update_Status'] == 'Updated']
    updated_approved = updated[updated['Approved_for_release'] == 'Approved']
    updated_approved_unprocessed = updated_approved[updated_approved['Approval_Processed'] == 'No']

    # Pull the Features for the Manager Approved Project Data
    features = pull_features(approved_url, token)

    # Iterate Through Data and Process Approved Project
    for index, row in updated_approved_unprocessed.iterrows():
            
        # Store the ObjectID
        objid = row['objectid']

        # Store Project Name
        proj_name = row['Project_Name']

        # Store UID
        uid = row['UID']


        # Select Attributes to Update from Features
        attributes = None

        for dictionary in features:
            
            dict_sel = dictionary['attributes']

            if dict_sel.get('UID') == uid:
                attributes = dict_sel
                break

            else:
                log = {
                    'Event': "UID Does Not Exist within Manager Approved Data",
                    'Date': datetime.datetime.now(pytz.timezone('US/Alaska')).date(),
                    'Time': datetime.datetime.now(pytz.timezone('US/Alaska')).time(),
                    'UID': uid,
                    'Project': proj_name
                }
    
                error_log(log)


        # Pull the Start and End for the Project
        start_x, start_y, end_x, end_y = pull_start_end(uid, proj_name)


        # Create Update DataFrame with Row Data
        entry = pd.DataFrame(row).T


        # Create List of Fields to Drop
        drop_list = [
            'objectid',
            'globalid',
            'Latitude',
            'Longitude',
            'Region',
            'UID',
            'Proj_Name',
            'Proj_Name_alt',
            'IRIS_Number',
            'CreationDate',
            'Creator',
            'EditDate',
            'Editor',
            'Last_Update'
            ]


        # Drop Fields from Update Table
        approve_entry = entry.drop(columns = drop_list, inplace = True)


        # Replace Columns with New Data
        for column in approve_entry.columns:
            for column in approve_entry.columns:
                attributes[column] = entry[column].iloc[0]


        # Replace None Values with Blanks
        for key, value in attributes.items():
            if value is None:
                attributes[key] = ''


        # Check for that one weird data error in that one entry, remove if found
        for key, value in attributes.items():
            if type(value) is str:
                value = value.replace('\xa0', '')
                value = value.replace('\\X', '')


        # Update the Start/End X+Y Fields
        attributes['Start_X'] = start_x
        attributes['Start_Y'] = start_y
        attributes['End_X'] = end_x
        attributes['End_Y'] = end_y

        # Set Timestamp
        current_time_anchorage = datetime.datetime.now(anchorage_timezone)
        attributes['Last_Update'] = current_time_anchorage.strftime('%Y-%m-%d %H:%M:%S %Z')
        

        # Wrap the attributes into a payload
        payload = [{'attributes': attributes}]


        # Send Payload to Update Approved Project Table
        update_approved(approved_url, 0, token, payload)

        # Send Update to Alaska 511 Management Table
        alaska_511_transfer(entry)

        # Send Update to Survey that Approval has been Processed
        update_approval_stamp(objid, token)

        # Send Message that Approved Update Processing Complete
        submission_log(f"{uid}: {proj_name} has been approved and successfully transferred to the Manager Approved Table", "Approved Project Processed", 'A4C400')
        



    ######### UPDATE SURVEY CSV DATA TABLE ##########

    # Pull the Approved Data
    approved = approved_data(approved_url, 0, token)

    # Create a CSV
    approved_csv = approved.to_csv(index = False)

    # Update the CSV 
    update_csv(approved_csv, token)