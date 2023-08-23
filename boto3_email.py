import boto3
from botocore.exceptions import ClientError
import datetime
import pytz

################################# SET EMAIL FUNCTION ######################################

def send_email(sender, recipients, subject, body):

    #Set the SES Client
    ses = boto3.client('ses', region_name='us-east-1')
    CHARSET = "UTF-8"
    client = boto3.client('ses')


    try:

        #Send Message to Recipients
        response = ses.send_email(
            Source=sender,
            Destination={
                'ToAddresses': [recipients],
            },
            Message={
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    'Html': {
                        'Data': body,
                    },
                },
            }
        )


    #If Email Failed to Send, Set Error
    except ClientError as e:
       
       log = {
                'Event': "Email Failed to Send",
                'Date': datetime.datetime.now(pytz.timezone('US/Alaska')).date(),
                'Time': datetime.datetime.now(pytz.timezone('US/Alaska')).time(),
                'Email': recipients
            } 