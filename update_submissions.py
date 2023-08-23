import pandas as pd
import datetime
import pytz
import traceback
import os
import requests

from update_start_end import update_start_end

from teams_notifications import submission_log
from teams_notifications import error_log

from agol_restapi_tools import token_generation
from agol_restapi_tools import oid_field
from agol_restapi_tools import military_time_convert
from agol_restapi_tools import locate_uid

from agol_table_pull import survey_data
from agol_table_pull import start_points_data
from agol_table_pull import end_points_data

from agol_update import update_status
from agol_update import update_points
from agol_update import update_timestamp

from emergency_attention import emergency_attention

from project_closed import project_closed

anchorage_timezone = pytz.timezone('America/Anchorage')

# USERNAME = os.environ['USERNAME']
# PASSWORD = os.environ['PASSWORD']

USERNAME = 'AKDOT_COMMUNICATIONS'
PASSWORD = 'Skisnowbird1'



############################ SET URL LINKS AND GENERATE TOKEN #############################

# Survey URL
survey_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/APEX_FORM_VIEW/FeatureServer'

# Start Points
start_points_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/Start_Points/FeatureServer'

# End Points
end_points_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/End_Points/FeatureServer'

# Set Token
token = token_generation(username = USERNAME, password = PASSWORD)





############################## RESET PREVIOUS ENTRIES TO NULL AND MOST RECENT TO "UPDATED"  ########################

def update_submissions():

    # Pull the Survey Data
    survey = survey_data(survey_url, 0, token)



    # Select Projects from Table by Project UID
    updated = survey[survey['Weekly_Update_Status'] == 'Updated']
    updated_new = updated[updated['New_Submission'] == 'Yes']



    # Iterate Through Projects and Send Along Updates to Points
    for index, row in updated_new.iterrows():
            
        # Store the ObjectID
        objid = row['objectid']

        # Store Project Name
        proj_name = row['Project_Name']

        # Store UID
        uid = row['UID']

        # Emergecny Alert Flag
        alert = row['Emergency_Attention']

        # Project Closed Flag
        #closed = row['Closed']


        # Convert Active Start and Active End to Standard Time
        start_time = military_time_convert(row['Activity_Start'])
        end_time = military_time_convert(row['Activity_End'])

        # Create Timestamp
        current_time_anchorage = datetime.datetime.now(anchorage_timezone)
        last_update = current_time_anchorage.strftime('%Y-%m-%d %H:%M:%S %Z')
        

        # Update the Start and End Points
        update_start_end(pd.DataFrame(row).T)


        # Check if Emergency Alert Signaled
        if alert == 'Yes': 
            emergency_attention(pd.DataFrame(row).T)


        # # Check if Project Closed Signaled
        # if closed == 'Yes': 
        #     project_closed(pd.DataFrame(row).T)



        # Create Update Payload
        payload = [{'attributes':{
                    'objectid': objid,
                    'Activity_Start': start_time,
                    'Activity_End':end_time,
                    'Last_Update': last_update,
                    'New_Submission': "Processed"
                }}]


        # Send the Update Payload to AGOL
        status_update = update_status(survey_url, 0, token, payload)


        # Check if Update Status Completed, if an Error is Returned in the Update Function, Submite Error to Log
        if status_update != None:
            
            log = {
                    'Event': "Update of Project Failed",
                    'Date': datetime.datetime.now(pytz.timezone('US/Alaska')).date(),
                    'Time': datetime.datetime.now(pytz.timezone('US/Alaska')).time(),
                    'ObjectID': objid,
                    'UID': uid,
                    'Project': proj_name,
                    'Error': status_update }
            
            error_log(log)


        # Send Successful Submission to Log
        else:

            submission_log(f"{uid}: {proj_name} Updated in AGOL", 'New Submission Processed', 'A4C400')