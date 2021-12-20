import io
import pickle
import os
import shutil
import logging
from mimetypes import MimeTypes
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from properties import (
    SHITPOST_DESTINATION,
    SCOPES,
    SOURCE_FOLDER_ID,
    USED_FOLDER_ID,
    LOG
)

# logging
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(filename=LOG, level=logging.DEBUG, format=FORMAT)


def get_gdrive_service():
    """Initializes the Google Drive authorization"""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automlibatically when the authorization flow completes for the first
    # time.
    if os.path.exists('../lib/token.pickle'):
        with open('../lib/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '../lib/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('../lib/token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # return Google Drive API service
    return build('drive', 'v3', credentials=creds)


gdrive_service = get_gdrive_service()


def file_download(file_id, file_name):
    """Downloads a file by its id from Google Drive"""
    file_name = SHITPOST_DESTINATION + file_name
    request = gdrive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()

    # Initialise a downloader object to download the file
    downloader = MediaIoBaseDownload(fh, request, chunksize=204800)
    done = False
    # Download the data in chunks
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)

    # Write the received data to the file
    with open(file_name, 'wb') as f:
        shutil.copyfileobj(fh, f)

    logging.info("File " + file_name + " downloaded")
    # Return True if file Downloaded successfully
    return True


def file_upload(filepath):
    """Uploads a file from a local filepath"""
    # Extract the file name out of the file path
    name = filepath.split('/')[-1]

    # Find the MimeType of the file
    mimetype = MimeTypes().guess_type(name)[0]

    # create file metadata
    file_metadata = {'name': name}
    media = MediaFileUpload(filepath, mimetype=mimetype)

    # Create a new file in the Drive storage
    file = gdrive_service.files().create(
        body=file_metadata, media_body=media, fields='id').execute()

    logging.info("File " + name + " downloaded")


def file_move(file_id, file_name):
    """Moves a file by its id in Google Drive to used"""

    # Retrieve the existing parents to remove
    file = gdrive_service.files().get(fileId=file_id, fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))

    # Move the file to the new folder
    file = gdrive_service.files().update(
        fileId=file_id,
        addParents=USED_FOLDER_ID,
        removeParents=previous_parents,
        fields='id, parents'
    ).execute()
    logging.info("File " + file_name + " moved")


def download_and_move_one_file():
    """Downloads and deletes the first File from the Google Drive shitpost folder"""
    results = gdrive_service.files().list(q="'" + SOURCE_FOLDER_ID + "' in parents", pageSize=10,
                                          fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    i_d = items[0].get('id')
    name = items[0].get('name')
    file_download(i_d, name)
    file_move(i_d, name)
    return name
