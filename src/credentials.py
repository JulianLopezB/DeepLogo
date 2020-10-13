import os
from google.oauth2 import service_account
from src.paths import *

#PARMAS
credentials = service_account.Credentials.from_service_account_file(path_json)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(path_json)