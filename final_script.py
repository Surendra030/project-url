import os
from pymongo import MongoClient
from mega import Mega
from getfiles import download_file_from_drive
from getaudio import get_audio_streams, extract_audio

# Initialize Mega API client
mega = Mega()

# Dropbox Access Token
token_url ="afg154009@gmail.com_megaMac02335!_token_mongodb+srv://afg154005:gnLhPlgHpuQaFjvh@cluster0.0yvn2uk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
ACCESS_TOKEN = token_url
str_lst = token_url.split("_token_")
keys = str_lst[0].split("_")
email = keys[0]
pass_key = keys[1]

# MongoDB URL
MONGO_URL = str_lst[1]

# Mega Folder Name
MEGA_FOLDER = "getdata101"

# MongoDB Collection
DB_NAME = "links_data"
COLLECTION_NAME = "link_lst"

# Function to login to Mega Cloud
def get_mega_session():
    try:
        session = mega.login(email, pass_key)
        print("Logged in to Mega Cloud.")
        return session
    except Exception as e:
        print(f"Login to Mega failed: {e}")
        raise

# Function to upload a file to Mega Cloud and get a sharable link
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
        print(f"Uploading {local_file_path} to Mega Cloud at {mega_folder_path}")
        file = session.upload(local_file_path, folder_id)
        sharable_link = session.get_link(file)
        print(f"Uploaded file: {local_file_path}. Sharable link: {sharable_link}")
        return sharable_link
    except Exception as e:
        print(f"Failed to upload {local_file_path} to Mega Cloud: {e}")
        return None

# Function to process the drive URL and update MongoDB
def process_snippet(snippet, collection):
    try:
        # Step 1: Download the file from Google Drive
        drive_url = snippet["link"]
        google_drive_base_url = "https://drive.google.com/uc?id={}&export=download"
        download_url = google_drive_base_url.format(drive_url)
                         
        if len(download_url) > 10:
            downloaded_file_name = download_file_from_drive(download_url)
            
            if downloaded_file_name:
                print(f"Downloaded file: {downloaded_file_name}")
                
                # Step 2: Extract audio streams from the file
                audio_streams = get_audio_streams(downloaded_file_name)
                
                # Step 3: Extract and save audio files
                extract_audio(downloaded_file_name, audio_streams)
                
                sharable_links = []
                
                # Step 4: Upload audio files to Mega Cloud
                for audio_file in os.listdir():
                    if audio_file.endswith(".mp3"):  # Process only .mp3 files
                        local_file_path = os.path.join(os.getcwd(), audio_file)
                        sharable_link = upload_to_mega(local_file_path, MEGA_FOLDER)
                        if sharable_link:
                            sharable_links.append(sharable_link)
                
                # Step 5: Update the MongoDB document
                update = {
                    "$set": {
                        "file_need_to_be_downloaded": False,
                        "workflow_accessing_url": False,
                        "files_uploaded_to_db": True,
                        "files_ready_to_download_from_db": True,
                        "url_not_required": False,
                        "sharable_link": sharable_links,
                    }
                }
                collection.update_one({"_id": snippet["_id"]}, update)
                print(f"Updated MongoDB document for ID: {snippet['_id']}")
            else:
                print("Failed to download file.")
    except Exception as e:
        print(f"Error processing snippet with ID {snippet['_id']}: {e}")

# Main Function
def main():
    # Connect to MongoDB
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    # Fetch all snippets that need to be processed
    snippets = collection.find({"file_need_to_be_downloaded": True})
    
    for index,snippet in enumerate(snippets):
        print(f"{index} : Processing snippet with ID: {snippet['_id']}")
        process_snippet(snippet, collection)

if __name__ == "__main__":
    main()
