import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config.config as config
from src.sheet_markup import Request, RequestsSheet

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(config.GDRIVE_CRED, scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
# sheet = client.open("OSBBotSheet").sheet1
doc = client.open_by_url(config.GDRIVE_URL)
requests = RequestsSheet(doc)


# Extract and print all of the values
# def test_get_all():
#     return doc.sheet1.get_all_values()


def test_get_request():
    row = 2
    return requests.get(Request.USER_NAME, row) + " (" + requests.get(Request.PHONE, row) + ")"
    # return RequestFields.USER_NAME.get(doc, row) + " (" + RequestFields.PHONE.get(doc, row) + ")"

