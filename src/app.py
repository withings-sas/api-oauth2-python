#!/usr/bin/env python

# from withings_api_example.www import app
from withings_api_example import www

# import urllib
import requests

# code = www.get_code()

# if __name__ == "__main__":
www.app.run(host='0.0.0.0', debug=True, port=5000)
# code = 

# blah =request.get("http://192.168.4.147:5000/")
print("blah")