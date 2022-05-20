from unicodedata import numeric
from flask import Flask, request, redirect
import pandas as pd
from datetime import datetime
import requests
from withings_api_example import config

app = Flask(__name__)

CLIENT_ID = config.get('withings_api_example', 'client_id')
CUSTOMER_SECRET = config.get('withings_api_example', 'customer_secret')
STATE = config.get('withings_api_example', 'state')
ACCOUNT_URL = config.get('withings_api_example', 'account_withings_url')
WBSAPI_URL = config.get('withings_api_example', 'wbsapi_withings_url')
CALLBACK_URI = config.get('withings_api_example', 'callback_uri')

@app.route("/")
def decide_at_start():
    print("Choose:\n sign up of new patient (signup) or data query (query)")
    decision = input("Enter key:\n")
    if decision == "signup":
        return redirect("/signup")
    elif decision == "query":
        return redirect("/query")
    else: 
        decide_at_start()   

@app.route("/signup")
def get_code():
    """
    Route to get the permission from an user to take his data.
    This endpoint redirects to a Withings' login page on which
    the user has to identify and accept to share his data
    """
    payload = {'response_type': 'code',  # imposed string by the api
               'client_id': CLIENT_ID,
               'state': STATE,
               'scope': ['user.info,user.metrics,user.activity'],  # see docs for enhanced scope
               'redirect_uri': CALLBACK_URI,  # URL of this app
               'mode': 'demo'  # Use demo mode, DELETE THIS FOR REAL APP
               }

    r_auth = requests.get(f'{ACCOUNT_URL}/oauth2_user/authorize2',
                          params=payload)
    print(r_auth)

    return redirect(r_auth.url)


@app.route("/get_token")
def get_token():
    """
    Callback route when the user has accepted to share his data.
    Once the auth has arrived Withings servers come back with
    an authentication code and the state code provided in the
    initial call
    """

    code = request.args.get('code')
    print(code)
    payload = {'action': 'requesttoken',
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CUSTOMER_SECRET,
            'code': code,
            'redirect_uri': CALLBACK_URI
            }

    token = requests.post(f'{WBSAPI_URL}/v2/oauth2', payload).json()
    print(token)
    #Update / add the user to a user / token file
    user_id = token['body']['userid']
    access_token = token["body"]["access_token"]
    refresh_token = token["body"]["refresh_token"]
    current_time = datetime.now()
    user_dict = {'User_id' : [int(user_id)], 'Access_token' :  [access_token], 'Refresh_token' : [refresh_token],"Last_update" : [current_time]}
    single_user_data = pd.DataFrame(user_dict)
    all_user_data = pd.read_csv("userdata.csv")
    all_user_data = df = (pd.concat([all_user_data, single_user_data]).drop_duplicates(["User_id"] , keep='last').sort_values(["User_id"] , ascending=False))
    all_user_data.to_csv('userdata.csv', index = False)



# #  #Offer option to look at devices or go back to start page
    # def device_check_now():
    #     device_check = input("Do you want to check devices? y/n \n")
    #     print(device_check)
    #     if device_check == "y":
    #         headers = {'Authorization': 'Bearer ' + access_token}
    #         payload = {'action': 'getdevice'}
    #         r_getdevice = requests.get(f'https://wbsapi.withings.net/v2/user', headers=headers, params=payload).json()
    #         return r_getdevice
    #     else :
    #         return redirect("/")

    # device_check_now()
    device_check = input("Do you want to check devices? y/n \n")
    if device_check ==  "y":
        headers = {'Authorization': 'Bearer ' + access_token}
        payload = {'action': 'getdevice'}
        r_getdevice = requests.get(f'https://wbsapi.withings.net/v2/user', headers=headers, params=payload).json()
        return r_getdevice
    else:
        return redirect("http://localhost:5000/")


# @app.route("/query")
# def query_data():
    #load user data from
    # loop through data and return
        #create accesstoken for everyone and update user data csv  (only update needed in this case)
        # Read out some data
    