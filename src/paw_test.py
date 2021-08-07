import requests
from prettyprinter import pprint

BASE_URL = "http://127.0.0.1:5000/"

WITHINGS_URL = "https://account.withings.com/oauth2_user/authorize2"


account_withings_url = "https://account.withings.com"
wbsapi_withings_url = "https://wbsapi.withings.net"
client_id =         "0f985c9465c5295a2b5f3d05ee48c0295f52dbff3d6004b83b317c268cff8eab"
customer_secret =   "a8aac3044dd5afc77fcb97b19fcf7ef20245e9854a3395e7b7a63221b7223efa"
state = "test_state"
callback_uri =  "http://localhost:5000/get_token"




# # Get your Autho Code
# def get_auth
# auth_params = {"response_type":"code",
#                 "client_id":client_id, 
#                 "state":state,
#                 "scope":"user.info",
#                 "redirect_uri":callback_uri,
#                 }


# r = requests.get(f'{WITHINGS_URL}', data=auth_params)

# print(r.text)

auth_code = "f66e68bd575b098dd95da33243099a9b6a00a350"



# Get your access code

ACCESS_TOKEN_BASE_URL = " https://wbsapi.withings.net/v2/oauth2"

access_params = {
    "action":"requesttoken",
    "client_id":client_id,
    "client_secret":customer_secret,
    "grant_type":"authorization_code",
    "code":auth_code,
    "redirect_uri":callback_uri
}

r2 = requests.post(ACCESS_TOKEN_BASE_URL, params=access_params)

t = """https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id=0f985c9465c5295a2b5f3d05ee48c0295f52dbff3d6004b83b317c268cff8eab&state=%3Cstring%3E&scope=user.info&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fget_token&b=authorize2&selecteduser=3088525"""


pprint(r2.text)

# r.json()

# print(r.headers)