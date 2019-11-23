import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config.config as config

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(config.GDRIVE_CRED, scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
# sheet = client.open("OSBBotSheet").sheet1
sheet = client.open_by_url(config.GDRIVE_URL).sheet1


# Extract and print all of the values
list_of_hashes = sheet.get_all_values()

def get_all():
    return sheet.get_all_values()
