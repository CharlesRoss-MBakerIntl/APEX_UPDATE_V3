import json
import requests


############ SUBMISSION LOG TEAMS MESSAGE ##############

def submission_log(message, title, color):

    #Create Error Catch
    error = None

    try:
        
        #Set the Connection to the Submission Logs
        webhook = 'https://mbakerintl.webhook.office.com/webhookb2/3343f011-93de-4d20-8d3d-833de2c612d1@4e1ee3db-4df6-4142-b7b9-bec15f171ca4/IncomingWebhook/7fb4b3f9856148899ca094bbe122d76d/db8a8ebb-eac1-4481-8c67-263eda53b6fc'

        #Create Message Payload
        payload = {
                '@type': 'MessageCard',
                '@context': 'http://schema.org/extensions',
                'themeColor': color,
                'summary': 'New message',
                'sections': [
                    {
                        'activityTitle': title,
                        'text': message
                    }
                ]
            }

        #Create Payload Headers
        headers = {
            'Content-Type': 'application/json'
        }

        #Submit Message
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)
        
        #If Request Connectin Failed, Create Event and Raise Exception
        if response.status_code != 200:
            error =  {'Event': 'Failed to Submit to Teams Log'}

            raise Exception("Failed to Submit to Log")


    #Return Error if Failed
    except Exception as e:
        return error




############ CODE ERROR ALERT LOG TEAMS MESSAGE ##############

def error_log(log):

    #Create Error Catch
    error = None

    try:

        #Convert Log to Readable Dictionary String
        dict_str = "<br>".join([f"{key}: {value}" for key, value in log.items()])
        
        #Set Webhook to Code Monitor Group
        webhook = 'https://mbakerintl.webhook.office.com/webhookb2/3343f011-93de-4d20-8d3d-833de2c612d1@4e1ee3db-4df6-4142-b7b9-bec15f171ca4/IncomingWebhook/ed6d2e87475d4cc4af3437ee1e73f0ae/db8a8ebb-eac1-4481-8c67-263eda53b6fc'

        #Create Message Payload
        payload = {
            'text': dict_str,
            'from': {
                'name': "APEX Code Alert"
            }
        }

        #Set Payload Headers
        headers = {
            'Content-Type': 'application/json'
        }

        #Submit Message
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)

        #If Request Connection Failed, Create Event and Raise Error
        if response.status_code != 200:
                error =  {'Event': 'Failed to Submit to Code Log'}

                raise Exception("Failed to Submit to Log")
    

    #Return Error if Failed
    except Exception as e:
        return error
    





############ NOTIFICATIONS SENT TO MICHAEL BAKER MANAGER CHANNEL ##############

def mb_alert(message):

    #Create Error Catch
    error = None

    try:
        
        #Set Webhook to Michael Baker Notification Group
        webhook = 'https://mbakerintl.webhook.office.com/webhookb2/3343f011-93de-4d20-8d3d-833de2c612d1@4e1ee3db-4df6-4142-b7b9-bec15f171ca4/IncomingWebhook/a08d69c7c1184af3bfabbb91fb3eea1c/db8a8ebb-eac1-4481-8c67-263eda53b6fc'

        #Create Message Payload
        payload = {
            'text': message,
            'from': {
                'name': "APEX Michael Baker Notifications"
            }
        }

        #Set Payload Headers
        headers = {
            'Content-Type': 'application/json'
        }

        #Submit Message
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)

        #If Request Connection Failed, Create Event and Raise Error
        if response.status_code != 200:
                error =  {'Event': 'Failed to Submit to Michael Baker Log'}

                raise Exception("Failed to Submit to Log")
    

    #Return Error if Failed
    except Exception as e:
        return error
    




############ EMAIL UPDATE SENT TO MICHAEL BAKER MANAGER CHANNEL ##############

def mb_email_summary(email_sum, header):

    #Create Error Catch
    error = None

    try:
        
        #Set Webhook to Michael Baker Notification Group
        webhook = 'https://mbakerintl.webhook.office.com/webhookb2/3343f011-93de-4d20-8d3d-833de2c612d1@4e1ee3db-4df6-4142-b7b9-bec15f171ca4/IncomingWebhook/a08d69c7c1184af3bfabbb91fb3eea1c/db8a8ebb-eac1-4481-8c67-263eda53b6fc'

        #Convert Log to Readable Dictionary String
        dict_list_str = "<br>".join([", ".join(f"{key}: {value}" for key, value in email.items()) for email in email_sum])

        #Create Message Payload
        payload = {
            'title': header,
            'text': dict_list_str,
            'from': {
                'name': "APEX Wed Email Summary"
            }
        }

        #Set Payload Headers
        headers = {
            'Content-Type': 'application/json'
        }

        #Submit Message
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)

        #If Request Connection Failed, Create Event and Raise Error
        if response.status_code != 200:
                error =  {'Event': 'Failed to Submit to MB Notifications'}

                raise Exception("Failed to Submit to Log")
    

    #Return Error if Failed
    except Exception as e:
        return error
    



############ EMAIL UPDATE SENT TO MICHAEL BAKER MANAGER CHANNEL ##############

def emergency_attention_alert(header, message):

    #Create Error Catch
    error = None

    try:
        
        #Set Webhook to Michael Baker Notification Group
        webhook = 'https://mbakerintl.webhook.office.com/webhookb2/3343f011-93de-4d20-8d3d-833de2c612d1@4e1ee3db-4df6-4142-b7b9-bec15f171ca4/IncomingWebhook/a08d69c7c1184af3bfabbb91fb3eea1c/db8a8ebb-eac1-4481-8c67-263eda53b6fc'

        dict_str = ""

        for key, value in message.items():
            if key == 'Details':
                dict_str += "<br>"
            dict_str += f"{key}: {value}<br>"
    
        #Create Message Payload
        payload = {
            'title': header,
            'text': dict_str,
            'from': {
                'name': "APEX Emergency Attention"
            }
        }

        #Set Payload Headers
        headers = {
            'Content-Type': 'application/json'
        }

        #Submit Message
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)

        #If Request Connection Failed, Create Event and Raise Error
        if response.status_code != 200:
                error =  {'Event': 'Failed to Submit to MB Notifications'}

                raise Exception("Failed to Submit Emergency Attention to Log")


    #Return Error if Failed
    except Exception as e:
        raise Exception("Failed to Submit Emergency Attention Message to Teams Log")
    





############ NOTIFICATIONS SENT TO EMAILS LOG CHANNEL ##############

def email_log(message, color):

    #Create Error Catch
    error = None

    try:
        
        #Set Webhook to APEX Email Log Channel
        webhook = 'https://mbakerintl.webhook.office.com/webhookb2/3343f011-93de-4d20-8d3d-833de2c612d1@4e1ee3db-4df6-4142-b7b9-bec15f171ca4/IncomingWebhook/691096d3558e4a2d844b81dace5c7f4b/db8a8ebb-eac1-4481-8c67-263eda53b6fc'

        #Create Message Payload
        payload = {
                '@type': 'MessageCard',
                '@context': 'http://schema.org/extensions',
                'themeColor': color,
                'summary': 'New message',
                'sections': [
                    {
                        'text': message
                    }
                ]
            }

        #Create Payload Headers
        headers = {
            'Content-Type': 'application/json'
        }

        #Submit Message
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)
        
        #If Request Connectin Failed, Create Event and Raise Exception
        if response.status_code != 200:
            error =  {'Event': 'Failed to Submit to Emnails Log'}

            raise Exception("Failed to Submit to Log")


    #Return Error if Failed
    except Exception as e:
        return error
    






############ WEBHOOK LOG MESSAGE ##############

def webhook_log(message, header, color):

    #Create Error Catch
    error = None

    try:
        
        #Set the Connection to the Submission Logs
        webhook = "https://mbakerintl.webhook.office.com/webhookb2/3343f011-93de-4d20-8d3d-833de2c612d1@4e1ee3db-4df6-4142-b7b9-bec15f171ca4/IncomingWebhook/fd796313229a4a1da4eeaca0197d11e9/db8a8ebb-eac1-4481-8c67-263eda53b6fc"

        dict_str = ""

        for key, value in message.items():
            if key == 'Details':
                dict_str += "<br>"
            dict_str += f"{key}: {value}<br>"
    
        #Create Message Payload
        payload = {
            'title': header,
            'text': dict_str,
            'themeColor': color,
            'from': {
                'name': "Webhook Processing"
            }
        }

        #Set Payload Headers
        headers = {
            'Content-Type': 'application/json'
        }

        #Submit Message
        response = requests.post(webhook, data=json.dumps(payload), headers=headers)

        #If Request Connection Failed, Create Event and Raise Error
        if response.status_code != 200:
                error =  {'Event': 'Failed to Submit Message to Webhook Log'}

                raise Exception("Failed to Submit Message to Webhook Log")


    #Return Error if Failed
    except Exception as e:
        raise Exception("Failed to Submit Message to Webhook Log")