## Introduction
This repository contains scripts for processing and updating patient and document data in a database. The scripts are designed to automate the process of updating patient information from an Excel file and extracting metadata from PDF and DOCX documents.

## Setup Instructions
### 1. Setting up a Virtual Environment
It's recommended to use a virtual environment to manage dependencies. You can create and activate a virtual environment using the following commands:

```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows
venv\\Scripts\\activate
# For Unix/macOS
source venv/bin/activate
```
### 2. Installing Dependencies

```
pip install -r requirements.txt
```
### 3. Running the Scripts
To run the program, execute the `script.py` script. The script will monitor changes in the specified directory and Excel file, and update the SQLite database accordingly.

```
python script.py
```
## Alternative: Using Docker
Alternatively, you can build and run the program using Docker. A Dockerfile is provided at the root of the project.

### Building the Docker Image
Navigate to the root of the project directory and run the following command to build the Docker image:

```
docker build -t your_image_name .
```
### Running the Docker Container
After building the image, you can run a Docker container using the following command:

```
docker run -it your_image_name
```
## Functionality
The `script.py` script performs the following operations:

1. Connects to the SQLite database `drwh.db`.
2. Monitors the directory `fichiers source` for PDF and DOCX files, as well as the Excel file `export_patient.xlsx`.
3. If new files are added, deleted, or modified in the directory, or if the Excel file is modified, the `update_patient_data` and `update_document_data` functions are called to update the database.
4. Changes are checked every 30 seconds.

## Conclusion
These scripts provide an automated solution for updating patient and document data in a database. Follow the setup instructions to get started with using the scripts in your environment. If you encounter any issues or have any questions, feel free to reach out for assistance. Happy coding!

