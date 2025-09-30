# inbuilt module
import csv
import json
from datetime import datetime
import logging

# custom module
from utility import CSVUtility

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVtoJSONWithMultipleFiles:
    # Constants
    DATE_FORMAT = "%m/%d/%Y"
    CSV_FOLDER = "csv"
    OUTPUT_JSON_FILE = "filtered data.json"
    REQUIRED_COLUMNS = [
        "LICENSE TYPE", "LICENSE NUMBER", "LICENSE EXPIRATION DATE",
        "COUNTY", "NAME", "MAILING ADDRESS LINE1", "MAILING ADDRESS LINE2",
        "MAILING ADDRESS CITY, STATE ZIP", "PHONE NUMBER"
    ]

    def __init__(self):
        self._inputCSVPaths = CSVUtility.get_csv_files_from_folder(
            self.CSV_FOLDER
        )

        self._outputJSONPath = self.OUTPUT_JSON_FILE

    @property
    def outputJSONPath(self):
        """Returns the output JSON file path."""
        return self._outputJSONPath

    @property
    def todaysDate(self):
        """Returns today's date."""
        return datetime.today()

    def check_for_required_columns(self, csvColumns, CsvFileName):
        """
        Checks if all required columns are present in the CSV data.
        Returns True if all required columns are found, False otherwise.
        """
        missingColumns = CSVUtility.check_for_required_columns(
            csvColumns, self.REQUIRED_COLUMNS
        )

        if missingColumns:
            print(
                f"Warning: Missing required columns {', '.join(missingColumns)} in '{CsvFileName}' "
            )
            return False

        return True

    def parse_csv_row(self, row):
        """
        Processes a single row and returns a dictionary for JSON output
        """

        expirationDateTrimmed = row.get("LICENSE EXPIRATION DATE", "")

        expirationDate = CSVUtility.parse_date(
            expirationDateTrimmed,
            self.DATE_FORMAT
        )

        # Skip expired or invalid rows
        if expirationDate is None or expirationDate <= self.todaysDate:
            return None

        # Process other fields using utility functions
        licenseType = CSVUtility.replace_empty_with_null(
            row.get("LICENSE TYPE")
        )

        licenseNumber = CSVUtility.replace_empty_with_null(
            row.get("LICENSE NUMBER")
        )

        licenseId = f"{licenseType}-{licenseNumber}" if licenseType and licenseNumber else None

        county = CSVUtility.replace_empty_with_null(row.get("COUNTY"))
        countyName = None if county and county.upper() == "OUT OF STATE" else county

        fullName, firstName, lastName = CSVUtility.get_first_last_full_name(
            row.get("NAME")
        )

        jsonFieldsForJsonFile = {
            "Id": licenseId,
            "License Type": licenseType,
            "License Number": licenseNumber,
            "License Expiration Date": expirationDateTrimmed,
            "County": countyName,
            "Full Name": fullName,
            "First Name": firstName,
            "Last Name": lastName,
            "Mailing Address Line1": CSVUtility.replace_empty_with_null(row.get("MAILING ADDRESS LINE1")),
            "Mailing Address Line2": CSVUtility.replace_empty_with_null(row.get("MAILING ADDRESS LINE2")),
            "Mailing Address City, State Zip": CSVUtility.replace_empty_with_null(row.get("MAILING ADDRESS CITY, STATE ZIP")),
            "Phone Number": CSVUtility.replace_empty_with_null(row.get("PHONE NUMBER")),
        }

        return jsonFieldsForJsonFile

    def get_json_from_csv(self):
        """
        Reads CSV file(s), processes the data, and writes the result to a JSON file.
        """
        jsonFileData = []

        for csv_file in self._inputCSVPaths:
            logger.info(f"Processing file: {csv_file}")
            with open(csv_file, newline='', encoding='utf-8') as csvFile:
                rowDict = csv.DictReader(csvFile)

                if not self.check_for_required_columns(rowDict.fieldnames, csv_file):
                    continue

                for row in rowDict:
                    processedRow = self.parse_csv_row(row)

                    if processedRow:
                        jsonFileData.append(processedRow)

        # Write the JSON data to the output file
        with open(self.outputJSONPath, 'w', encoding='utf-8') as jsonfile:
            json.dump(jsonFileData, jsonfile, indent=4)
            logger.info(f"JSON data has been written to {self.outputJSONPath}")


if __name__ == "__main__":
    classObj = CSVtoJSONWithMultipleFiles()
    classObj.get_json_from_csv()
