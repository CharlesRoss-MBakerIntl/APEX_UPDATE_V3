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

from agol_table_pull import survey_data
from agol_table_pull import start_points_data
from agol_table_pull import end_points_data

from agol_update import update_status
from agol_update import update_points

# USERNAME = os.environ['USERNAME']
# PASSWORD = os.environ['PASSWORD']

USERNAME = 'AKDOT_COMMUNICATIONS'
PASSWORD = 'Skisnowbird1'



############################ SET URL LINKS AND GENERATE TOKEN #############################

# Start Points
start_points_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/Start_Points/FeatureServer'

# End Points
end_points_url = 'https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/End_Points/FeatureServer'

# Set Token
token = token_generation(username = USERNAME, password = PASSWORD)



########## UPDATE START END POINTS  ###########

def update_start_end(entry):

    ######## START AND END POINTS TABLE ##########

    # Pull Start Point Feature Table
    start_points = start_points_data(start_points_url, 0, token)

    # Find the OID field in Start Points
    start_points_oid = oid_field(start_points_url, 0, token)


    # Pull Start Point Feature Table
    end_points = end_points_data(end_points_url, 0, token)

    # Find the OID field in End Points
    end_points_oid = oid_field(end_points_url, 0, token)


    # Store the Data from Entry
    uid = entry['UID'].iloc[0]

    project_name = entry['Project_Name'].iloc[0]

    

    ########### PROCESS ENTRY AND UPDATE START AND END

    # Select New Entry from Table and Select the Start and End X,Y Values
    coord = entry[['Start_X', 'Start_Y', 'End_X', 'End_Y']]

    # Check if any Coordinates Empty
    if coord.empty == True:
        raise Exception('Coordinate Selection During Points Update Returned Empty Dataframe')

    # Set a Switch 
    switch = ''

    # Check if Data Missing
    for index, row in coord.iterrows():
        for column in coord.columns:
            if row[column] == '':

                # Flip the Switch to Not Update
                switch = 'on'

                

    #Check if Any of These Values Empty, if So, Skip the Upload to Point Features
    if switch != 'on':
    
        #Find the Start and End Point ObjectIDs to Update in the Data Tables using the Project UID Number
        try:

            #Find the Project OBJECTID in Start Points
            start_objectid = start_points[start_points['UID'] == uid][start_points_oid].iloc[0]

            ##Find the Project OBJECTID in End Points
            end_objectid = end_points[end_points['UID'] == uid][end_points_oid].iloc[0]


        #UID Was not Found in the Start or End Point Tables, Return an Error with Logged Message
        except IndexError as e:

            log = {
                        'Event': "UID Does Not Exist within Start/End Point Layers",
                        'Date': datetime.datetime.now(pytz.timezone('US/Alaska')).date(),
                        'Time': datetime.datetime.now(pytz.timezone('US/Alaska')).time(),
                        'UID': uid,
                        'Project': project_name}
           

            error_log(log)


        #Create a Geo Package of Start and End Points to Update Geographic Locations in Update Points Function
        geo_package = {'starts': [{
                                    "geometry": {
                                        "x": coord['Start_X'],
                                        "y": coord["Start_Y"],
                                        'spatialReference': {
                                            'wkid': 4326 }
                                    },
                                    "attributes": {
                                        f"{start_points_oid}": start_objectid,
                                        } 
                                    }],

                        'ends': [{
                                    "geometry": {
                                        "x": coord['End_X'],
                                        "y": coord["End_Y"],
                                        'spatialReference': {
                                            'wkid': 4326 }
                                    },
                                    "attributes": {
                                        f"{end_points_oid}": end_objectid,
                                        } 
                                    }]
                    }
        
        #Update the Start and End Points
        points_update = update_points(start_points_url, 0, end_points_url, 0, token, geo_package)

        #If Points Update Function Returned Error, Raise Exception
        if points_update != None:
           
           log = {
                        'Event': "Update of Start and End Points Failed",
                        'Date': datetime.datetime.now(pytz.timezone('US/Alaska')).date(),
                        'Time': datetime.datetime.now(pytz.timezone('US/Alaska')).time(),
                        'UID': uid,
                        'Project': project_name}
           

           error_log(log)



    else:
        # Submit a Notification to the Log if Empty Values
        submission_log(f"{uid}: {project_name} contains missing values for start and end points, skipping point update", "Missing Start/End Lat, Lng", color = 'FFAFAF')