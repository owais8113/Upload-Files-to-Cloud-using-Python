import sys
import dropbox
import tkinter as tk
from tkinter import filedialog
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
import requests
API_TOKEN = '______________________'
REMOTE_FOLDER_ID = '___________'  # Replace with the ID of the remote folder you want to upload to

# Access token
TOKEN = '______________________________________________'

# LOCALFILE = r"C:\Users\Owais Ahmed\Downloads\Science Club.docx"
# FILE_PATH = r"C:\Users\Owais Ahmed\Downloads\Cloud Computing (Week 3 Lecture Notes).pdf"  # Replace with the path of the file you want to upload
LOCALFILE = filedialog.askopenfilename(title="Select a file to upload")
BACKUPPATH = "/" + LOCALFILE.split("/")[-1]

# Create a Tkinter window
root = tk.Tk()
root.withdraw()

if not LOCALFILE:
    sys.exit("No file selected. Exiting...")
def upload_to_pcloud(file_path, remote_folder_id, api_token):
    url = 'https://api.pcloud.com/uploadfile'
    
    headers = {
        'Authorization': f'Bearer {api_token}',
    }
    
    params = {
        'path': f'/folderid:{remote_folder_id}/',
    }
    
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file)}
        response = requests.post(url, headers=headers, params=params, files=files)
        
        if response.status_code == 200:
            print('File uploaded successfully')
        else:
            print(f'Upload failed. Response: {response.text}')

# if __name__ == '__main__':
    # upload_to_pcloud(LOCALFILE, REMOTE_FOLDER_ID, API_TOKEN)
# Uploads contents of LOCALFILE to Dropbox
def backup():
    with open(LOCALFILE, 'rb') as f:
        print("Uploading " + LOCALFILE + " to Dropbox as " + BACKUPPATH + "...")
        try:
            dbx.files_upload(f.read(), BACKUPPATH, mode=WriteMode('overwrite'))
        except ApiError as err:
            if (err.error.is_path() and
                    err.error.get_path().error.is_insufficient_space()):
                sys.exit("ERROR: Cannot back up; insufficient space.")
            elif err.user_message_text:
                print(err.user_message_text)
                sys.exit()
            else:
                print(err)
                sys.exit()

def checkFileDetails():
    print("Checking file details")
    try:
        for entry in dbx.files_list_folder('').entries:
            print(entry.name)
    except dropbox.exceptions.AuthError as err:
        print(f"Authentication error: {err}")
    except dropbox.exceptions.ApiError as err:
        print(f"API error: {err}")

def categorizeAndMoveFile(file_path, category_folder):
    dest_path = f"/{category_folder}/{BACKUPPATH.split('/')[-1]}"
    try:
        dbx.files_move(file_path, dest_path)
        print(f"File moved to {dest_path}")
    except ApiError as err:
        print(f"Error moving file: {err}")

if __name__ == '__main__':
    if (len(TOKEN) == 0):
        sys.exit("ERROR: Access token is missing.")

    print("Creating a Dropbox object...")
    dbx = dropbox.Dropbox(TOKEN)

    try:
        dbx.users_get_current_account()
    except AuthError as err:
        sys.exit("ERROR: Invalid access token.")

    try:
        checkFileDetails()
    except dropbox.exceptions.Error as err:
        sys.exit("Error while checking file details")

    print("Creating backup...")
    backup()

    # Categorize and move the file based on its type
    file_extension = BACKUPPATH.split(".")[-1].lower()
    
    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
        categorizeAndMoveFile(BACKUPPATH, "Images")
    elif file_extension in ['doc', 'docx', 'txt', 'pdf']:
        categorizeAndMoveFile(BACKUPPATH, "Document")
    elif file_extension in ['mp4', 'mov', 'avi', 'mkv']:
        categorizeAndMoveFile(BACKUPPATH, "Videos")
    elif file_extension in ['mp3', 'wav', 'flac']:
        categorizeAndMoveFile(BACKUPPATH, "Audio")
    else:
        print("File type not recognized. No categorization performed.")

    print("Done!")
