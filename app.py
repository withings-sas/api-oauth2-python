#!/usr/bin/env python3

# import sys, os
# sys.path.append(r'C:\Users\larsm\OneDrive\Dokumente\Research Basics and Coding Projects\Data Projects\Marc Pawlitzki\CIDP\WithingsWebApp\api-oauth2-python\src')

from withings_study_features.main_app import app


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=5000)
    print("moin")
