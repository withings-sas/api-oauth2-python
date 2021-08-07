from flask import Flask, request, redirect
import requests
from withings_api_example import config
import datetime

from sqlalchemy import create_engine
import psycopg2

import json

import datetime
import pandas as pd


def write_df_to_postgres(data_frame, table_name):

    engine = create_engine("postgresql+psycopg2://postgres:mysecretpassword@192.168.4.143/withings")
    postgresSQLConnection = engine.connect()

    try:
        data_frame.to_sql(table_name, postgresSQLConnection, if_exists='append')

    except ValueError as vx:

        print(vx)

    except Exception as ex:  

        print(ex)

    else:
        print("PostgreSQL Table %s has been created successfully."%table_name)

    finally:
        postgresSQLConnection.close()





app = Flask(__name__)

CLIENT_ID = config.get('withings_api_example', 'client_id')
CUSTOMER_SECRET = config.get('withings_api_example', 'customer_secret')
STATE = config.get('withings_api_example', 'state')
ACCOUNT_URL = config.get('withings_api_example', 'account_withings_url')
WBSAPI_URL = config.get('withings_api_example', 'wbsapi_withings_url')
CALLBACK_URI = config.get('withings_api_example', 'callback_uri')


@app.route("/")
def get_code():
    """
    Route to get the permission from an user to take his data.
    This endpoint redirects to a Withings' login page on which
    the user has to identify and accept to share his data
    """
    payload = {'response_type': 'code',  # imposed string by the api
               'client_id': CLIENT_ID,
               'state': STATE,
               'scope': 'user.metrics,user.activity',  # see docs for enhanced scope
               'redirect_uri': CALLBACK_URI,  # URL of this app
            #    'mode': 'demo'  # Use demo mode, DELETE THIS FOR REAL APP
               }

    r_auth = requests.get(f'{ACCOUNT_URL}/oauth2_user/authorize2',
                          params=payload)

    # r_auth.url = https://account.withings.com/oauth2_user/account_login?response_type=code&client_id=0f985c9465c5295a2b5f3d05ee48c0295f52dbff3d6004b83b317c268cff8eab&state=%3Cstring%3E&scope=user.info&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fget_token&b=authorize2
    return  redirect(r_auth.url)



@app.route("/get_token")
def get_token():
    """
    Callback route when the user has accepted to share his data.
    Once the auth has arrived Withings servers come back with
    an authentication code and the state code provided in the
    initial call
    """
    code = request.args.get('code')
    state = request.args.get('state')

    payload = {'grant_type': 'authorization_code',
               'client_id': CLIENT_ID,
               'client_secret': CUSTOMER_SECRET,
               'code': code,
               'redirect_uri': CALLBACK_URI
               }

    r_token = requests.post(f'{ACCOUNT_URL}/oauth2/token',
                            data=payload).json()

    

    access_token = r_token.get('access_token', '')
    
    # r_token = json.loads(r_token)

    

    print(r_token)

    # Add everything to a dict and pass to df
    withings_cred =  payload
    withings_cred['auth_code'] = code
    withings_cred['state'] = state
    withings_cred['access_token'] = access_token
    withings_cred['time_stamp'] = datetime.datetime.now()

    # Pull from response
    withings_cred['userid'] = r_token.get('userid')
    withings_cred['refresh_token'] = r_token.get('refresh_token')
    withings_cred['scope'] = r_token.get('scope')
    

    withings_cred_df = pd.DataFrame(withings_cred, index=[0])

    write_df_to_postgres(withings_cred_df, 'withings_cred')


    # GET Some info with this token
    headers_val = {'Authorization': 'Bearer ' + access_token}
    payload = {'action': 'getdevice'}

    # List devices of returned user
    r_getdevice = requests.get(f'{WBSAPI_URL}/v2/user',
                               headers=headers_val,
                               params=payload).json()




# curl --header "Authorization: Bearer YOUR_ACCESS_TOKEN" --data "action=getmeas&meastype=meastype&meastypes=meastypes&category=category&startdate=startdate&enddate=enddate&offset=offset&lastupdate=int" 'https://wbsapi.withings.net/measure'
    measure_payload = {
        "action":"getmeas"
        # "meastypes":[1,76],
        # "category":1,
    }

    r_getmeasure = requests.get(f'{WBSAPI_URL}/measure',
                               headers=headers_val,
                               params=measure_payload).json()
    

    #ACCOUNT_URL = https://account.withings.com

    return r_getmeasure # r_getdevice



























# auth_code = ""

# @app.route("/get_measure")
# def get_measure(auth_code):
#     """
#     Callback route when the user has accepted to share his data.
#     Once the auth has arrived Withings servers come back with
#     an authentication code and the state code provided in the
#     initial call
#     """
#     code = request.args.get('code')
#     state = request.args.get('state')

#     payload = {'grant_type': 'authorization_code',
#                'client_id': CLIENT_ID,
#                'client_secret': CUSTOMER_SECRET,
#                'code': auth_code,
#                'redirect_uri': CALLBACK_URI
#                }

#     r_token = requests.post(f'{ACCOUNT_URL}/oauth2/token',
#                             data=payload).json()

#     access_token = r_token.get('access_token', '')

#     # GET Some info with this token
#     headers = {'Authorization': 'Bearer ' + access_token}
#     payload = {'action': 'getdevice'}

#     # List devices of returned user
#     r_getdevice = requests.get(f'{WBSAPI_URL}/v2/user',
#                                headers=headers,
#                                params=payload).json()

#     return r_getdevice
