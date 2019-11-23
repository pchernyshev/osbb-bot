from src.db.base import AbstractDatabaseBridge


class SpreadsheetBridge(AbstractDatabaseBridge):
    TYPE_QUALIFIER = "google-spreadsheet"

    # TODO: integrate with spreadsheets

