import json
import datetime
import pytz
from pytz import timezone

from update_submissions import update_submissions
from approved_projects import approved_projects
from update_ibi import alaska_511_transfer_timed


#Find the Current Date and Time to Send Alert
utc_now = datetime.datetime.now(timezone('UTC'))
ak_tz = timezone('America/Anchorage')
ak_now = utc_now.astimezone(ak_tz)
current_date = ak_now.date().weekday()


#Initiate Wed Email Run
def lambda_handler(event, context):

    #Update APEX Entries
    update_submissions()

    #Update Approved Projects
    approved_projects()

    
    return {
        'statusCode': 200,
        'body': json.dumps('Update Complete')
    }

