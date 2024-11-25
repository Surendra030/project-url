import subprocess
import re
import os

def get_audio_streams(video_file):
    """Get audio stream details from the video file."""
    # Run ffmpeg command to get the stream details of the video file
    command = ["ffmpeg", "-i", video_file]
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    
    # Get raw output of ffmpeg command
    ffmpeg_output = result.stderr
    
    # Find all audio streams using regex
    audio_streams = []
    for match in re.finditer(r"Stream #(\d+):(\d+)\((.*?)\): Audio: (\S+), (\d+) Hz, (\S+),", ffmpeg_output):
        stream_index = match.group(2)
        language = match.group(3)
        codec = match.group(4)
        sample_rate = match.group(5)
        channels = match.group(6)
        
        audio_streams.append({
            "index": stream_index,
            "language": language,
            "codec": codec,
            "sample_rate": sample_rate,
            "channels": channels
        })
    print(audio_streams)
    
    return audio_streams

def extract_audio(video_file, audio_streams):
    """Extract audio streams from video file and save them to MP3 files."""
    for stream in audio_streams:
        stream_index = stream["index"]
        language = stream["language"]
        stream_index = int(stream_index) - 1  # Adjust index for ffmpeg
        # Construct the output filename based on language or stream index
        output_filename = f"output_{language.lower()}.mp3" if language else f"output_{stream_index}.mp3"
        # Construct the ffmpeg command to extract audio
        command = [
            "ffmpeg", "-i", video_file, 
            "-map", f"0:a:{stream_index}", 
            "-c:a", "libmp3lame", 
            "-q:a", "2", 
            output_filename
        ]
        
        # Run the command to extract and save the audio
        subprocess.run(command)
        print(f"Extracted {language} audio to {output_filename}")
    
    # Delete the video file permanently after extracting audio
    try:
<<<<<<< HEAD
        os.remove(video_file)
        print(f"Deleted video file: {video_file}")
    except FileNotFoundError:
        print(f"File not found: {video_file}")
=======
        # Open the Google Drive link
        driver.get(url)
        time.sleep(2)  # Give the page a moment to load

        # Extract the file name and size from the page content
        page_source = driver.page_source
        file_name_match = re.search(r'<a href="[^"]*">([^<]+)</a>\s?\(([\d\.]+[MGKB]+)\)', page_source)
        if file_name_match:
            downloaded_file_name = file_name_match.group(1)  # Extract file name
            expected_size_str = file_name_match.group(2)  # Extract file size string
            expected_size = convert_size_to_bytes(expected_size_str)  # Convert to bytes
            print(f"Expected file name: {downloaded_file_name}")
            print(f"Expected file size: {expected_size / (1024 * 1024)} MB")
        else:
            raise Exception("Could not extract file name and size from the page")

        # Find the "Download anyway" button by its ID and click it
        download_button = driver.find_element(By.ID, "uc-download-link")
        download_button.click()
        print("Download started...")

        # Define the file path to check the download progress
        file_path = os.path.join(os.getcwd(), downloaded_file_name)

        # Wait for initial 30 seconds before checking the file size
        time.sleep(70)
        print("Initial 30 seconds completed...")

        # Monitor the download progress
        while True:
            if os.path.exists(file_path):
                current_size = os.path.getsize(file_path)  # Get the current size of the file in bytes
                print(f"Current file size: {current_size / (1024 * 1024)} MB")
                if current_size >= expected_size:  # Check if the downloaded file size meets the expected size
                    print("Download complete!")
                    break
                else:
                    print("Download still in progress, waiting 10 more seconds...")
                    time.sleep(10)  # Wait for 10 more seconds before checking again
            else:
                print("File not found yet, waiting 10 more seconds...")
                time.sleep(10)  # Wait for 10 more seconds before checking again

>>>>>>> b181993ec9c339967e2bf7e720c6bec251d66b9a
    except Exception as e:
        print(f"Error while deleting file: {e}")

