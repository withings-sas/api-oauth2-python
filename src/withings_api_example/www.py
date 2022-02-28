from flask import Flask, request, redirect
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
def get_code():
    """
    Route to get the permission from an user to take his data.
    This endpoint redirects to a Withings' login page on which
    the user has to identify and accept to share his data
    """
    payload = {'response_type': 'code',  # imposed string by the api
               'client_id': CLIENT_ID,
               'state': STATE,
               'scope': 'user.info',  # see docs for enhanced scope
               'redirect_uri': CALLBACK_URI,  # URL of this app
               'mode': 'demo'  # Use demo mode, DELETE THIS FOR REAL APP
               }

    r_auth = requests\
        .get(
        'https://account.withings.com/oauth2_user/authorize2',
        params=payload
    )

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

    payload = {
               "action": "requesttoken",
               'grant_type': 'authorization_code',
               'client_id': CLIENT_ID,
               'client_secret': CUSTOMER_SECRET,
               'code': code,
               'redirect_uri': CALLBACK_URI
               }

    r_token = requests.post(
        'https://wbsapi.withings.net/v2/oauth2',
        data=payload
    ) \
        .json()

    access_token = r_token.get('body', '').get('access_token', "")

    # GET Some info with this token
    headers = {'Authorization': 'Bearer ' + access_token}
    payload = {'action': 'getdevice'}

    # List devices of returned user
    r_getdevice = requests.get(
        f'https://wbsapi.withings.net/v2/user',
        headers=headers,
        params=payload
    ).json()

    return r_getdevice
