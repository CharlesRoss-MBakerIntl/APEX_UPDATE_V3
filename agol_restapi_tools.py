import requests
import json
import pandas as pd
import pytz
import re
import datetime
import pytz

import warnings
warnings.simplefilter('ignore')

from teams_notifications import error_log




############################################################ CONVERT AGOL DATES TOOL ######################################################################

def agol_date_convert_akt(agol_data, agol_df):

    #Set Alaska Timezone
    alaska_tz = pytz.timezone('US/Alaska')
    
    #Pull Fields from AGOL Data Table, BEFORE PD CONVERSION
    if agol_data.get("fields") != None:
        fields = agol_data['fields']

        #Find Field Names and Types
        field_types = pd.DataFrame([[row['name'], row['type']] for row in fields], columns = ['name', 'type'])

        #Iterate Through Data Field, if Field is an ESRIDATETYPE, Check if Field in AGOL DF, If There, Convert to Datetime
        for index,row in field_types.iterrows():
            if row['type'] == 'esriFieldTypeDate':
                date_field = row['name']
                if date_field in agol_df.columns:
                    agol_df[date_field] = pd.to_datetime(agol_df[date_field], unit='ms')
                    agol_df[date_field] =  agol_df[date_field].dt.tz_localize('UTC').dt.tz_convert(alaska_tz)
                    agol_df[date_field] = agol_df[date_field].apply(lambda x: x.strftime('%B %d, %Y   %H:%S'))

        return agol_df

    elif agol_data.get("fields") == None:
        raise Exception("Input Data Table Has No 'Fields' Attribute")
    



############################################## GRAB THE OID FIELD FOR A FEATURE LAYER #######################################################

def oid_field(service_url, layer, token):

    #Set Query URL
    url = f'{service_url}/{str(layer)}/query'

    #Set Query Params
    params = {
        'f': 'json',
        'where':'1=1',           # response format
        'outFields': '*',       # fields to include in the response
        'returnGeometry': 'false',
        'token':token  # don't include geometry
    }

    #Send Response to AGOL
    response = requests.get(url = url, params=params)

    #Pull Table Data
    data = json.loads(response.text)


    #Search for OID Field in Table
    oid_field = None

    for field in data['fields']:
        if field['type'] == 'esriFieldTypeOID':
            oid_field = field['name']
            break

    return oid_field




###################################################### CONVERT PANDAS TO ATTRIBUTE LIST FOR AGOL UPLOAD #############################################################

def pd_to_attributes_list(df):
    
    #Create Entry List for Attributes
    data_append = []


    #Check for Dates in Table and Convert to Strings
    if df.select_dtypes(include=['datetime64']).columns != 0:
        dates = df.select_dtypes(include=['datetime64']).columns
        for column in dates:
            df[column] = df[column].astype("str")


    #Iterate Throught the Entire Pandas Data Table
    for row in df.iterrows():
    
        #Grab Each Row
        entry = pd.DataFrame(data = row[1])

        #Convert the Row into a Dictionary
        entry = entry.to_dict()
        
        #Grab Info from Dictionary and Place into Attributes Dictionary
        for key, values in entry.items():
            attributes = {'attributes': values}

        #Add Attributes to List of Items to Append to Hosted Table
        data_append.append(attributes)

    return data_append





###################################################### GENERATE AGOL TOKEN #############################################################

def token_generation(username, password):
    #Rest Api Token URl
    url = 'https://www.arcgis.com/sharing/rest/generateToken'

    #User Data to Generate Token
    data = {
        "username":username,
        'password':password,
        'referer':'https://www.arcgis.com'
    }

    #Additional Parameters
    params = {
        'f':'json'
    }

    #Send Response to Generate Token
    response = requests.post(url, params=params, data=data)

    #Save Token
    token = response.json()["token"]

    return token






###################################################### CONVERT AGOL SERVICE URL TO PANDAS DF #############################################################

def agol_table_to_pd(service_url, layer, token, convert_dates = "n", drop_objectids = "n"):

    url = f'{service_url}/{str(layer)}/query'

    #Enter Serach Parameters to Pull Data Table
    params = {
        'f': 'json',
        'token': token,
        'where': '1=1',  
        'outFields': '*',
        'returnGeometry': False
    }

    #Send Repsonse to Pull Table
    response = requests.get(url, params=params)

    #If Response Connection Successful, Pull Data and Convert to Pandas Dataframe
    if response.status_code == 200:
        data = response.json()
        table = data.get('features', [])
        df = pd.DataFrame([row['attributes'] for row in table])



    #Drop ObjectID
    if drop_objectids.lower() == "y":
    
        if "ObjectId" in df.columns:
            df = df.drop(columns = "ObjectId")

        elif "objectid" in df.columns:
            df = df.drop(columns = "objectid")

        elif "OBJECTID" in df.columns:
            df = df.drop(columns = "OBJECTID")

        elif "Fid" in df.columns:
            df = df.drop(columns = "Fid")

        elif "fid" in df.columns:
            df = df.drop(columns = "fid")

        elif "FID" in df.columns:
            df = df.drop(columns = "FID")


    #Catch All Date Fields and Convert to Pandas Datetime if Selected
    if convert_dates.lower() == "y":
        agol_date_convert_akt(data, df)
    
    elif convert_dates.lower() == "n":
        pass

    else:
        pass


    #Fill NAs or Nans
    df.fillna("", inplace = True)
    

    return df





###################################################### CONVERT AGOL SERVICE URL TO PANDAS DF WITH GEOMETRY #############################################################

def agol_table_to_pd_with_geometry(service_url, layer, token, uid_field, uid = "*"):

    #Set Query URl
    url = f'{service_url}/{str(layer)}/query'

    if uid != "*" and type(uid) == int:
        
        #Enter Serach Parameters to Pull Data Table
        params = {
        'where': f'{uid_field}={uid}',
        'outFields': '*',
        'returnGeometry': 'true',
        'f': 'geojson',
        'token':token
        }

   
    elif uid == "*":
        #Enter Serach Parameters to Pull Data Table
        params = {
        'where':"1=1",
        'outFields': '*',
        'returnGeometry': 'true',
        'f': 'geojson',
        'token':token
        }


    else:
        raise Exception("UID is not an Integer")
    

    #Send Pull Request
    response = requests.get(url, params)

    # Extract the geometry from the response
    data = response.json()
    geometry = [feature['geometry'] for feature in data['features']]


    return data, geometry




############################################## CONVERT MILITARY TIME TO 12HR TIME #######################################################
def military_time_convert(time):

    #Set Formatted Time Catch
    formatted_time = None
    
    #Set Military Time Pattern
    pattern = r'^[0-2][0-9]:[0-5][0-9]$'

    #If time meets the pattern of military time, convert to AM or PM format:
    if re.match(pattern, time):

        #Convert Time
        conversion = datetime.datetime.strptime(time, "%H:%M")
        formatted_time = conversion.strftime("%I:%M %p").lstrip("0")

    #If time does not match, output the original time
    else:
        formatted_time = time

    return formatted_time




########################################## CONVERT STANDARD TIME TO MILITARY TIME #################################################
def standard_time_convert(time_str):

    formatted_time = '12:00'

    # Define the regex pattern
    pattern = r'\b(1[012]|[1-9]):([0-5][0-9])\s*(?:AM|PM)\b'
    
    # Find the match
    match = re.search(pattern, time_str)
    
    if match:
        # Extract the hour and minutes from the match
        hour, minutes = map(int, match.groups())
        
        # Check if it's PM and adjust the hour accordingly
        if 'PM' in match.group():
            hour += 12
            hour %= 24  # Ensure hour is within the range of 0 to 23
        
        # Convert to 24-hour format and return
        formatted_time = f'{hour:02d}:{minutes:02d}'
    
    # Return None if no match is found
    return formatted_time




######################### LOCATE UID IN MASTER POLYGON DATA #########################

def locate_uid(proj_name, token):
    
    master = "https://services.arcgis.com/r4A0V7UzH9fcLVvv/arcgis/rest/services/CY2023_Project_Polygons_notcleaned/FeatureServer"

    df = agol_table_to_pd(master, 0, token, drop_objectids='y')
    
    df_sel = df[df['Project_Name'] == proj_name]

    if df_sel.empty == False:
    
        return df_sel['Unique_ID'].iloc[0]

    
    else:
        pass




############################ CHECK UPDATE STATUS FUNCTION #############################

def check_update_status(creationDate):

    #Set Alaska Timezone
    alaska_tz = pytz.timezone('US/Alaska')

    #Save Current Date and Time for Comparison
    today = datetime.datetime.now(alaska_tz).date()

    #Find the Date for This Week's Monday
    this_monday = pd.Timestamp(today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(days = 0))

    #Find the Date for This Week's Sunday
    this_sunday = pd.Timestamp(this_monday + datetime.timedelta(days = 6))

    #Find the date that is 4 Weeks Back from the Sunday
    four_weeks_back = pd.Timestamp(this_monday - datetime.timedelta(days = 28))
    
    #Modify CreationDate
    creationDate = pd.Timestamp(creationDate)
    

    #Check CreationDate Status Against Dates
    status = ''

    if creationDate < four_weeks_back:
        status = "Out of Date"

    elif creationDate >= four_weeks_back and creationDate < this_monday:
        status = 'Awaiting Update'

    elif creationDate >= this_monday and creationDate <= this_sunday:
        status = 'Updated'


    return status
    







