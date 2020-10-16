import os
from google.oauth2 import service_account
from src.paths import *

#PARMAS
#credentials = service_account.Credentials.from_service_account_file(path_json)
credentials = service_account.Credentials.from_service_account_file(
    path_json,
    scopes=['https://www.googleapis.com/auth/devstorage.full_control', 
            'https://www.googleapis.com/auth/cloud-platform']
    )

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(path_json)