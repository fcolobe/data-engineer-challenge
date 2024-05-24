import logging
import os
from datetime import datetime

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

directory = "fichiers source"
file = "export_patient.xlsx"
path = os.path.join(directory, file)
sheet_name = "Export Worksheet"


def read_and_clean_excel(path, sheet_name):
    """
    Reads an Excel file and removes duplicates based on the specified columns.

    Args:
    - path (str): Path to the Excel file.
    - sheet_name (str): Name of the sheet to read.

    Returns:
    - pd.DataFrame: Cleaned DataFrame without duplicates.
    """
    try:
        export_patient = pd.read_excel(
            path, sheet_name=sheet_name, dtype={"HOSPITAL_PATIENT_ID": str}
        )
        export_patient_cleaned = export_patient.drop_duplicates(
            subset=["NOM", "PRENOM", "DATE_NAISSANCE", "ADRESSE", "TEL"]
        )
        return export_patient_cleaned
    except Exception as e:
        logging.error(f"Error reading the Excel file: {e}")
        return None


def create_patient_dict(index, row, upload_id):
    """
    Creates a dictionary for a patient from a row of the DataFrame.

    Args:
    - index (int): Index of the row.
    - row (pd.Series): Row of the DataFrame.
    - upload_id (int): Upload ID.

    Returns:
    - dict: Dictionary containing patient information.
    """
    patient_num = index + 1
    birth_date = row["DATE_NAISSANCE"]
    death_date = row["DATE_MORT"] if pd.notna(row["DATE_MORT"]) else None

    patient_dict = {
        "PATIENT_NUM": patient_num,
        "LASTNAME": row["NOM"],
        "FIRSTNAME": row["PRENOM"],
        "BIRTH_DATE": birth_date,
        "SEX": row["SEXE"],
        "MAIDEN_NAME": (
            row["NOM_JEUNE_FILLE"] if pd.notna(row["NOM_JEUNE_FILLE"]) else None
        ),
        "RESIDENCE_ADDRESS": row["ADRESSE"],
        "PHONE_NUMBER": row["TEL"],
        "ZIP_CODE": row["CP"],
        "RESIDENCE_CITY": row["VILLE"],
        "DEATH_DATE": death_date,
        "RESIDENCE_COUNTRY": row["PAYS"],
        "RESIDENCE_LATITUDE": None,
        "RESIDENCE_LONGITUDE": None,
        "DEATH_CODE": "1" if death_date else "0",
        "UPDATE_DATE": datetime.now().strftime("%d/%m/%Y"),
        "BIRTH_COUNTRY": None,
        "BIRTH_CITY": None,
        "BIRTH_ZIP_CODE": None,
        "BIRTH_LATITUDE": None,
        "BIRTH_LONGITUDE": None,
        "UPLOAD_ID": upload_id,
    }

    return patient_dict


def create_ipphist_dict(index, row, upload_id):
    """
    Creates a dictionary for an IPPHIST record from a row of the DataFrame.

    Args:
    - index (int): Index of the row.
    - row (pd.Series): Row of the DataFrame.
    - upload_id (int): Upload ID.

    Returns:
    - dict: Dictionary containing IPPHIST information.
    """
    patient_num = index + 1

    ipphist_dict = {
        "PATIENT_NUM": patient_num,
        "HOSPITAL_PATIENT_ID": row["HOSPITAL_PATIENT_ID"],
        "ORIGIN_PATIENT_ID": "SIH",
        "MASTER_PATIENT_ID": "1" if row["HOSPITAL_PATIENT_ID"] else "0",
        "UPLOAD_ID": upload_id,
    }

    return ipphist_dict


def get_patient_data(export_patient, upload_id):
    """
    Extracts patient and IPPHIST record data from the DataFrame.

    Args:
    - export_patient (pd.DataFrame): DataFrame containing patient data.
    - upload_id (int): Upload ID.

    Returns:
    - (list, list): List of dictionaries for patients and IPPHIST records.
    """
    patients_data = [
        create_patient_dict(index, row, upload_id)
        for index, row in export_patient.iterrows()
    ]
    ipphist_data = [
        create_ipphist_dict(index, row, upload_id)
        for index, row in export_patient.iterrows()
    ]
    return patients_data, ipphist_data


def update_existing_data(df, table_name, conn):
    """
    Updates existing records in a database table with data from a DataFrame.

    Args:
    - df (pd.DataFrame): The DataFrame containing the data to update.
    - table_name (str): The name of the target table.
    - conn (sqlite3.Connection): The connection to the database.

    Returns:
    - None
    """
    for _, row in df.iterrows():
        placeholders = ", ".join(
            [f"{col} = ?" for col in row.index if col != "PATIENT_NUM"]
        )
        query = f"UPDATE {table_name} SET {placeholders} WHERE PATIENT_NUM = ?"
        params = tuple(row[col] for col in row.index if col != "PATIENT_NUM") + (
            row["PATIENT_NUM"],
        )
        conn.execute(query, params)
    conn.commit()


def insert_new_data(df, table_name, conn):
    """
    Inserts a DataFrame into a database table.

    Args:
    - df (pd.DataFrame): The DataFrame containing the data to insert.
    - table_name (str): The name of the target table.
    - conn (sqlite3.Connection): The connection to the database.

    Returns:
    - None
    """
    df.to_sql(table_name, con=conn, if_exists="append", index=False)


def update_patient_data(upload_id, conn):
    """
    Updates patient and IPPHIST data in the database.

    Args:
    - upload_id (int): The upload ID to associate with the records.
    - conn (sqlite3.Connection): The connection to the database.

    Returns:
    - None
    """
    try:
        logging.info("Reading data from the Excel file...")
        export_patient = read_and_clean_excel(path, sheet_name)
        if export_patient is None:
            logging.error("The Excel file could not be read properly. Update aborted.")
            return
        logging.info("Data reading successful.")

        patients_data, ipphist_data = get_patient_data(export_patient, upload_id)
        df_patients = pd.DataFrame(patients_data)
        df_ipphist = pd.DataFrame(ipphist_data)

        existing_patients = pd.read_sql_query("SELECT * FROM DWH_PATIENT", conn)
        existing_ipphist = pd.read_sql_query("SELECT * FROM DWH_PATIENT_IPPHIST", conn)

        new_patients = df_patients[
            ~df_patients["PATIENT_NUM"].isin(existing_patients["PATIENT_NUM"])
        ]
        new_ipphist = df_ipphist[
            ~df_ipphist["PATIENT_NUM"].isin(existing_ipphist["PATIENT_NUM"])
        ]

        update_existing_data(df_patients, "DWH_PATIENT", conn)
        update_existing_data(df_ipphist, "DWH_PATIENT_IPPHIST", conn)
        insert_new_data(new_patients, "DWH_PATIENT", conn)
        insert_new_data(new_ipphist, "DWH_PATIENT_IPPHIST", conn)

        logging.info("Update successful.")

    except Exception as e:
        logging.error(f"Error updating DWH_PATIENT and DWH_PATIENT_IPPHIST tables: {e}")
