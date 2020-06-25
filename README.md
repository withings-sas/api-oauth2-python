# Quickstart

Here is quick description of the structure of the created project, how to
install it and how to use it.
This project launches a small Flask webserver on which you have the bare bones
to connect to withings' developer API through Oauth 2.0. The full documentation
of the API is [here](https://developer.withings.com/)

You need to use Python V3.

First create a new python virtual environment, activate it and install this as a python package in your shiny venv.
```
virtualenv venv
source venv/bin/activate
pip install -e .
```

Then create a developer account on withings' api [here](https://account.withings.com/partner/add_oauth2)
with the following parameters:
* Environment = dev
* callback url = http://localhost:5000/get_token

You can take the sample image put in the folder as logo and put whatever you want into the other fields.
You do need to have a regular Withings account to have a developer account. Use [account](https://account.withings.com/)
to create one if you don't have one.

You should put in your client_id and client_secret you got from your developer account you just created into the config
after copying the config and editing it:
```
cp project.conf.example project.conf
vim project.conf
```

There are two keys to change: client_id and customer_secret. You can leave state like that or put whatever you like in it.
Leave the other parameters unchanged.

Launch the app on localhost, port 5000. If this port is already taken change it in the config and app.py
```
source venv/bin/activate
./scripts/app.py
```
Go the the URL http://localhost:5000

The following happened:
* You are redirected to account.withings.com for the "demo" user. If you didn't use the demo user, a user would have to log in.
* The demo user accepts the sharing
* The logged user are is redirected to the "redirect_url" on your domain with two parameters: "code" and "state".
* Your app can then use the "code" (which is the Authorization token) to genenerate a acces token
* With this access token you can get the data from the user, or even subscribe to a notification features.
* Here the app list the devices of the demo user (he has none)
* Edit the code and enjoy :)

NB: This project is really bare bones, no error handling when communicating with Withings' webservices has been made: the
app simply crashes when faced with an issue. No tests have been writter either. It is meant for exploration purposes and nor production use.
