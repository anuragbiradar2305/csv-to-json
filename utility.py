from datetime import datetime
import os


class CSVUtility:
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

        lastName, firstName = [
            part.strip()
            for part in inputName.split(',', 1)
        ]

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

    @staticmethod
    def check_for_required_columns(csvColumns, requiredColumns):
        """
        Checks if all required columns are present in the CSV data.
        Returns True if all required columns are found, False otherwise.
        """
        missingColumns = [
            col for col in requiredColumns if col not in csvColumns
        ]
        return missingColumns

    @staticmethod
    def get_csv_files_from_folder(folderPath):
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

    @staticmethod
    def parse_date(date_string, date_format):
        """
        Parses a date string using the provided format and returns a datetime object.
        Returns None if the date is invalid.
        """
        try:
            return datetime.strptime(date_string.strip(), date_format)
        except ValueError:
            return None
