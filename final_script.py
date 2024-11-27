
import os
from getfiles import download_file_from_drive
from getaudio import get_audio_streams, extract_audio
from pymongo import MongoClient
from mega import Mega
from datetime import datetime, timedelta

# Get the current time (start time)
start_time = datetime.now()
target_time = start_time + timedelta(hours=5, minutes=40)


# Dropbox Access Token
token_url =os.getenv("M_TOKEN")

str_lst = token_url.split("_token_")
keys = str_lst[0].split("_")
email = keys[0]
pass_key = keys[1]

# MongoDB URL
MONGO_URL = str_lst[1]
client = MongoClient(MONGO_URL)
db = client["links_data"]
collection = db["link_lst"]
mega = Mega()


# Function to upload file to Dropbox

# Function to login to Mega Cloud
def get_mega_session():
    try:
        session = mega.login(email, pass_key)
        print("Logged in to Mega Cloud.")
        return session
    except Exception as e:
        print(f"Login to Mega failed: {e}")
        raise

def upload_to_mega(local_file_path, mega_folder_path):
    session = get_mega_session()
    try:
        # Check if the folder exists or create it
        all_nodes = session.get_files()
        folder_id = None
        for node_id, details in all_nodes.items():
            if details['t'] == 1 and details['a']['n'] == mega_folder_path:
                folder_id = node_id
                break

        if not folder_id:
            print(f"Folder '{mega_folder_path}' not found. Creating it.")
            folder_id = session.create_folder(mega_folder_path)["f"]["h"]

        # Upload the file
        print(f"Uploading {local_file_path}, {(os.path.getsize(local_file_path)) / (1024 * 1024)} to Mega Cloud at {mega_folder_path}")
        file = session.upload(local_file_path)
        sharable_link = session.get_link(file,folder_id)
        print(f"Uploaded file: {local_file_path}. Sharable link: {sharable_link}")
        return sharable_link
    except Exception as e:
        print(f"Failed to upload {local_file_path} to Mega Cloud: {e}")
        return None



def main(drive_url,snippet):
    # Step 1: Download the file from Google Drive
    downloaded_file_name = download_file_from_drive(drive_url)
    print(f"Downloaded file: {downloaded_file_name}")
    if downloaded_file_name:
            # Step 2: Extract audio streams from the downloaded file
            audio_streams = get_audio_streams(downloaded_file_name)
            
            # Step 3: Extract and save audio files
            extract_audio(snippet["link"], downloaded_file_name, audio_streams)
            print(os.listdir())

            # Step 4: Upload audio files to Dropbox
            for audio_file in os.listdir():
                if audio_file.endswith('.mp3'):  # Upload only the .mp3 files
                    local_file_path = os.path.join(os.getcwd(), audio_file).replace("\\", "/").split("/")[-1]
                    dropbox_file_path = "files_folder"
                    upload_to_mega(local_file_path, dropbox_file_path)
            
            # Step 5: Update MongoDB exit_flag to True after processing
            print(f"Processing completed for {downloaded_file_name}")
            
            # ** Delete .mkv and .mp3 files after every 10 indexes **
            
    else:   
        print("File download failed.")



if __name__ =="__main__":
    snippets = collection.find({"file_need_to_be_downloaded": True})

    for index,snippet in enumerate(snippets):
        if index >=25:
            current_time = datetime.now()
            if current_time >=target_time :
                print("target time completed..")
                exit
            print("index : ",index,snippet["_id"])
            drive_url = snippet["link"]
            if len(drive_url)>10:
                google_drive_base_url = f"https://drive.google.com/uc?id={drive_url}&export=download"
                main(google_drive_base_url,snippet)
        if index >=30:
            exit
        if index % 10 == 0:  # Delete every 10th index
                print("Deleting .mkv and .mp3 files...")
                for file in os.listdir():
                    if file.endswith('.mkv') or file.endswith('.mp3'):
                        try:
                            os.remove(file)
                            print(f"Deleted {file}")
                        except Exception as e:
                            print(f"Error deleting {file}: {e}")
            