from unicodedata import numeric
from flask import Flask, request, redirect
import pandas as pd
import numpy as np
from datetime import datetime
import requests
from withings_study_features import config

app = Flask(__name__)

CLIENT_ID = config.get('withings_study_features', 'client_id')
CUSTOMER_SECRET = config.get('withings_study_features', 'customer_secret')
STATE = config.get('withings_study_features', 'state')
ACCOUNT_URL = config.get('withings_study_features', 'account_withings_url')
WBSAPI_URL = config.get('withings_study_features', 'wbsapi_withings_url')
CALLBACK_URI = config.get('withings_study_features', 'callback_uri')
AVAILABLE_STUDIES = {'1' : "CIDP", '2' : "Stroke", "3" : "360_PMS", "4" : "Saturate_MS"}

#Start point - selecting study as well as first task. selected_study is a global variable used for paths later
@app.route("/")
def choose_study():
    print("Choose a study environment and enter the corresponding number")
    for k,v in AVAILABLE_STUDIES.items():
        print(k, v, "\n")
    global selected_study
    selected_study = AVAILABLE_STUDIES[input("Study # : ")]
    print("Selected study: ", selected_study)
    return redirect("/start")
    
@app.route("/start")
def decide_at_start():
    print("Choose:\n Sign up of new patient (signup) or data query (query)")
    decision = input("Enter key:\n")
    if decision == "signup":
        return redirect("/signup")
    elif decision == "query":
        return redirect("/query")
    else:
        decide_at_start()

#Route for user signup for specific studies
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
               'redirect_uri': CALLBACK_URI  # URL of this app
               #'mode': 'demo'  # Use demo mode, DELETE THIS FOR REAL APP
               }

    r_auth = requests.get(f'{ACCOUNT_URL}/oauth2_user/authorize2',
                          params=payload)
    print(r_auth)

    return redirect(r_auth.url)

# ROute to then fetch user credentials and store user in database/csv
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
    user_dict = {'Study' : selected_study, 'User_id' : [int(user_id)], 'Access_token' :  [access_token], 'Refresh_token' : [refresh_token],"Last_update" : [current_time]}
    single_user_data = pd.DataFrame(user_dict)
    all_user_data = pd.read_csv(f"studydata/{selected_study}/userdata.csv")
    all_user_data = df = (pd.concat([all_user_data, single_user_data]).drop_duplicates(['Study',"User_id"] , keep='last').sort_values(["User_id"] , ascending=False))
    all_user_data.to_csv(f'studydata/{selected_study}/userdata.csv', index = False)



# #  #Offer option to look at devices or go back to start page
    device_check = input("Do you want to check devices? y/n \n")
    if device_check ==  "y":
        headers = {'Authorization': 'Bearer ' + access_token}
        payload = {'action': 'getdevice'}
        r_getdevice = requests.get(f'https://wbsapi.withings.net/v2/user', headers=headers, params=payload).json()
        return r_getdevice
    else:
        return redirect("http://localhost:5000/start")


#Route to query user data for study
@app.route("/query")
def query_data():
    #load in userdata and iterate over all users to fetch data
    userdata = pd.read_csv(f"studydata/{selected_study}/userdata.csv")
    #userdata = userdata[userdata["Study"] == selected_study] #filter to specific study
    user_devices_all = []
    for index, row in userdata.iterrows():
        user_id = row['User_id']
        refresh_token = row['Refresh_token']
        print(user_id, refresh_token)
        #Renew access-token and save new access token and refresh token to data


        payload = {'action': 'requesttoken',
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'client_secret': CUSTOMER_SECRET,
            'refresh_token': refresh_token,
            'redirect_uri': CALLBACK_URI
            }
        token = requests.post(f'{WBSAPI_URL}/v2/oauth2', payload).json()
        print("Refreshtoken Request:\n",token)
        access_token = token["body"]["access_token"]
        refresh_token = token["body"]["refresh_token"]
        current_time = datetime.now()

        user_dict = {'User_id' : [int(user_id)], 'Access_token' :  [access_token], 'Refresh_token' : [refresh_token],"Last_update" : [current_time]}
        single_user_data = pd.DataFrame(user_dict)
        #print(userdata)
        #print(single_user_data)
        userdata = userdata[['User_id']].merge(single_user_data, 'left').set_index(userdata.index).fillna(userdata)


        ### First data queries - trying to transform answer list of lists and thus gather all users
        def query_registered_devices():
            headers = {'Authorization': 'Bearer ' + access_token}
            payload = {'action': 'getdevice'}
            r_getdevice_raw = requests.get('https://wbsapi.withings.net/v2/user', headers=headers, params=payload)
            r_getdevice = r_getdevice_raw.json()
            data = r_getdevice['body']['devices']
            #Add user id via list comprehension
            data = [dict(item, **{'User_id':user_id}) for item in data]
            user_devices_all.append(data)
            #user_devices["User_Id"] = user_id
        query_registered_devices()
    # flatten list of list and transform to dataframe (faster out out loop)
    user_devices_all = [item for sublist in user_devices_all for item in sublist]
    print(user_devices_all)
    device_df = pd.DataFrame(user_devices_all)
    # Extract that DataFrame into sheet for reference purposes
    device_df.to_excel(f"studydata/{selected_study}/Devices.xlsx")
    userdata.to_csv(f"studydata/{selected_study}/userdata.csv", index = False)
    print("\nTokens were renewed for all users \nDevice list for users has been updated\n")
    input("Press Enter to Proceed to fetch all data\n")



    ####TEST GET WEIGHT
    user_all_weights = []
    for index, row in userdata.iterrows():
        user_id = row['User_id']
        refresh_token = row['Refresh_token']
        access_token = row['Access_token']

        def query_weight():
            headers = {'Authorization': 'Bearer ' + access_token}
            payload = {'action': 'getmeas',
                       'meastype' : '1'}
            r_get_weight_raw = requests.get('https://wbsapi.withings.net/measure', headers=headers, params=payload)
            r_get_weight = r_get_weight_raw.json()
            data = r_get_weight['body']['measuregrps']
            #Add user id via list comprehension
            data = [dict(item, **{'User_id':user_id}) for item in data]
            user_all_weights.append(data)
        query_weight()
    user_all_weights = [item for sublist in user_all_weights for item in sublist]
    [item.update(item['measures'][0]) for item in user_all_weights]
    [item.pop('measures', None) for item in user_all_weights]
    user_all_weights = pd.json_normalize(user_all_weights, sep='_')
    # Transform variables for optimal data sheet
    # user_all_weights['date'] = user_all_weights['date'].dt.strftime('%Y-%m-%d')
    user_all_weights['value_kg'] = user_all_weights["value"] / (10 ** abs(user_all_weights["unit"]))
    def change_timestamp(result_date):
        return datetime.fromtimestamp(int(result_date)).strftime("%Y-%m-%d")
    user_all_weights['date'] = user_all_weights['date'].apply(change_timestamp)
    user_all_weights.to_excel(f"studydata/{selected_study}/all_weights.xlsx")
    print("Weight data saved")


### TEST GET ACTIVITY




### FINISHING UP AND READY FOR NEXT STUDY
    print(f"Query for {selected_study} study finished.")





    #return r_getdevice
    return redirect("http://localhost:5000/")


    # load user data from
    # loop through data and return
    #     create accesstoken for everyone and update user data csv  (only update needed in this case)
    #     Read out some data

