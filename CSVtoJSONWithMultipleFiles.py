import csv
import json
from datetime import datetime
import os


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
        self._inputCSVPaths = self.get_csv_files_from_folder(self.CSV_FOLDER)
        self._outputJSONPath = self.OUTPUT_JSON_FILE

    @property
    def outputJSONPath(self):
        """Returns the output JSON file path."""
        return self._outputJSONPath

    @property
    def todaysDate(self):
        """Returns today's date."""
        return datetime.today()

    @staticmethod
    def get_first_last_full_name(inputName):
        """
        Parses a name string in the format 'LastName, FirstName'
        and returns:
            - FullName (title case)
            - FirstName (title case)
            - LastName (title case)

        Returns (None, None, None) if the input(name) is invalid.
        """
        if not inputName or ',' not in inputName:
            return None, None, None

        lastName, firstName = [part.strip()
                               for part in inputName.split(',', 1)]
        fullName = f"{firstName} {lastName}".title()

        return fullName, firstName.title(), lastName.title()

    @staticmethod
    def replace_empty_with_null(inputValue):
        """
        Replaces empty or whitespace with None.

        Parameters:
            value (str or None).

        Returns:
            str or None: (The stripped string if it contains non-whitespace characters; 
                        otherwise, None).
        """
        return inputValue.strip() if inputValue and inputValue.strip() else None

    def get_csv_files_from_folder(self, folderPath):
        """
        Returns a list of all CSV files in the specified folder.
        """
        csvFiles = []
        if os.path.exists(folderPath) and os.path.isdir(folderPath):
            for fileName in os.listdir(folderPath):
                filePath = os.path.join(folderPath, fileName)
                if fileName.lower().endswith('.csv') and os.path.isfile(filePath):
                    csvFiles.append(filePath)

                if not csvFiles:
                    print(f"Warning: No CSV file found in '{folderPath}'.")
        else:
            print(
                f"Warning: The folder {folderPath} does not exist or is not a directory."
            )

        return csvFiles

    def check_for_required_columns(self, csvColumns, CsvFileName):
        """
        Checks if all required columns are present in the CSV data.
        Returns True if all required columns are found, False otherwise.
        """
        missingColumns = [
            col for col in self.REQUIRED_COLUMNS if col not in csvColumns
        ]

        if missingColumns:
            print(
                f"Warning: Missing requiredcolumns {', '.join(missingColumns)} in '{CsvFileName}':"
            )
            return False

        return True

    def get_json_from_csv(self):
        """
        Reads multiple CSV files, filters and processes the data,
        and writes the result to a JSON file.

        This function performs the following steps:
            - Skips records with missing or invalid LICENSE EXPIRATION DATE.
            - Filters rows whose LICENSE EXPIRATION DATE is greater than today's date.
            - Create license ID by joining LICENSE TYPE and LICENSE NUMBER.
            - Gets full name, first name, and last name from the "NAME" field.
            - Writes the filtered data to a JSON file.
        """
        jsonFileData = []

        for csv_file in self._inputCSVPaths:

            with open(csv_file, newline='', encoding='utf-8') as csvFile:
                rowDict = csv.DictReader(csvFile)

                if not self.check_for_required_columns(rowDict.fieldnames, csv_file):
                    continue

                for row in rowDict:

                    expirationDateTrimmed = row.get(
                        "LICENSE EXPIRATION DATE", ""
                    )

                    try:
                        expirationDate = datetime.strptime(
                            expirationDateTrimmed.strip(), self.DATE_FORMAT)
                    except ValueError:
                        continue

                    if expirationDate <= self.todaysDate:
                        continue

                    licenseType = self.replace_empty_with_null(
                        row.get("LICENSE TYPE"))
                    licenseNumber = self.replace_empty_with_null(
                        row.get("LICENSE NUMBER"))

                    licenseId = f"{licenseType}-{licenseNumber}" if licenseType and licenseNumber else None

                    county = self.replace_empty_with_null(row.get("COUNTY"))
                    countyName = None if county and county.upper() == "OUT OF STATE" else county

                    fullName, firstName, lastName = self.get_first_last_full_name(
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
                        "Mailing Address Line1": self.replace_empty_with_null(row.get("MAILING ADDRESS LINE1")),
                        "Mailing Address Line2": self.replace_empty_with_null(row.get("MAILING ADDRESS LINE2")),
                        "Mailing Address City, State Zip": self.replace_empty_with_null(row.get("MAILING ADDRESS CITY, STATE ZIP")),
                        "Phone Number": self.replace_empty_with_null(row.get("PHONE NUMBER")),
                    }

                    jsonFileData.append(jsonFieldsForJsonFile)

        with open(self.outputJSONPath, 'w', encoding='utf-8') as jsonfile:
            json.dump(jsonFileData, jsonfile, indent=4)


if __name__ == "__main__":
    classObj = CSVtoJSONWithMultipleFiles()
    classObj.get_json_from_csv()
