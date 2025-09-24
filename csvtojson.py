import csv
import json
from datetime import datetime, date

# Constants
INPUT_CSV_FILE = "TX_HVAC.csv"
OUTPUT_JSON_FILE = "filtered data.json"
DATE_FORMAT = "%m/%d/%Y"


def get_first_last_full_name(inputName):
    """
    Parses a name string in the format 'LastName, FirstName'
    and returns:
        - FullName (title case)
        - FirstName (title case)
        - LastName (title case)

    Returns (None, None, None) if the input(name).
    """

    if not inputName or ',' not in inputName:
        return None, None, None

    lastName, firstName = [part.strip() for part in inputName.split(',', 1)]
    fullName = f"{firstName} {lastName}".title()

    return fullName, firstName.title(), lastName.title()


def replace_empty_with_null(inputColumnvalue):
    """
    Replaces empty or whitespace with None.

    Parameters:
        value (str or None).

    Returns:
        str or None: (The stripped string if it contains non-whitespace characters; 
                     otherwise, None).
    """

    return inputColumnvalue.strip() if inputColumnvalue and inputColumnvalue.strip() else None


def get_json_from_csv(inputCsvPath, outputJsonPath):
    """
    Reads CSV file of license records, filters and processes the data,
    and writes the result to a JSON file.

    This function performs the following steps:
        - Skips records with missing or invalid LICENSE EXPIRATION DATE.
        - Filters rows whose LICENSE EXPIRATION DATE is greater than today's date.
        - Create license ID by joining LICENSE TYPE and LICENSE NUMBER.
        - Gets full name, first name, and last name from the "NAME" field.
        - Writes the filtered data to a JSON file.

    Parameters:
        inputCsvPath (str): Path to the input CSV file containing raw license data.
        outputJsonPath (str): Path where the processed JSON output should be saved.

    Returns:
        None
    """

    todayDate = datetime.today()
    jsonFileData = []

    with open(inputCsvPath, newline='', encoding='utf-8') as csvfile:
        rowDict = csv.DictReader(csvfile)

        for row in rowDict:
            expirationDateTrimmed = row.get(
                "LICENSE EXPIRATION DATE", ""
            ).strip()

            try:
                expirationDate = datetime.strptime(
                    expirationDateTrimmed,
                    DATE_FORMAT
                )
            except Exception:
                continue

            if expirationDate <= todayDate:
                continue

            licenseType = replace_empty_with_null(row.get("LICENSE TYPE"))
            licenseNumber = replace_empty_with_null(row.get("LICENSE NUMBER"))

            licenseId = f"{licenseType}-{licenseNumber}" if licenseType and licenseNumber else None

            county = replace_empty_with_null(row.get("COUNTY"))
            countyName = None if county and county.upper() == "OUT OF STATE" else county

            fullName, firstName, lastName = get_first_last_full_name(
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
                "Mailing Address Line1": replace_empty_with_null(row.get("MAILING ADDRESS LINE1")),
                "Mailing Address Line2": replace_empty_with_null(row.get("MAILING ADDRESS LINE2")),
                "Mailing Address City, State Zip": replace_empty_with_null(row.get("MAILING ADDRESS CITY, STATE ZIP")),
                "Phone Number": replace_empty_with_null(row.get("PHONE NUMBER")),
            }

            jsonFileData.append(jsonFieldsForJsonFile)

    with open(outputJsonPath, 'w', encoding='utf-8') as jsonfile:
        json.dump(jsonFileData, jsonfile, indent=4)


get_json_from_csv(INPUT_CSV_FILE, OUTPUT_JSON_FILE)
