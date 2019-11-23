from enum import IntEnum

from gspread import Spreadsheet, Worksheet


class OsbbSheet:
    sheet: Worksheet

    def __init__(self, doc: Spreadsheet, sheet_id: int):
        self.sheet = doc.get_worksheet(sheet_id)

    def get(self, field, row_num):
        return self.sheet.cell(row_num, field.value).value

    def put(self, field, row_num, new_value):
        self.sheet.update_cell(row_num, field.value, new_value)


class RequestsSheet(OsbbSheet):
    def __init__(self, doc: Spreadsheet):
        super().__init__(doc, 1)


class UpdatesSheet(OsbbSheet):
    def __init__(self, doc: Spreadsheet):
        super().__init__(doc, 2)


class FaqSheet(OsbbSheet):
    def __init__(self, doc: Spreadsheet):
        super().__init__(doc, 3)


class Request(IntEnum):
    REQUEST_ID = 1
    DATE = 2
    TIME = 3
    USER_ID = 4
    USER_NAME = 5
    PHONE = 6
    HOUSE_NO = 7
    APARTMENT_NO = 8
    TEXT = 9
    PHOTO_URL = 10
    STATE = 11
    PUBLIC_COMMENTS = 12
    REQUEST_URL = 13
    PRIVATE_COMMENTS = 14;


class AnyFields(IntEnum):
    REQ = 1



    # def get(self, document: Spreadsheet, row_num):
    #     return document.get_worksheet(1).cell(row_num, self.value).value
    #
    # def put(self, document: Spreadsheet, row_num, value):
    #     document.get_worksheet(1).update_cell(row_num, self.value, row_num, value)

# class Requests:
#     sheet: Worksheet
#
#     def __init__(self, spreadsheet):
#         self.sheet = spreadsheet.sheet1
#
#     def __get_field_by_name__(self, name: RequestFields, row_num):
#         return self.sheet.cell(row_num, name.value)
#
#     def request_id(self, row_num):
#         return RequestFields.REQUEST_ID.get(self.sheet, row_num)
#
#     def date(self, row_num):
#         return RequestFields.DATE.get(self.sheet, row_num)
#
#     def time(self, row_num):
#         return RequestFields.TIME.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_name(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)
#
#     def user_id(self, row_num):
#         return RequestFields.USER_ID.get(self.sheet, row_num)