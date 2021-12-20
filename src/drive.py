import io
import pickle
import os
import shutil
from mimetypes import MimeTypes

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']


def get_gdrive_service():
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

    print("File Downloaded")
    # Return True if file Downloaded successfully
    return True


def file_upload(filepath):
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

    print("File Uploaded.")


def list_files():
    destination = '/home/simonski/Data/PycharmProjects/impfbot-shitpost/src'
    results = gdrive_service.files().list(fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    id = items[0].get('id')
    name = items[0].get('name')
    file_download(id, name)


list_files()
