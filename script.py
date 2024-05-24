import logging
import os
import sqlite3
import time

from exo_1 import update_patient_data
from exo_2 import update_document_data

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

directory = "fichiers source"
excel_file = "export_patient.xlsx"
excel_path = os.path.join(directory, excel_file)


def get_current_files_with_timestamps(directory):
    """
    Returns a dictionary of the current files with their timestamps in the specified directory.

    Args:
    - directory (str): The path to the directory.

    Returns:
    - dict: A dictionary where the keys are filenames and the values are their last modified timestamps.
    """
    return {
        filename: os.path.getmtime(os.path.join(directory, filename))
        for filename in os.listdir(directory)
        if filename.endswith((".pdf", ".docx"))
    }


def has_changes(directory, last_seen_files):
    """
    Checks for new files, deleted files, or modified files in the directory.

    Args:
    - directory (str): The path to the directory.
    - last_seen_files (dict): A dictionary of previously seen files with their timestamps.

    Returns:
    - tuple: A tuple containing sets of new files, deleted files, modified files, and the current files with their timestamps.
    """
    current_files = get_current_files_with_timestamps(directory)
    new_files = set(current_files.keys()) - set(last_seen_files.keys())
    deleted_files = set(last_seen_files.keys()) - set(current_files.keys())

    modified_files = {
        filename
        for filename in current_files
        if filename in last_seen_files
        and current_files[filename] != last_seen_files[filename]
    }

    return new_files, deleted_files, modified_files, current_files


def main():
    upload_id_patient = 1
    upload_id_document = 1
    last_seen_files = get_current_files_with_timestamps(directory)

    try:
        excel_last_modified_time = os.path.getmtime(excel_path)

        while True:
            logging.info("Checking for file changes...")

            new_files, deleted_files, modified_files, last_seen_files = has_changes(
                directory, last_seen_files
            )
            excel_current_modified_time = os.path.getmtime(excel_path)

            if (
                excel_current_modified_time != excel_last_modified_time
                or upload_id_patient == 1
            ):
                if upload_id_patient == 1:
                    logging.info(
                        "Initializing tables DWH_PATIENT and DWH_PATIENT_IPPHIST..."
                    )
                else:
                    logging.info(
                        "The Excel file has been modified, updating in progress..."
                    )

                update_patient_data(upload_id_patient, conn)
                excel_last_modified_time = excel_current_modified_time
                upload_id_patient += 1

                logging.info(
                    "Updating of tables DWH_PATIENT and DWH_PATIENT_IPPHIST completed."
                )

            if new_files or deleted_files or modified_files or upload_id_document == 1:
                if upload_id_document == 1:
                    logging.info("Initializing the DWH_DOCUMENT table...")

                if new_files:
                    logging.info(f"New files detected: {new_files}")

                if deleted_files:
                    logging.info(f"Deleted files detected: {deleted_files}")

                if modified_files:
                    logging.info(f"Modified files detected: {modified_files}")

                update_document_data(directory, upload_id_document, conn)
                upload_id_document += 1
                logging.info("Update of the DWH_DOCUMENT table completed.")

            else:
                logging.info("No changes found.")

            time.sleep(30)

    except Exception as e:
        logging.error(f"Error in the main loop: {e}")


if __name__ == "__main__":
    try:
        conn = sqlite3.connect("drwh.db")
        main()
    except sqlite3.Error as e:
        logging.error(f"Error connecting to the database: {e}")
    finally:
        if conn:
            conn.close()
