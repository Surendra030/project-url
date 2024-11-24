import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
# Set up Chrome options for headless mode and to handle downloads
options = Options()
options.add_argument("--headless")  # Uncomment this line if you want to run headless (without opening a window)
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")
options.add_experimental_option("prefs", {
    "download.default_directory": os.getcwd(),  # Save in the current working directory
    "download.prompt_for_download": False,  # Disable download prompt
    "directory_upgrade": True
})

# Specify the path to your chromedriver
chromedriver_path = r"chromedriver" # Update this path to the actual location of chromedriver

# Use the Service class to specify the chromedriver path
service = Service(executable_path=chromedriver_path)
# Function to convert size string like '302M' or '5G' to bytes
def convert_size_to_bytes(size_str):
    size_str = size_str.strip().upper()
    match = re.match(r'(\d+)([MGKB])', size_str)
    if match:
        size = int(match.group(1))
        unit = match.group(2)
        if unit == 'M':
            return size * 1024 * 1024  # Convert MB to bytes
        elif unit == 'G':
            return size * 1024 * 1024 * 1024  # Convert GB to bytes
        elif unit == 'K':
            return size * 1024  # Convert KB to bytes
    return 0  # Invalid size

# Function to download file from Google Drive
def download_file_from_drive(url):
    # Set the path to chromedriver explicitly
    driver = webdriver.Chrome(service=service, options=options)

    downloaded_file_name = None
    
    try:
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
        time.sleep(40)
        print("Initial 30 seconds completed...")

        # Monitor the download progress
        timeout = time.time() + 240  # 5 minutes timeout
        while True:
            if time.time() > timeout:
                print("Download timeout. Assuming the download is complete.")
                break

            if os.path.exists(file_path):
                current_size = os.path.getsize(file_path)
                print(f"Current file size: {current_size / (1024 * 1024)} MB")
                if current_size >= expected_size:
                    print("Download complete!")
                    break
                elif current_size > 0 and current_size == previous_size:  # No change in size
                    unchanged_iterations += 1
                    if unchanged_iterations > 5:  # After 5 unchanged iterations, assume it's done
                        print("Download seems complete (stalled but size consistent).")
                        break
                else:
                    unchanged_iterations = 0
                previous_size = current_size
            else:
                print("File not found yet, waiting 10 more seconds...")

                time.sleep(10)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

    return downloaded_file_name