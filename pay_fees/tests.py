import requests

# url = "https://sandbox.safaricom.co.ke/oauth/v1/generate"
# querystring = {"grant_type": "client_credentials"}
# payload = ""
# headers = {
#     "Authorization": "Basic SWZPREdqdkdYM0FjWkFTcTdSa1RWZ2FTSklNY001RGQ6WUp4ZVcxMTZaV0dGNFIzaA=="
# }
# response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
# print(response.text)

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_year_project.settings')
django.setup()

from pay_fees.models import *

