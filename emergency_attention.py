import pandas as pd
import datetime
import pytz
import traceback
import os
import requests

from agol_restapi_tools import token_generation
from agol_restapi_tools import oid_field

from teams_notifications import error_log

from agol_table_pull import survey_data

from boto3_email import send_email
from botocore.exceptions import ClientError

from teams_notifications import emergency_attention_alert
from teams_notifications import submission_log

# USERNAME = os.environ['USERNAME']
# PASSWORD = os.environ['PASSWORD']

USERNAME = 'AKDOT_COMMUNICATIONS'
PASSWORD = 'Skisnowbird1'


############################ SET URL LINKS AND GENERATE TOKEN #############################


#Set Token
token = token_generation(username = USERNAME, password = PASSWORD)





########################## GRAB PROJECT INFORMATION AND SUBMIT EMAIL AND SEND TEAMS NOTIFICATION  ########################
def emergency_attention(entry):

    # Set Empty Emergency Dict
    emer_dict = {}

    #Package Project Data
    emer_dict['Project Name'] = f"<b>{entry['Project_Name'].iloc[0]}</b>"
    emer_dict['Iris Number'] = f"<b>{entry['IRIS_Number'].iloc[0]}</b>"
    emer_dict['Roadway'] = f"<b>{entry['Roadway'].iloc[0]}</b>"
    emer_dict['Submitter Name'] = f"<b>{entry['Name'].iloc[0]}</b>"
    emer_dict['Submitter Job Title'] = f"<b>{entry['Job_Title'].iloc[0]}</b>"
    emer_dict['Submitter Email'] = f"<b>{entry['Email'].iloc[0]}</b>"
    emer_dict['Submitter Alt Email'] = f"<b>{entry['Email_alt'].iloc[0]}</b>"
    emer_dict['Details'] = f"<b>{entry['Emergency_Explain'].iloc[0]}</b>"

    #Develop Message
    header = "Emergency Attention for Project in APEX"

    message = f"""
            <p>An emergency attention indicator has been flagged in a survey submission for</p> 

            <p>Project Name:  {emer_dict['Project Name']}</p>

            <p>IRIS Number:  {emer_dict['Iris Number']}</p>

            <p>Roadway:  {emer_dict['Roadway']}</p>

            <p>Submitter Name:  {emer_dict['Submitter Name']}</p>

            <p>Submitter Job:  {emer_dict['Submitter Job Title']}</p>

            <p>Submitter Email:  {emer_dict['Submitter Email']}</p>

            <p>Submitter Alt Email:  {emer_dict['Submitter Alt Email']}</p>

            <br>

            <p>Explanation of emergency:</p>

            <p>{emer_dict['Details']}</p>
        """


    # Set Manager Alert List
    #alert_list = ['caitlin.frye@mbakerintl.com', 'charles.ross@mbakerintl.com']
    alert_list = ['charles.ross@mbakerintl.com']


    # Send Email to Managers in Alert List
    for email in alert_list:

        #Send Email through BOTO3
        response = send_email(sender = 'caitlin.frye@mbakerintl.com',
                            recipients = email,
                            subject = header,
                            body = message)
        
        

    # Send Teams Notification
    emergency_attention_alert(header, emer_dict)





   